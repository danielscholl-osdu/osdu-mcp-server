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

### Interactive Process Flow
**Legal Tag Discovery** → **Schema Discovery** → **Record Creation** → **Asset Dashboard** → **Search Validation** → **Interactive Cleanup**

### Time Estimate: 10-15 minutes
### Prerequisites: Write and delete permissions enabled, valid OSDU environment
### Workflow Type: **Interactive** - Adapts based on your environment and choices

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

### Phase 1: Interactive Legal Tag Discovery & Selection

#### Step 1: Discover Available Legal Tags

**Purpose**: Find existing suitable legal tags or create new one with intelligent guidance

**🔍 Discovery Process**:

1. **List All Available Legal Tags**
   **MCP Tool**: `legaltag_list`
   ```
   legaltag_list(valid_only=true)
   ```

2. **Analyze Available Options**
   Based on the results, create a recommendation table:

   ```
   ## 🏷️ Available Legal Tags Analysis

   ┌─────────────────────────────┬──────────────┬──────────────┬─────────────────┬──────────────┐
   │ Legal Tag Name              │ Security     │ Data Type    │ Expires         │ Recommended  │
   ├─────────────────────────────┼──────────────┼──────────────┼─────────────────┼──────────────┤
   │ opendes-public-usa-general  │ Public       │ Public Domain│ 2025-06-30      │ ✅ EXCELLENT │
   │ opendes-private-test-data   │ Private      │ Test Data    │ 2024-12-31      │ ⚠️  EXPIRING │
   │ opendes-confidential-prod   │ Confidential │ Production   │ 2026-01-01      │ ❌ AVOID     │
   └─────────────────────────────┴──────────────┴──────────────┴─────────────────┴──────────────┘

   💡 **RECOMMENDATION**: Use `opendes-public-usa-general` for this test workflow

   **Reasoning**:
   - ✅ Public classification suitable for test data
   - ✅ Long expiration date (6+ months remaining)
   - ✅ General purpose, perfect for testing
   - ✅ Already exists (no creation needed)
   ```

3. **Decision Point**
   ```
   📋 **Choose Your Legal Tag Strategy**:

   Option A: Use recommended tag: `opendes-public-usa-general`
   Option B: Use different existing tag: `[specify-name]`
   Option C: Create new legal tag for this workflow

   ⚡ **Quick Action**: If using Option A, skip to Step 2 (Schema Discovery)
   ```

4. **If Creating New Legal Tag** (Option C selected)

   **📋 Template Resource**: Read `legal-tag-template.json` for working structure
   ```
   ReadMcpResourceTool(server="osdu-mcp-server", uri="file://legal-tag-template.json")
   ```

   **MCP Tool**: `legaltag_create`
   ```
   legaltag_create(
     name="public-usa-test-lifecycle-20241219",
     description="Test legal tag for record lifecycle workflow",
     country_of_origin=["US"],
     contract_id="TEST-CONTRACT-001",
     originator="OSDU-MCP-Server",
     security_classification="Public",
     personal_data="No Personal Data",
     export_classification="EAR99",
     data_type="Public Domain Data",
     expiration_date="2025-12-31"
   )
   ```

5. **Validate Selected/Created Legal Tag**
   **MCP Tool**: `legaltag_get`
   ```
   legaltag_get(name="[your-chosen-legal-tag]")
   ```

**Success Criteria**:
- Legal tag exists and is accessible
- Tag status shows as valid
- Expiration date is in the future
- Security classification appropriate for test data

---

### Phase 2: Interactive Schema Discovery & Selection

#### Step 2: Discover Available Schemas

**Purpose**: Find suitable schema for your data type with intelligent recommendations

**🔍 Discovery Process**:

1. **Discover Published Schemas**
   **MCP Tool**: `schema_search`
   ```
   schema_search(
     filter={"scope": "SHARED", "status": "PUBLISHED"},
     latest_version=true,
     sort_by="entityType",
     limit=20
   )
   ```

2. **Present Common Options with Analysis**

   ```
   ## 📋 Recommended Schemas for Testing

   ┌────────────────────────────────────────────┬─────────────┬──────────────┬──────────────────┐
   │ Schema Type                                │ Version     │ Complexity   │ Best For         │
   ├────────────────────────────────────────────┼─────────────┼──────────────┼──────────────────┤
   │ 🧪 reference-data--ProcessingParameterType│ 1.0.0       │ ⭐ Simple    │ ✅ Testing       │
   │ 📊 work-product-component--WellLog        │ 1.2.0       │ ⭐⭐⭐ Complex│ Advanced flows   │
   │ 📁 work-product--SeismicAcquisitionSurvey │ 2.1.0       │ ⭐⭐⭐⭐ Very │ Production data  │
   │ 🏗️ reference-data--GeologicalFeature     │ 1.1.0       │ ⭐⭐ Medium  │ Geological data  │
   └────────────────────────────────────────────┴─────────────┴──────────────┴──────────────────┘

   💡 **RECOMMENDATION**: Use `reference-data--ProcessingParameterType:1.0.0`

   **Reasoning**:
   - ✅ Simple structure, perfect for learning workflows
   - ✅ Minimal required fields (Name, ID)
   - ✅ Stable schema (Published status)
   - ✅ Well-documented and extensively tested
   - ✅ Fast validation and indexing
   ```

3. **Retrieve Detailed Schema Information**
   **MCP Tool**: `schema_get`
   ```
   schema_get(id="osdu:wks:reference-data--ProcessingParameterType:1.0.0")
   ```

4. **Present Schema Requirements Summary**

   ```
   ## 📋 Schema Requirements Summary

   **Required Fields**:
   - `Name` (string) - Display name for the parameter
   - `ID` (string) - Unique identifier within your namespace

   **Optional Fields**:
   - `Code` (string) - Short reference code
   - `Source` (string) - Origin system identifier
   - `Description` (string) - Detailed description

   **Validation Rules**:
   - Name: 1-255 characters, no special restrictions
   - ID: Must be unique, recommend using timestamp or UUID
   - All string fields accept standard text

   **Example Data Structure**:
   ```json
   {
     "Name": "QA Test Case - Record Lifecycle",
     "ID": "qatest-lifecycle-20241219",
     "Code": "QA-LIFECYCLE",
     "Source": "osdu-mcp-server-workflow-test"
   }
   ```
   ```

**Success Criteria**:
- Schema exists and is accessible
- Schema status is "PUBLISHED" (stable)
- Required fields are clearly identified
- Example data structure is understood

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

#### Step 4: Generate OSDU Asset Dashboard

**Purpose**: Comprehensive visibility into created OSDU assets with visual dashboard and detailed analysis

**🔍 Asset Analysis Process**:

1. **Retrieve Complete Record Details**
   **MCP Tool**: `storage_get_record`
   ```
   storage_get_record(id="[record-id-from-step-3]")
   ```

2. **Analyze Legal Tag Details**
   **MCP Tool**: `legaltag_get`
   ```
   legaltag_get(name="[your-legal-tag-name]")
   ```

3. **Check Version History**
   **MCP Tool**: `storage_list_record_versions`
   ```
   storage_list_record_versions(id="[record-id-from-step-3]")
   ```

4. **Generate Asset Dashboard**

   ```
   ## 📊 OSDU Asset Dashboard
   ┌─────────────────────────────────────────────────────────────────┐
   │  🏗️  ASSET INVENTORY                           Status: ✅ HEALTHY │
   ├─────────────────────────────────────────────────────────────────┤
   │ Storage Record │ opendes:record:12345      │ v1    │ ✅ Active   │
   │ Legal Tag      │ opendes-public-usa-general│ -     │ ✅ Valid    │
   │ Schema         │ ProcessingParameterType   │ 1.0.0 │ ✅ Published│
   │ Search Index   │ [Pending Analysis]        │ -     │ ⏳ TBD      │
   └─────────────────────────────────────────────────────────────────┘

   🔐 ACCESS CONTROL MATRIX
   ┌────────────────┬─────────────────────────────┬────────────────┐
   │ Permission     │ Groups                      │ Domain         │
   ├────────────────┼─────────────────────────────┼────────────────┤
   │ 👀 Viewers     │ data.default.viewers        │ contoso.com    │
   │ 👑 Owners      │ data.default.owners         │ contoso.com    │
   │ 🌍 Scope       │ Partition: opendes          │ Public Access  │
   └────────────────┴─────────────────────────────┴────────────────┘
   ```

5. **Create Asset Cards**

   ```
   ## 📇 OSDU Asset Cards

   ┌─────────────────────────────────┐ ┌─────────────────────────────────┐
   │ 📄 STORAGE RECORD               │ │ ⚖️ LEGAL TAG                    │
   │ ID: opendes:record:12345        │ │ Name: opendes-public-usa-general│
   │ Kind: ProcessingParameterType   │ │ Classification: Public          │
   │ Version: 1                      │ │ Contract: GENERAL-001           │
   │ Size: 2.1 KB                    │ │ Countries: US                   │
   │ Created: 2024-12-19 14:30 UTC   │ │ Expires: 2025-06-30             │
   │ Status: ✅ Active               │ │ Status: ✅ Valid                │
   │                                 │ │                                 │
   │ 🎯 Key Data:                    │ │ 🎯 Compliance:                  │
   │ • Name: QA Test Case            │ │ • Export: EAR99                 │
   │ • ID: qatest-lifecycle          │ │ • Personal Data: None           │
   │ • Source: mcp-server-test       │ │ • Data Type: Public Domain      │
   └─────────────────────────────────┘ └─────────────────────────────────┘
   ```

6. **Generate Workflow Timeline**

   ```
   ⏰ WORKFLOW TIMELINE
   14:30:15 │ ⚖️  Legal tag selected: [tag-name] ([new/existing])
   14:30:18 │ 📋 Schema validated: ProcessingParameterType:1.0.0
   14:30:22 │ 📄 Record created: [record-id] (v1)
   14:30:25 │ 🔍 Asset dashboard generated
   14:XX:XX │ ⏳ [Next: Search validation]

   ⏱️  Current workflow time: ~45 seconds
   🎯 Success rate: 100% (4/6 phases completed)
   ```

**Validation Points**:
- Record structure matches schema requirements
- ACL and legal metadata are properly configured
- Data payload is correctly stored and accessible
- Version information is accurate (typically v1 for new records)
- Asset relationships are properly established

---

### Phase 4: Search Validation

#### Step 5: Verify Record Indexing & Discoverability

**Purpose**: Confirm record is properly indexed and discoverable through OSDU search

**🔍 Search Validation Process**:

**Wait Period**: Allow 30-60 seconds for search indexing to complete

1. **Search by Record ID**
   **MCP Tool**: `search_by_id`
   ```
   search_by_id(id="[record-id-from-step-3]")
   ```

2. **Search by Data Content**
   **MCP Tool**: `search_query`
   ```
   search_query(
     query="data.ID:(\"qatest-lifecycle-20241219\")",
     kind="osdu:wks:reference-data--ProcessingParameterType:1.0.0",
     limit=10
   )
   ```

3. **Update Asset Dashboard with Search Status**

   ```
   ## 📊 Updated OSDU Asset Dashboard
   ┌─────────────────────────────────────────────────────────────────┐
   │  🏗️  ASSET INVENTORY                           Status: ✅ HEALTHY │
   ├─────────────────────────────────────────────────────────────────┤
   │ Storage Record │ opendes:record:12345      │ v1    │ ✅ Active   │
   │ Legal Tag      │ opendes-public-usa-general│ -     │ ✅ Valid    │
   │ Schema         │ ProcessingParameterType   │ 1.0.0 │ ✅ Published│
   │ Search Index   │ Indexed & Discoverable    │ -     │ ✅ Ready    │
   └─────────────────────────────────────────────────────────────────┘
   ```

**Validation Points**:
- Record appears in search results within 60 seconds
- Search metadata matches record data
- Record data is properly indexed and searchable
- Total count > 0 indicates successful indexing

**Common Issue**: If record doesn't appear immediately, wait additional 30 seconds and retry. Search indexing can have delays in some OSDU environments.

---

### Phase 5: Interactive Cleanup & Safety Validation

#### Step 6: Interactive Cleanup with Safety Validation

**Purpose**: Safe, informed cleanup with comprehensive validation and user confirmation

## 🛡️ Pre-Deletion Safety Assessment

**⚠️ CRITICAL**: Always validate what you're about to remove before proceeding with any destructive operations.

### 1. **Comprehensive Asset Inspection**

1. **Inspect Storage Record Details**
   **MCP Tool**: `storage_get_record`
   ```
   storage_get_record(id="[record-id-from-step-3]")
   ```
   **Verify**: Confirm this is test data by checking:
   - Data payload contains test identifiers
   - Creation timestamp is recent (workflow session)
   - Record size/content matches your test data

2. **Check Legal Tag Usage** (Critical for Shared Resources)
   **MCP Tool**: `search_query`
   ```
   search_query(
     query="legal.legaltags:([your-legal-tag-name])",
     kind="*:*:*:*",
     limit=50
   )
   ```
   **Verify**: How many records use this legal tag?
   - If > 1 result: Legal tag is shared, DO NOT DELETE
   - If = 1 result: Only your test record uses it, safe to delete

3. **Review Asset Summary** (From Step 4 Dashboard)
   Review your complete asset dashboard before proceeding

### 2. **Generate Safety Assessment Matrix**

```
## 🛡️ Pre-Deletion Safety Assessment

┌─────────────────────┬──────────┬─────────────────────┬────────────────┐
│ Safety Check        │ Status   │ Details             │ Action         │
├─────────────────────┼──────────┼─────────────────────┼────────────────┤
│ 🏷️  Test Data Only  │ ✅ PASS  │ Contains 'test' ID  │ Safe to delete │
│ 🔗 No Dependencies  │ ✅ PASS  │ No child records    │ Safe to delete │
│ 👥 Limited Scope    │ ✅ PASS  │ Only test users     │ Safe to delete │
│ ⏰ Recent Creation  │ ⚠️  WARN │ Created <1 hour ago │ Verify intent  │
│ 🌍 Partition Scope  │ ✅ PASS  │ Test partition      │ Safe to delete │
│ 🏷️  Legal Tag Used  │ ⚠️  CHECK│ Tag used elsewhere  │ Keep legal tag │
└─────────────────────┴──────────┴─────────────────────┴────────────────┘
```

### 3. **Create Deletion Plan**

```
## 📋 Deletion Plan

**Will Delete**:
- ✅ Storage Record: `[record-id]` (confirmed test data only)

**Will Keep**:
- ⚖️  Legal Tag: `[legal-tag-name]` (used by other records OR reusable)
- 📋 Schema: `ProcessingParameterType:1.0.0` (shared OSDU resource)

**Reasoning**:
- Storage record is test-only and safe to remove
- Legal tag [is shared/was created for this test] - [keep/delete] accordingly
- Schema is a shared OSDU resource and should never be deleted
```

### 4. **Interactive Confirmation**

```
📊 **DELETION SUMMARY**
You created these OSDU assets during this workflow:
   • 1 Storage Record (test data)
   • [0/1] Legal Tag ([used existing/created new])
   • 0 Schemas (used existing shared resource)

🗑️  **Ready to delete**: [#] test-only resources
🔒 **Will preserve**: [#] shared/reusable resources

❓ **PROCEED WITH CLEANUP?**

Options:
- Type 'YES' to confirm deletion of test storage record only
- Type 'DELETE-ALL' to delete both record AND legal tag (if safe)
- Type 'NO' to keep all assets for further testing
- Type 'DETAILS' to see full asset information again

⚠️  **CRITICAL**: Only proceed after confirming all assets are test-only resources
```

### 5. **Execute Cleanup** (Only After Confirmation)

**If User Confirms 'YES' or 'DELETE-ALL':**

1. **Delete Storage Record**
   **MCP Tool**: `storage_delete_record`
   ```
   storage_delete_record(id="[record-id-from-step-3]")
   ```

2. **Delete Legal Tag** (Only if 'DELETE-ALL' and confirmed safe)
   **MCP Tool**: `legaltag_delete`
   ```
   legaltag_delete(
     name="[legal-tag-name]",
     confirm=true
   )
   ```

### 6. **Verify Cleanup Success**

1. **Verify Record Deletion**
   **MCP Tool**: `storage_get_record`
   ```
   storage_get_record(id="[record-id-from-step-3]")
   ```
   **Expected**: Error indicating record not found or deleted

2. **Verify Legal Tag Status** (if deleted)
   **MCP Tool**: `legaltag_get`
   ```
   legaltag_get(name="[legal-tag-name]")
   ```
   **Expected**: Error if deleted, success if preserved

3. **Final Asset Status**
   ```
   ## ✅ Cleanup Complete

   **Deleted**:
   - 📄 Storage Record: Successfully removed
   - ⚖️  Legal Tag: [Removed/Preserved] as planned

   **Preserved**:
   - 📋 Schema: ProcessingParameterType:1.0.0 (shared resource)
   - [Other preserved resources]

   **Result**: Test environment cleaned, shared resources preserved
   ```

**Success Criteria**:
- Test resources properly removed with confirmation
- Shared resources preserved and still accessible
- Clean environment ready for future testing

---

## Interactive Workflow Validation Checkpoints

### Phase-by-Phase Success Criteria

**Phase 1: Legal Tag Discovery**
- [ ] **Discovery**: Successfully listed available legal tags
- [ ] **Analysis**: Generated recommendation table with reasoning
- [ ] **Selection**: Chose appropriate legal tag strategy (existing/new)
- [ ] **Validation**: Confirmed legal tag exists and is valid

**Phase 2: Schema Discovery**
- [ ] **Discovery**: Listed available schemas with complexity analysis
- [ ] **Selection**: Chose appropriate schema for testing workflow
- [ ] **Requirements**: Understood required vs optional fields
- [ ] **Validation**: Confirmed schema is published and stable

**Phase 3: Record Creation**
- [ ] **Templates**: Accessed ACL and record templates for environment
- [ ] **Creation**: Successfully created storage record
- [ ] **Validation**: Record ID and version assigned correctly

**Phase 4: Asset Dashboard**
- [ ] **Dashboard**: Generated complete asset inventory status
- [ ] **ACL Analysis**: Confirmed access control configuration
- [ ] **Asset Cards**: Reviewed detailed record and legal tag information
- [ ] **Timeline**: Tracked workflow progress and timing

**Phase 5: Search Validation**
- [ ] **Indexing**: Record discoverable via search within 60 seconds
- [ ] **Queries**: Both ID and content searches return correct results
- [ ] **Dashboard Update**: Search status updated to "Ready"

**Phase 6: Interactive Cleanup**
- [ ] **Safety Assessment**: Completed comprehensive pre-deletion validation
- [ ] **Asset Inspection**: Confirmed test-only data and dependencies
- [ ] **User Confirmation**: Obtained explicit cleanup confirmation
- [ ] **Selective Cleanup**: Deleted test resources, preserved shared assets
- [ ] **Verification**: Confirmed successful cleanup with proper preservation

### Enhanced Error Indicators
- **Discovery Failures** → Check service connectivity and permissions
- **Recommendation Errors** → Verify legal tag/schema accessibility
- **Permission Denied** → Check write/delete mode environment variables
- **Schema Validation** → Review record structure against schema requirements
- **ACL Format Errors** → Verify data domain configuration and group format
- **Search Indexing Delays** → Normal behavior, wait 30-60 seconds and retry
- **Safety Assessment Failures** → Review asset inspection results before cleanup
- **Cleanup Incomplete** → Check delete permissions and confirmation parameters

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

## Interactive Workflow Summary

This enhanced workflow transforms the OSDU record lifecycle from a rigid script into an intelligent, interactive experience:

### 🎯 **Interactive Discovery & Intelligence**
1. **Legal Tag Discovery** → Smart analysis of existing resources with recommendations
2. **Schema Discovery** → Complexity analysis and intelligent schema selection
3. **Record Creation** → Template-guided creation with environment-specific formats

### 📊 **Visual Asset Management**
4. **Asset Dashboard** → Comprehensive visibility with status tables and detailed cards
5. **Search Validation** → Indexing verification with dashboard updates

### 🛡️ **Safe & Informed Cleanup**
6. **Interactive Cleanup** → Safety assessment, dependency analysis, and user confirmation

### 🌟 **Key Innovations**

**Intelligence**:
- Discovers existing OSDU resources instead of blind creation
- Provides reasoning for all recommendations
- Adapts workflow based on environment and user choices

**Safety**:
- Multiple validation layers prevent accidental data loss
- Dependency analysis identifies shared vs. test-only resources
- Interactive confirmation with full context before destructive operations

**Visibility**:
- Visual dashboard with status indicators and ACL matrices
- Asset cards showing detailed resource information
- Timeline tracking workflow progress and performance

**Education**:
- Users learn about OSDU resource relationships
- Guided discovery teaches platform best practices
- Clear explanations of reasoning behind recommendations

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
