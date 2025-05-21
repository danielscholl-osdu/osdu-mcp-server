# Specification for OSDU MCP Server (Phase 2: Entitlements Service)

> Second service implementation managing authorization through groups and members in OSDU.

## Overview

This specification defines the Entitlements Service integration into the MCP Server, following patterns established by the Partition Service. The Entitlements Service manages authorization in OSDU through a group-based access control system where users and applications are members of groups that grant specific permissions.

## Service Context

The Entitlements Service controls access to OSDU resources through:
- **Groups**: Named collections that grant permissions (e.g., `users.datalake.viewers`)
- **Members**: Users or service principals that belong to groups
- **Roles**: Position within a group (MEMBER or OWNER)
- **Group Types**: Categories of groups (DATA, SERVICE, USER, NONE)

### Member Identification

Members can be identified using different formats depending on the identity provider:
- **Email format**: `user@company.com` (common for users in most providers)
- **OID format**: `12345678-1234-1234-1234-123456789012` (Azure AD users and service principals)
- **Service Principal**: Typically uses OID format in Azure, may vary by provider

The tools must handle both formats transparently.

### Common Group Patterns

Standard OSDU group naming follows this pattern:
- `users@{partition}.{domain}` - Base user group
- `users.datalake.viewers@{partition}.{domain}` - Read-only access
- `users.datalake.editors@{partition}.{domain}` - Read/write access
- `users.datalake.admins@{partition}.{domain}` - Administrative access
- `users.datalake.ops@{partition}.{domain}` - Operations access (can delete)

## Tool Requirements

### Design Principles

1. **Simplicity First**: Focus on common authorization tasks
2. **Safety by Default**: Only member management for existing groups
3. **AI-Optimized**: Clear, structured responses for LLM consumption
4. **Abstraction**: Shield AI from complex group naming conventions
5. **Format Agnostic**: Handle various member ID formats transparently

### Read Operations (Always Available)

#### List Groups Tool

**Purpose**: Discover available groups in a partition

**Requirements**:
- List all accessible groups
- Optional filtering by group type (DATA, SERVICE, USER, NONE)
- Return simplified group identifiers
- Include group metadata (type, description)

**Key Behaviors**:
- Abstract full email format from AI when possible
- Handle permission errors gracefully
- Support both simple and detailed views

#### Get Group Members Tool

**Purpose**: View members of a specific group

**Requirements**:
- List all members in a group
- Optional role filtering (MEMBER, OWNER)
- Include member type information
- Show member roles

**Key Behaviors**:
- Accept simplified group names (auto-expand to full email)
- Return member identities as provided by the API (email or OID)
- Include role and type information
- Handle mixed member ID formats in same group

#### Get Member Groups Tool

**Purpose**: Discover what groups a member belongs to

**Requirements**:
- List all groups for a specific member
- Support different member ID formats (email or OID)
- Show member's role in each group
- Optional filtering by group type

**Key Behaviors**:
- Accept any valid member identifier format
- Auto-detect member type from ID format
- Return simplified group names
- Include role details

### Write Operations (Protected by Configuration)

All write operations require `OSDU_MCP_ENTITLEMENTS_ALLOW_WRITE=true`

#### Add Member to Group Tool

**Purpose**: Grant access by adding members to groups

**Requirements**:
- Add member with specified role
- Support any member ID format (email or OID)
- Validate member format
- Default to MEMBER role

**Key Behaviors**:
- Accept both email and OID formats for member_id parameter
- Simplify group specification for common patterns
- Return confirmation with actual member ID used
- Handle existing membership gracefully

#### Remove Member from Group Tool

**Purpose**: Revoke access by removing members from groups

**Requirements**:
- Remove member from specified group
- Support any member ID format
- Confirm removal

**Key Behaviors**:
- Accept both email and OID formats for member_id parameter
- Return clear success/failure indication
- Handle non-existent membership gracefully
- Include final membership status

## API Contract Details

### List Groups
```http
GET /api/entitlements/v2/groups
Authorization: Bearer {token}
data-partition-id: {partition}
Accept: application/json

Response 200:
{
  "groups": [
    {
      "name": "users",
      "email": "users@opendes.dataservices.energy",
      "description": "Default user group"
    },
    {
      "name": "users.datalake.viewers", 
      "email": "users.datalake.viewers@opendes.dataservices.energy",
      "description": "Read access to data lake"
    }
  ]
}
```

### Get Group Members
```http
GET /api/entitlements/v2/groups/{group_email}/members
Authorization: Bearer {token}
data-partition-id: {partition}
Accept: application/json

Response 200:
{
  "members": [
    {
      "email": "user@company.com",
      "role": "MEMBER",
      "memberType": "USER"
    },
    {
      "email": "12345678-1234-1234-1234-123456789012",
      "role": "OWNER", 
      "memberType": "SERVICE"
    }
  ]
}

Note: "email" field contains the member identifier, which may be an actual email or an OID
```

### Get Member Groups
```http
GET /api/entitlements/v2/members/{member_id}/groups?type=NONE
Authorization: Bearer {token}
data-partition-id: {partition}
Accept: application/json

Response 200:
{
  "groups": [
    {
      "name": "users",
      "email": "users@opendes.dataservices.energy"
    },
    {
      "name": "users.datalake.viewers",
      "email": "users.datalake.viewers@opendes.dataservices.energy"
    }
  ]
}

Note: {member_id} can be either email format or OID format
```

### Add Member to Group
```http
POST /api/entitlements/v2/groups/{group_email}/members
Authorization: Bearer {token}
data-partition-id: {partition}
Content-Type: application/json

{
  "email": "user@company.com",  // Can be email or OID
  "role": "MEMBER"
}

Response 200:
{
  "email": "user@company.com",
  "role": "MEMBER"
}
```

### Remove Member from Group
```http
DELETE /api/entitlements/v2/groups/{group_email}/members/{member_id}
Authorization: Bearer {token}
data-partition-id: {partition}

Response 204: No Content

Note: {member_id} can be either email format or OID format
```

## Implementation Guidelines

### Service URL Management

Update the service URL enum:

```python
# shared/service_urls.py
class OSMCPService(Enum):
    """OSDU service identifiers."""
    # ... existing services ...
    ENTITLEMENTS = "entitlements"

SERVICE_BASE_URLS = {
    # ... existing mappings ...
    OSMCPService.ENTITLEMENTS: "/api/entitlements/v2",
}
```

### Group Name Simplification

Implement helper functions to handle group naming:

```python
def expand_group_name(simple_name: str, partition: str, domain: str = "dataservices.energy") -> str:
    """Convert simple group name to full email format."""
    if "@" in simple_name:
        return simple_name  # Already full format
    return f"{simple_name}@{partition}.{domain}"

def simplify_group_name(email: str) -> str:
    """Extract simple name from group email."""
    return email.split("@")[0] if "@" in email else email
```

### Member ID Handling

Implement helper to detect member ID format:

```python
def detect_member_type(member_id: str) -> str:
    """Detect if member ID is email or OID format."""
    # Basic UUID v4 pattern
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    if re.match(uuid_pattern, member_id.lower()):
        return "OID"
    elif "@" in member_id:
        return "EMAIL"
    else:
        return "UNKNOWN"
```

### Error Mapping

Map Entitlements Service errors to MCP errors:

| OSDU Status | Scenario | MCP Error Type |
|-------------|----------|----------------|
| 403 | Insufficient permissions | OSMCPAuthError |
| 404 | Group/member not found | OSMCPAPIError |
| 409 | Member already exists | OSMCPAPIError |
| 400 | Invalid request format | OSMCPValidationError |

### Security Patterns

1. **Write Protection**
   - Environment variable: `OSDU_MCP_ENABLE_WRITE_MODE`
   - Default: `false` (read-only)
   - Clear error messages when disabled

2. **Sensitive Operations**
   - All write operations logged
   - Member changes tracked with full ID
   - No group lifecycle management (create/delete)

3. **Permission Handling**
   - Graceful handling of permission errors
   - Clear feedback on access limitations
   - No exposure of system internals

## Response Design

### AI-Optimized Structures

```json
// List Groups Response
{
  "success": true,
  "count": 15,
  "groups": [
    {
      "name": "users.datalake.viewers",
      "type": "DATA",
      "description": "Read-only data access",
      "member_count": 45
    }
  ],
  "partition": "opendes"
}

// Get Group Members Response (mixed formats)
{
  "success": true,
  "group": "users.datalake.editors",
  "members": [
    {
      "id": "user@company.com",
      "type": "USER",
      "role": "MEMBER",
      "format": "EMAIL"
    },
    {
      "id": "12345678-1234-1234-1234-123456789012",
      "type": "SERVICE",
      "role": "OWNER",
      "format": "OID"
    }
  ],
  "count": 2
}

// Member Operations Response
{
  "success": true,
  "action": "added",
  "member": {
    "id": "12345678-1234-1234-1234-123456789012",
    "format": "OID"
  },
  "group": "users.datalake.editors",
  "role": "MEMBER",
  "message": "Successfully added member to editors group"
}
```

### Error Response Pattern

```json
{
  "success": false,
  "error": "Write operations disabled",
  "details": "Set OSDU_MCP_ENABLE_WRITE_MODE=true to enable",
  "operation": "add_member"
}
```

## Testing Requirements

### Test Scenarios

1. **Member ID Formats**
   - Email format members
   - OID format members
   - Mixed formats in same group
   - Invalid ID formats

2. **Group Operations**
   - Empty groups
   - Type filtering
   - Permission errors
   - Large result sets

3. **Member Management**
   - Add/remove with different ID formats
   - Duplicate members
   - Invalid formats
   - Role changes

4. **Security Tests**
   - Write protection
   - Permission boundaries
   - Audit logging
   - Error messages

### Mock Data Requirements

Create realistic test data reflecting OSDU patterns:
- Mix of email and OID member formats
- Standard group types (viewers, editors, admins, ops)
- Service principals with OIDs
- Various permission scenarios

## Configuration

### Environment Variables

```bash
# Write operation control (default: false)
OSDU_MCP_ENTITLEMENTS_ALLOW_WRITE=false

# Default domain for group emails (default: dataservices.energy)
OSDU_MCP_ENTITLEMENTS_DOMAIN=dataservices.energy

# Enable detailed audit logging (default: true)
OSDU_MCP_ENTITLEMENTS_AUDIT_LOG=true
```

## Observability

### Audit Requirements

All write operations must log:
- Operation type
- Target group
- Member affected (full ID)
- Member ID format
- User context
- Timestamp
- Success/failure

Example audit log:
```json
{
  "timestamp": "2025-01-20T14:30:00Z",
  "operation": "add_member",
  "group": "users.datalake.editors@opendes.dataservices.energy",
  "member": {
    "id": "12345678-1234-1234-1234-123456789012",
    "format": "OID",
    "type": "SERVICE"
  },
  "role": "MEMBER",
  "user": "ai-assistant-1",
  "result": "success",
  "trace_id": "xyz-789"
}
```

## Performance Considerations

1. **ID Format Detection**
   - Cache format detection results
   - Optimize regex patterns
   - Minimize validation overhead

2. **Batch Operations**
   - Consider bulk member operations
   - Optimize API calls for large groups
   - Cache frequently accessed data

## Common Use Cases

### Grant Data Access (Email User)
```python
# Add user with email to viewers group
1. member_id = "user@company.com"
2. group = "users.datalake.viewers"
3. add_member(member_id, group, role="MEMBER")
```

### Grant Service Access (OID)
```python
# Add service principal to admin group
1. member_id = "12345678-1234-1234-1234-123456789012"
2. group = "users.datalake.admins"
3. add_member(member_id, group, role="MEMBER")
```

### Audit Mixed Access
```python
# Review group with mixed member types
1. group = "users.datalake.editors"
2. members = get_group_members(group)
3. Sort by member type and format
4. Report access summary
```

## Tool Summary

Final tool set for Entitlements Service:

1. **Read Operations** (always available):
   - `list_groups` - Discover available groups
   - `get_group_members` - View members of a group
   - `get_member_groups` - See groups a member belongs to

2. **Write Operations** (require OSDU_MCP_ENTITLEMENTS_ALLOW_WRITE=true):
   - `add_member` - Add member to existing group
   - `remove_member` - Remove member from group

All tools support both email and OID member formats transparently.

## Validation Criteria

Entitlements Service implementation is complete when:

- [ ] Service URL added to central management
- [ ] Service client implements required endpoints
- [ ] All read tools functional
- [ ] Write operations properly protected
- [ ] Email and OID formats handled correctly
- [ ] Group name simplification working
- [ ] Error mapping comprehensive
- [ ] Audit logging includes format details
- [ ] Tests cover both ID formats
- [ ] Documentation updated
- [ ] Performance benchmarks met

## Future Enhancements

### Potential Features
- Batch member operations
- ID format conversion utilities
- Access pattern analysis
- Cross-provider ID mapping
- Compliance reporting

### Pattern Evolution
- Monitor ID format usage
- Optimize format detection
- Enhance error messages
- Support additional providers

## References

- [Architecture Decision Records](../docs/adr.md)
- [Foundation Specification](foundation-spec.md)
- [Partition Service Specification](partition-service-spec.md)
- [Entitlements API Documentation](../ai-docs/entitlements.yaml)
- [Entitlements Usage Examples](../ai-docs/entitlements.http)