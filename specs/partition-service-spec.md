# Specification for OSDU MCP Server (Phase 2: Partition Service)

> First service implementation demonstrating the pattern for all future OSDU service integrations.

## Overview

This specification establishes the pattern for integrating OSDU services into the MCP Server, using the Partition Service as the first implementation. The patterns defined here will serve as the template for all subsequent service integrations.

## Architectural Pattern for Service Integration

### Service Integration Components

Each OSDU service integration requires:

1. **Service Client** - Specialized client extending the base OSDU client
2. **MCP Tools** - AI-optimized tools exposing service operations
3. **Service URL Configuration** - Service endpoint management
4. **Test Coverage** - Behavior-driven tests for reliability

### Central URL Management (ADR-009)

Update the service URL enum to include Partition Service:

```python
# shared/service_urls.py
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    PARTITION = "partition"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.PARTITION: "/api/partition/v1",
}
```

### Project Structure Pattern

```
osdu_mcp_server/
├── src/
│   └── osdu_mcp_server/
│       ├── shared/
│       │   └── clients/          # Service-specific clients
│       └── tools/
│           └── {service}/        # Service-specific tools
├── tests/
│   └── tools/
│       └── {service}/           # Service-specific tests
```

## Partition Service Requirements

### Service Context

The Partition Service manages data partition configurations in OSDU. Partitions are logical data isolation boundaries essential for sharding data.

API calls for other services typically include the `data-partition-id` header and will use the default value from configuration unless directly specified.

### Tool Requirements

#### List Partitions Tool

**Purpose**: Enable AI assistants to discover available data partitions

**Requirements**:
- List all accessible partitions
- Optional detailed view including partition properties
- Return count and identifiers


**Key Behaviors**:
- Must handle empty partition lists
- Should support partial data retrieval for performance
- Error gracefully when permissions insufficient or 403 errors received
- Pagination is not neccesary

#### Get Partition Tool

**Purpose**: Retrieve configuration for a specific partition

**Requirements**:
- Fetch partition properties by ID
- Each property is a key-value pair with a `sensitive` metadata flag indicating if the value is a secret or a reference to a secret
- The `data-partition-id` header is set to the default partition unless a specific partition is requested, in which case the provided value is used.

**Key Behaviors**:
- Properties may include a `sensitive` flag. This flag indicates the property is a secret (e.g., credential, connection string), but the value is still returned in the response and is not masked or redacted by default. The flag is informational, not a masking instruction.
- By default, all properties (including sensitive) are returned as provided by the Partition Service.
- Return clear indication when partition doesn't exist

#### Optional Write Operations (Protected by Configuration)

**Purpose**: Manage partition lifecycle in controlled environments

**Tools** (only available when `OSDU_MCP_ENABLE_WRITE_MODE=true`):
- Create Partition Tool
- Update Partition Tool  
- Delete Partition Tool

**Key Behaviors**:
- Disabled by default for safety
- Return clear error when attempted without permission
- Include warning in tool descriptions about risks
- Require explicit confirmation for destructive operations

### Security Requirements

1. **Sensitive Data Protection**
   - Properties marked as sensitive must be filtered by default
   - No credential or secret values exposed without explicit request
   - Audit logging for sensitive data access

2. **Write Operation Protection**
   - Read-only operations by default
   - Write operations (CREATE, UPDATE, DELETE) disabled unless explicitly enabled
   - Environment variable `OSDU_MCP_ENABLE_WRITE_MODE=true` required for write operations
   - Clear warning messages when write operations are attempted without permission
   - Tools designed for safe exploration by default

### API Compatibility

Based on OSDU Partition Service v1:
- Base URL: `/api/partition/v1`
- Standard OSDU authentication
- Consistent error response format

### API Contract Details

#### List Partitions
```http
GET /api/partition/v1/partitions
Authorization: Bearer {token}
Accept: application/json

Response 200 (default, typical):
[
  "osdu",
  "tenant-a", 
  "tenant-b"
]

```

#### Get Partition
```http
GET /api/partition/v1/partitions/{partitionId}
Authorization: Bearer {token}
Accept: application/json
data-partition-id: {partitionId}

Response 200:
{
  "compliance-ruleset": {
    "sensitive": false,
    "value": "shared"
  },
  "storage-account-key": {
    "sensitive": true,
    "value": "secret-key"
  }
}

Response 404:
"{partitionId} partition not found"

> Note: The Partition Service returns plain text error messages (not JSON) for 404 and other errors. Clients/tools should handle both plain text and JSON error responses gracefully.
```

#### Required Headers
- `Authorization`: Bearer token (all endpoints)
- `data-partition-id`: Target partition (partition-specific operations)
- `Accept`: application/json

## Implementation Guidelines

### Service Client Pattern

- Extend base OSDU client for consistency
- Implement service-specific methods
- Handle service-specific errors appropriately
- Maintain stateless operations
- Reuse shared authentication per ADR-012 (supports Azure/AWS/GCP)
- Leverage connection pooling from base client per ADR-005

### Authentication Support (ADR-012)

The Partition Client inherits multi-provider authentication:
- Azure: DefaultAzureCredential (current implementation)
- AWS: IAM roles (future)
- GCP: Service accounts (future)

No partition-specific authentication required.

### Concurrency Guidelines (ADR-005)

Leverage base client's connection management:
- Connection pool: 100 total, 30 per host
- Exponential backoff: 2^attempt seconds
- Timeout: 30 seconds default
- Session reuse for multiple requests

### Tool Implementation Pattern

- Follow ADR-007 pure function pattern
- Use established error handling decorators  
- Optimize responses for AI consumption
- Include helpful metadata in responses
- All tools must be async functions per ADR-008

### Error Contract Mapping (ADR-004)

Map OSDU Partition Service errors to standard MCP errors:

| OSDU Status | MCP Error Type | Tool Response |
|-------------|----------------|---------------|
| 404 | OSMCPAPIError | `{"exists": false, "error": "Partition not found"}` |
| 403 | OSMCPAuthError | `{"error": "Insufficient permissions"}` |
| 401 | OSMCPAuthError | `{"error": "Authentication required"}` |
| 500 | OSMCPAPIError | `{"error": "Service unavailable"}` |
| 400 | OSMCPValidationError | `{"error": "Invalid partition ID"}` |

### Response Design Principles

1. **AI-Optimized Structure**
   - Clear success/failure indicators
   - Structured data over raw API responses
   - Contextual information included

2. **Security by Default**
   - Sensitive data redacted automatically
   - Explicit flags required for full data
   - Permission context in responses

3. **Error Transparency**
   - Clear error categorization
   - Actionable error messages
   - Sufficient context for troubleshooting

### Observability and Audit Requirements

1. **Structured Logging**
   - JSON-formatted logs with standard fields
   - Trace ID propagation for request correlation
   - Log levels: DEBUG, INFO, WARN, ERROR

2. **Metrics Collection**
   - Tool invocation count by name
   - Response time percentiles (p50, p90, p99)
   - Error rates by error type
   - Sensitive data access attempts

3. **Audit Trail**
   - Log all write operation attempts (success/failure)
   - Record sensitive property access
   - Include user context and timestamp
   - Maintain compliance with data retention policies

Example log entry:
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "trace_id": "abc-123",
  "level": "INFO",
  "tool": "get_partition",
  "action": "sensitive_data_access",
  "partition_id": "osdu",
  "properties_accessed": ["storage-account-key"],
  "user": "ai-assistant-1",
  "result": "redacted"
}
```

## Testing Requirements

### Test Categories

1. **Unit Tests**
   - Individual component validation
   - Mock external dependencies
   - Fast execution (<100ms)

2. **Integration Tests**  
   - Service interaction validation
   - Error scenario coverage
   - Performance benchmarks
   - Test with stubbed Partition service
   
3. **Contract Tests**
   - MCP protocol compliance
   - Tool interface validation
   - Response format verification
   - Validate tool discovery

### Test Focus Areas

- Sensitive data filtering
- Error handling scenarios  
- Permission boundaries
- Performance under load
- Pagination behavior
- Write operation blocking

## Scalability Considerations

### Pattern Reusability

This specification establishes patterns for:
- Service client architecture
- Tool organization structure
- Security handling approach
- Testing methodology

### Future Service Integration

When adding new services:
1. Follow the established client pattern
2. Organize tools in service-specific folders
3. Apply consistent security filtering
4. Maintain test coverage standards

## Performance Requirements

- Tool response time: <3 seconds (95th percentile)
- Batch operations should optimize API calls
- Consider caching for frequently accessed data
- Implement appropriate timeouts

## Configuration

### Base Configuration
Leverages existing Phase 1 configuration:
- Service URLs managed centrally
- Authentication handled by foundation
- Standard error handling patterns
- Default data partition can be set via environment variable:

```bash
# Environment variable to set the default data partition (used for all service calls unless overridden)
OSDU_MCP_DEFAULT_DATA_PARTITION=osdu
```

- All service calls include the `data-partition-id` header, using this default unless a specific partition is provided in the request.

#### Write Operation Control
```bash
# Environment variable to enable write operations (defaults to false)
OSDU_MCP_ENABLE_WRITE_MODE=false
```

- Default or not specified: `false` (read-only mode)
- Set to `true` only in controlled environments
- Affects: Create, Update, Delete operations
- When disabled: Tools return error with clear explanation

## Validation Criteria

Partition Service implementation is complete when:

- [ ] Service URL added to central management (ADR-009)
- [ ] Service client extends base OSDU client  
- [ ] List and get tools meet requirements
- [ ] API contract matches documented examples
- [ ] Security filtering working correctly
- [ ] Write operations protected by environment variable
- [ ] Clear error messages when write operations blocked  
- [ ] Error mapping follows ADR-004 patterns
- [ ] Observability logging implemented
- [ ] Connection pooling configured per ADR-005
- [ ] Unit test coverage >80%
- [ ] Contract tests for MCP protocol  
- [ ] Documentation reflects patterns

## Future Considerations

### Potential Enhancements
- Property validation utilities
- Cross-partition comparison tools
- Change detection capabilities
- Audit trail access

### Pattern Evolution
- Monitor pattern effectiveness
- Gather feedback from implementations
- Refine patterns based on learnings
- Document pattern updates

## References

- [Architecture Decision Records](../docs/adr.md)
- [Foundation Specification](foundation-spec.md)
- [Partition Service API Documentation](../ai-docs/partition.yaml)
- [Partition Service API Usage Sample](../ai-docs/partition.http)