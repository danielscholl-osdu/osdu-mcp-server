"""
OSDU Record Lifecycle Workflow Prompt.

Provides comprehensive guidance for executing the complete OSDU record lifecycle
workflow from legal compliance setup through record creation, validation,
discovery, and cleanup.
"""

from typing import List, Dict, Any

# Define Message type for development/testing
Message = Dict[str, Any]


async def guide_record_lifecycle() -> List[Message]:
    """
    Provide comprehensive guidance for executing the complete OSDU record
    lifecycle workflow with validation at each step.

    This workflow demonstrates end-to-end integration across all major OSDU
    services and serves as both educational content and a practical testing
    methodology.

    Returns:
        List[Message]: Single user message containing the complete workflow guide
    """
    content = """# OSDU Record Lifecycle Workflow Guide

## Complete Record Lifecycle Workflow

### Process Flow
**Legal Setup** → **Schema Validation** → **Record Creation** → **Record Verification** → **Search Validation** → **Cleanup**

### Time Estimate: 10-15 minutes
### Prerequisites: Write and delete permissions enabled, valid OSDU environment

## 🔧 Available MCP Resources

**Before starting the workflow**, access these template resources to avoid format errors:

### Template Resources
- **legal-tag-template.json** - Working legal tag structure with validation notes
- **processing-parameter-record.json** - Complete record template for ProcessingParameterType

### Reference Resources
- **acl-format-examples.json** - ACL format examples for different OSDU environments
- **search-query-patterns.json** - Proven search patterns for record validation

💡 **Usage**: Use `ReadMcpResourceTool` to access these templates before starting each phase. These resources contain working examples that eliminate format guessing errors.

---

## Prerequisites & Environment Setup

### Required Permissions
For this workflow to execute successfully, you must enable both write and delete operations:

```json
"env": {
  "OSDU_MCP_ENABLE_WRITE_MODE": "true",     // Required for record and legal tag creation
  "OSDU_MCP_ENABLE_DELETE_MODE": "true"     // Required for cleanup operations
}
```

### Environment Validation
Before starting the workflow, verify all OSDU services are accessible:

**MCP Tool**: `health_check`
```
health_check(include_services=true, include_auth=true)
```

**Success Criteria**: All services (legal, schema, storage, search) return "healthy" status

### Required Information
Prepare these values for your workflow:
- **Target Schema Kind**: e.g., `osdu:wks:reference-data--ProcessingParameterType:1.0.0`
- **Legal Tag Name**: Must be unique, e.g., `public-usa-test-lifecycle-[timestamp]`
- **Record Data**: Sample data payload matching your schema requirements

### 🌐 Data Domain Configuration (Critical for ACL Format)

**ACL format varies by OSDU deployment.** Determine your data domain before starting:

**Method 1: Environment Variable (Recommended)**
```json
"env": {
  "OSDU_MCP_SERVER_DOMAIN": "contoso.com"
}
```

**Data Domain Examples:**
- Standard OSDU: `contoso.com`
- Microsoft OSDU: `dataservices.energy`
- Microsoft Internal: `msft-osdu-test.org`

**Method 2: Check Your Groups**
```
entitlements_mine()
```
Look at group formats to determine your data domain (e.g., `data.default.viewers@opendes.DOMAIN`)

**📋 Resource**: Read `acl-format-examples.json` for comprehensive domain detection guidance
```
ReadMcpResourceTool(server="osdu-mcp-server", uri="file://acl-format-examples.json")
```

---

## Step-by-Step Workflow Guide

### Phase 1: Legal Compliance Setup

#### Step 1: Create Legal Tag

**Purpose**: Establish legal compliance framework for the record

**📋 Template Resource**: First, read `legal-tag-template.json` for working legal tag structure
```
ReadMcpResourceTool(server="osdu-mcp-server", uri="file://legal-tag-template.json")
```

**MCP Tool**: `legaltag_create`

**Example**:
```
legaltag_create(
  name="public-usa-test-lifecycle-20241219",
  description="Test legal tag for record lifecycle workflow",
  country_of_origin=["US"],
  contract_id="TEST-CONTRACT-001",
  security_classification="Public",
  personal_data="No Personal Data",
  export_classification="EAR99",
  data_type="Public Domain Data",
  expiration_date="2025-12-31"
)
```

**Validation**: Verify tag creation success
**MCP Tool**: `legaltag_get`
```
legaltag_get(name="public-usa-test-lifecycle-20241219")
```

**Success Criteria**:
- Legal tag created with proper compliance properties
- Tag accessible and contains all required metadata
- Status shows as valid

---

### Phase 2: Schema Validation

#### Step 2: Retrieve Target Schema

**Purpose**: Understand record structure and validation requirements

**MCP Tool**: `schema_get`

**Example**:
```
schema_get(id="osdu:wks:reference-data--ProcessingParameterType:1.0.0")
```

**Validation Points**:
- Schema exists and is accessible
- Required properties are identified in schema.properties
- Schema version is compatible (status: "PUBLISHED")
- Note required fields for record creation

**Key Information to Extract**:
- Required vs optional properties
- Data types and validation rules
- Any specific format requirements

---

### Phase 3: Record Creation & Verification

#### Step 3: Create Storage Record

**Purpose**: Create properly structured record with compliance metadata

**📋 Template Resources**: Read these templates first to avoid format errors:
```
# Get ACL format for your environment
ReadMcpResourceTool(server="osdu-mcp-server", uri="file://acl-format-examples.json")

# Get complete record template
ReadMcpResourceTool(server="osdu-mcp-server", uri="file://processing-parameter-record.json")
```

**MCP Tool**: `storage_create_update_records`

**Example**:
```
storage_create_update_records(
  records=[{
    "kind": "osdu:wks:reference-data--ProcessingParameterType:1.0.0",
    "acl": {
      "viewers": ["data.default.viewers@{partition}.{domain}"],
      "owners": ["data.default.owners@{partition}.{domain}"]
    },
    "legal": {
      "legaltags": ["{partition}-public-usa-test-lifecycle-20241219"],
      "otherRelevantDataCountries": ["US"],
      "status": "compliant"
    },
    "data": {
      "Name": "QA Test Case - Record Lifecycle",
      "ID": "qatest-lifecycle-20241219",
      "Code": "QA-LIFECYCLE",
      "Source": "osdu-mcp-server-workflow-test"
    }
  }]
)
```

**Important**: Replace placeholders with your values:
- `{partition}` → your data partition ID (e.g., `opendes`)
- `{domain}` → your OSDU data domain (e.g., `contoso.com`)

**Success Criteria**:
- Record creation returns success status
- Record ID is generated and returned
- Version number is assigned (typically 1 for new records)

#### Step 4: Verify Record Creation

**Validation Steps**:

1. **Get Latest Record Version**
   **MCP Tool**: `storage_get_record`
   ```
   storage_get_record(id="[record-id-from-step-3]")
   ```

2. **Check Record Versions**
   **MCP Tool**: `storage_list_record_versions`
   ```
   storage_list_record_versions(id="[record-id-from-step-3]")
   ```

3. **Get Specific Version** (optional)
   **MCP Tool**: `storage_get_record_version`
   ```
   storage_get_record_version(id="[record-id-from-step-3]", version=1)
   ```

**Validation Points**:
- Record structure matches schema requirements
- ACL and legal metadata are properly set
- Data payload is correctly stored
- Version information is accurate

---

### Phase 4: Search Validation

#### Step 5: Verify Record Indexing

**Purpose**: Confirm record is properly indexed and discoverable

**📋 Reference Resource**: Get proven search patterns to avoid query syntax errors:
```
ReadMcpResourceTool(server="osdu-mcp-server", uri="file://search-query-patterns.json")
```

**Wait Period**: Allow 30-60 seconds for search indexing to complete

**MCP Tool**: `search_query`

**Example**:
```
search_query(
  query="data.ID:(\"qatest-lifecycle-20241219\")",
  kind="osdu:wks:reference-data--ProcessingParameterType:1.0.0",
  limit=10
)
```

**Alternative Search by ID**:
**MCP Tool**: `search_by_id`
```
search_by_id(id="[record-id-from-step-3]")
```

**Validation Points**:
- Record appears in search results
- Search metadata matches record data
- Record data is properly indexed and searchable
- Total count > 0 indicates successful indexing

**Common Issue**: If record doesn't appear immediately, wait additional 30 seconds and retry. Search indexing can have delays.

---

### Phase 5: Cleanup & Verification

#### Step 6: Complete Cleanup

**Purpose**: Remove test resources and verify proper cleanup

**Cleanup Sequence**:

1. **Delete Storage Record**
   **MCP Tool**: `storage_delete_record`
   ```
   storage_delete_record(id="[record-id-from-step-3]")
   ```

2. **Delete Legal Tag**
   **MCP Tool**: `legaltag_delete`
   ```
   legaltag_delete(
     name="public-usa-test-lifecycle-20241219",
     confirm=true
   )
   ```

**Verification Steps**:

1. **Verify Record Deletion**
   **MCP Tool**: `storage_get_record`
   ```
   storage_get_record(id="[record-id-from-step-3]")
   ```
   **Expected**: Should return error indicating record not found or is deleted

2. **Verify Legal Tag Deletion**
   **MCP Tool**: `legaltag_get`
   ```
   legaltag_get(name="public-usa-test-lifecycle-20241219")
   ```
   **Expected**: Should return error indicating legal tag not found

**Success Criteria**: Both resources return "not found" errors, confirming complete cleanup

---

## Validation Checkpoints

### After Each Step
- [ ] **Legal Tag**: Created successfully with all required properties
- [ ] **Schema**: Retrieved and requirements understood
- [ ] **Record**: Created with proper structure and compliance metadata
- [ ] **Versions**: Record versioning working correctly
- [ ] **Search**: Record indexed and discoverable
- [ ] **Cleanup**: All test resources properly removed

### Error Indicators
- Permission denied errors → Check write/delete mode settings
- Schema validation failures → Review record structure against schema
- Record creation failures → Verify ACL format and legal tag references
- Search indexing delays → Normal, wait 30-60 seconds and retry
- Cleanup incomplete → Check delete permissions and confirmation parameters

---

## Common Issues & Solutions

### Permission Errors
**Issue**: "Write operations are disabled" or "Delete operations are disabled"
**Solution**:
- Verify `OSDU_MCP_ENABLE_WRITE_MODE=true` for creation operations
- Verify `OSDU_MCP_ENABLE_DELETE_MODE=true` for cleanup operations
- Restart MCP server after environment variable changes

### Schema Validation Errors
**Issue**: Record creation fails with schema validation errors
**Solution**:
- Compare your record data structure against schema requirements
- Ensure all required fields are present
- Check data types match schema specifications
- Verify enum values are valid if applicable

### Legal Tag Reference Errors
**Issue**: Record creation fails with legal tag not found
**Solution**:
- Ensure legal tag name includes partition prefix: `{partition}-{tag-name}`
- Verify legal tag was created successfully before record creation
- Check legal tag is in valid status

### Search Indexing Delays
**Issue**: Record not immediately discoverable via search
**Solution**:
- Search indexing typically takes 30-60 seconds
- Retry search after waiting
- This is normal OSDU behavior, not an error

### ACL Format Errors
**Issue**: Record creation fails with ACL validation errors
**Solution**:
- Use proper email format for viewers/owners groups
- Include partition name in group email addresses
- Format: `data.default.viewers@{partition}.dataservices.energy`

### Cleanup Failures
**Issue**: Resources not properly removed during cleanup
**Solution**:
- Ensure `OSDU_MCP_ENABLE_DELETE_MODE=true`
- Use `confirm=true` parameter for destructive operations
- Check resource still exists before attempting deletion

---

## Advanced Workflow Patterns

### Multi-Record Creation
For testing bulk operations:
```
storage_create_update_records(
  records=[
    {record1_definition},
    {record2_definition},
    {record3_definition}
  ]
)
```

### Schema Evolution Testing
Test different schema versions:
1. Create record with schema v1.0.0
2. Retrieve schema v1.1.0 if available
3. Update record to new schema version
4. Validate backward compatibility

### Performance Validation
Measure workflow timing:
- Track time for each phase
- Identify bottlenecks
- Optimize based on results

### Error Recovery Testing
Test partial failure scenarios:
- Create legal tag, fail record creation
- Create record, fail search validation
- Practice recovery procedures

---

## OSDU Best Practices Demonstrated

### Compliance Best Practices
- **Legal Tags**: Always create with complete compliance metadata
- **Required Fields**: Include all mandatory properties (countryOfOrigin, contractId, etc.)
- **Expiration Dates**: Set appropriate expiration dates for test data
- **Data Classification**: Use appropriate security classifications

### Data Management Best Practices
- **ACL Configuration**: Use proper group-based access control
- **Versioning**: Understand and validate record versioning
- **Metadata**: Include comprehensive metadata for discoverability
- **Cleanup**: Always clean up test resources

### Service Integration Best Practices
- **Dependency Order**: Legal tags before records, records before search
- **Error Handling**: Validate each step before proceeding
- **Timeout Handling**: Account for search indexing delays
- **Resource Management**: Track and clean up all created resources

### Testing Best Practices
- **Unique Identifiers**: Use timestamps or UUIDs for test data
- **Validation Points**: Verify success at each step
- **Complete Cleanup**: Remove all test resources
- **Repeatable Process**: Design for multiple executions

---

## Workflow Summary

This workflow demonstrates the complete OSDU record lifecycle:

1. **Legal Compliance** → Establishing data governance framework
2. **Schema Validation** → Understanding data structure requirements
3. **Record Creation** → Creating properly compliant data records
4. **Verification** → Validating successful storage and versioning
5. **Discovery** → Confirming search indexing and discoverability
6. **Cleanup** → Responsible resource management

The workflow serves multiple purposes:
- **Learning Tool**: Understand OSDU service integration
- **Testing Framework**: Validate environment functionality
- **Best Practices Guide**: Demonstrate proper OSDU usage
- **Quality Assurance**: Comprehensive validation methodology

By following this workflow, you'll gain practical experience with all major OSDU operations while ensuring proper compliance and data management practices.

---

## Next Steps

After mastering this basic workflow, consider exploring:
- **Advanced Search Patterns**: Complex queries and aggregations
- **Batch Operations**: Handling multiple records efficiently
- **Schema Management**: Creating and updating custom schemas
- **Cross-Service Workflows**: Complex multi-service integrations
- **Production Patterns**: Scaling and optimizing for production use

Use the `guide_search_patterns` prompt for advanced search techniques, and `list_mcp_assets` for a complete overview of all available OSDU MCP Server capabilities."""

    return [{"role": "user", "content": content}]
