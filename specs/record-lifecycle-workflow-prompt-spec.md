# Specification for OSDU MCP Server (Record Lifecycle Workflow Prompt)

## Overview

The Record Lifecycle Workflow Prompt provides comprehensive, step-by-step guidance for the complete OSDU record lifecycle - from legal compliance setup through record creation, validation, discovery, and cleanup. This workflow-style prompt demonstrates end-to-end integration across all major OSDU services and serves as both educational content and a practical testing methodology.

## Purpose & Scope

### Core Purpose
Enable AI assistants and users to understand and execute the complete record lifecycle workflow in OSDU, demonstrating proper service integration, validation patterns, and best practices for data compliance and management.

### Primary Goals
1. **End-to-End Workflow**: Complete record lifecycle from legal setup to cleanup
2. **Service Integration**: Demonstrate how Legal, Schema, Storage, and Search services work together
3. **Validation Methodology**: Provide verification steps at each stage
4. **Best Practices**: Showcase proper OSDU compliance and data management patterns
5. **Error Handling**: Guide users through common issues and troubleshooting
6. **Testing Framework**: Serve as a comprehensive integration test methodology

### Workflow Scope
The prompt covers the complete record lifecycle:
- **Legal Compliance Setup** → Create and verify legal tags
- **Schema Validation** → Retrieve and understand record structure requirements
- **Record Creation** → Create properly structured records with compliance metadata
- **Record Verification** → Validate successful creation and versioning
- **Search Validation** → Confirm record indexing and discoverability
- **Cleanup Procedures** → Proper resource cleanup and cleanup verification

### Enhanced with MCP Resources
The workflow is enhanced with template resources that eliminate format guessing:
- **Template Legal Tags** → Working legal tag structures users can copy/modify
- **Sample Records** → Complete valid record templates for different schemas
- **ACL Examples** → Environment-specific ACL format references
- **Search Patterns** → Proven query examples for validation

### Excluded Capabilities
- Advanced batch processing workflows (future enhancement)
- Multi-partition record operations (future enhancement)
- Complex schema evolution scenarios (future enhancement)
- Production deployment considerations (separate documentation)

## Architectural Integration

### MCP Protocol Alignment
This prompt follows established patterns:
- Implements ADR-024 (Prompt Implementation Pattern)
- Uses ADR-025 (Prompt Naming Convention) - `guide_record_lifecycle`
- Follows ADR-026 (Content Generation Strategy) for maintainable content

### Service Dependencies
The workflow demonstrates integration across all major OSDU services:
- **Legal Service** → Legal tag creation and management
- **Schema Service** → Record structure validation
- **Storage Service** → Record CRUD operations and versioning
- **Search Service** → Record indexing and discovery
- **Entitlements Service** → ACL validation (referenced in examples)

### Existing Tool Integration
Leverages all implemented MCP tools:
```
Legal: legaltag_create, legaltag_get, legaltag_delete
Schema: schema_get
Storage: storage_create_update_records, storage_get_record, storage_list_record_versions
Search: search_query, search_by_id
Foundation: health_check (for environment validation)
```

### MCP Resources Integration

#### Resource-Enhanced Workflow
The workflow is significantly enhanced by providing working template resources that eliminate format guessing and reduce errors:

**Problem Solved**: Instead of users guessing at ACL formats, legal tag structures, or record schemas and failing with validation errors, they can reference proven templates that actually work.

#### Resource Architecture
```
resources/
├── templates/
│   ├── legal-tag-template.json         # Working legal tag structure
│   ├── processing-parameter-record.json # Complete valid record template
│   ├── wellbore-record.json           # Alternative record type template
│   └── dataset-record.json            # Another common record type
├── references/
│   ├── acl-format-examples.json       # Environment-specific ACL formats
│   ├── search-query-patterns.json     # Proven search query examples
│   └── validation-checkpoints.json    # Success criteria templates
└── workflows/
    ├── minimal-workflow.json          # Simplified workflow for quick tests
    └── complete-workflow.json         # Full lifecycle workflow
```

#### Resource-Driven Workflow Steps
Each workflow phase references relevant resources:

1. **Legal Setup**: "Read `legal-tag-template.json` for structure, modify with your values"
2. **Record Creation**: "Use `processing-parameter-record.json` as template, replace data section"
3. **ACL Configuration**: "Reference `acl-format-examples.json` for your environment"
4. **Search Validation**: "Use patterns from `search-query-patterns.json`"

#### Benefits of Resource Integration
- **Eliminates Format Guessing**: Users copy working templates instead of guessing
- **Reduces Errors**: Templates are validated and known to work
- **Educational Value**: Users learn proper structure by example
- **Environment Adaptation**: Multiple templates for different deployment scenarios
- **Workflow Acceleration**: Skip trial-and-error, start with working code

## Prompt Specification

### `guide_record_lifecycle` Prompt

**Function Signature**:
```python
async def guide_record_lifecycle() -> List[Message]:
```

**Purpose**: Provide comprehensive guidance for executing the complete OSDU record lifecycle workflow with validation at each step.

**Parameters**: None (initial implementation)

**Expected Behavior**:
- Return comprehensive workflow guide as formatted user message
- Include step-by-step instructions with MCP tool examples
- Provide validation checkpoints and troubleshooting guidance
- Demonstrate proper service integration patterns
- Include real-world examples with proper OSDU compliance

**Response Contract**:
```python
[
    {
        "role": "user", 
        "content": "# OSDU Record Lifecycle Workflow Guide\n\n[comprehensive workflow content...]"
    }
]
```

## Content Requirements

### 1. Workflow Overview
```markdown
## Complete Record Lifecycle Workflow

### Process Flow
Legal Setup → Schema Validation → Record Creation → Record Verification → Search Validation → Cleanup

### Time Estimate: 10-15 minutes
### Prerequisites: Write and delete permissions enabled, valid OSDU environment
```

### 2. Prerequisites & Environment Setup
```markdown
## Prerequisites

### Required Permissions
- OSDU_MCP_ENABLE_WRITE_MODE=true (for record and legal tag creation)
- OSDU_MCP_ENABLE_DELETE_MODE=true (for cleanup operations)

### Environment Validation
Use health_check tool to verify all services are available:
[MCP tool example]

### Required Information
- Target schema kind (e.g., osdu:wks:reference-data--ProcessingParameterType:1.0.0)
- Legal tag name (must be unique)
- Record data payload
```

### 3. Step-by-Step Workflow Guide

#### Phase 1: Legal Compliance Setup
```markdown
### Step 1: Create Legal Tag

**Purpose**: Establish legal compliance framework for the record

**Resource Template**: First, examine the legal tag template structure
**MCP Resource**: `legal-tag-template.json`
[Shows working legal tag structure with all required fields]

**MCP Tool**: legaltag_create
**Example**:
[Tool call using template values, user modifies name/dates]

**Validation**: Verify tag creation
**MCP Tool**: legaltag_get
[Validation example]

**Success Criteria**: 
- Legal tag created with proper compliance properties
- Tag accessible and properly formatted
- Template structure followed correctly
```

#### Phase 2: Schema Validation
```markdown
### Step 2: Retrieve Target Schema

**Purpose**: Understand record structure and validation requirements

**MCP Tool**: schema_get
**Example**:
[Schema retrieval example]

**Validation Points**:
- Schema exists and is accessible
- Required properties identified
- Schema version compatibility confirmed
```

#### Phase 3: Record Creation & Verification
```markdown
### Step 3: Create Storage Record

**Purpose**: Create properly structured record with compliance metadata

**Resource Templates**: Start with working record templates
**MCP Resources**: 
- `processing-parameter-record.json` (complete valid record structure)
- `acl-format-examples.json` (environment-specific ACL formats)

**Template Usage**:
1. Read record template for complete structure
2. Replace data section with your specific values
3. Use correct ACL format for your environment
4. Reference your legal tag from Phase 1

**MCP Tool**: storage_create_update_records
**Example**:
[Tool call using template structure with user modifications]

**Validation Steps**:
1. Verify record creation success using template validation patterns
2. Check record structure matches template requirements
3. Validate version information

**MCP Tools**: 
- storage_get_record
- storage_list_record_versions
[Validation examples using success criteria from templates]
```

#### Phase 4: Search Validation
```markdown
### Step 4: Verify Record Indexing

**Purpose**: Confirm record is properly indexed and discoverable

**Resource Reference**: Use proven search patterns
**MCP Resource**: `search-query-patterns.json`
[Contains working query examples for different search scenarios]

**Template-Driven Search**:
1. Use ID-based search pattern from templates
2. Apply field-specific search examples
3. Follow timing guidance for indexing delays

**MCP Tool**: search_query
**Example**:
[Search query using template patterns with your record ID]

**Validation Points**:
- Record appears in search results (using template success criteria)
- Search metadata matches template expectations
- Record data properly indexed per template validation
```

#### Phase 5: Cleanup & Verification
```markdown
### Step 5: Complete Cleanup

**Purpose**: Remove test resources and verify cleanup

**Cleanup Sequence**:
1. Delete storage record
2. Delete legal tag
3. Verify removal

**MCP Tools**:
- storage_delete_record
- legaltag_delete
[Cleanup examples with verification]
```

### 4. Validation Checkpoints
```markdown
## Validation Checkpoints

### After Each Step
1. **Legal Tag**: Verify creation and properties
2. **Schema**: Confirm accessibility and structure
3. **Record**: Validate creation, metadata, and versioning
4. **Search**: Confirm indexing and discoverability
5. **Cleanup**: Verify complete resource removal

### Error Indicators
- Permission denied errors
- Schema validation failures
- Record creation failures
- Search indexing delays
- Cleanup incomplete
```

### 5. Error Handling & Troubleshooting
```markdown
## Common Issues & Solutions

### Permission Errors
**Issue**: Write operations fail with permission denied
**Solution**: Verify OSDU_MCP_ENABLE_WRITE_MODE=true

### Schema Validation Errors
**Issue**: Record creation fails due to schema mismatch
**Solution**: Review schema requirements and adjust record structure

### Search Indexing Delays
**Issue**: Record not immediately discoverable
**Solution**: Search indexing may take 30-60 seconds, retry search

### Cleanup Failures
**Issue**: Resources not properly removed
**Solution**: Check delete permissions and retry with proper confirmation
```

### 6. Advanced Patterns & Variations
```markdown
## Advanced Workflow Patterns

### Multi-Record Creation
[Example of creating multiple related records]

### Schema Evolution Testing
[Example of testing schema compatibility]

### Performance Validation
[Example of measuring workflow timing]

### Error Recovery Testing
[Example of handling partial failures]
```

### 7. Best Practices Summary
```markdown
## OSDU Best Practices Demonstrated

### Compliance
- Proper legal tag usage
- Required metadata inclusion
- ACL configuration

### Data Management
- Record versioning awareness
- Proper cleanup procedures
- Validation at each step

### Service Integration
- Dependency management
- Error handling patterns
- Resource lifecycle management
```

## Implementation Requirements

### Content Generation Strategy
Following ADR-026:
- **Static Framework**: Core workflow structure and patterns
- **Dynamic Examples**: Current tool signatures and parameters
- **Template Approach**: Consistent formatting and structure
- **Maintenance Hooks**: Easy updates when tools change

### Integration Points
- **Tool Discovery**: Automatically reference current MCP tools
- **Configuration Integration**: Use current server configuration patterns
- **Error Message Alignment**: Consistent with existing error handling
- **Write Protection Integration**: Respect current permission models

### MCP Resources Implementation

#### Resource Structure
```
src/osdu_mcp_server/resources/
├── templates/
│   ├── legal-tag-template.json         # Working legal tag structure
│   ├── processing-parameter-record.json # Complete valid record template
│   └── dataset-record.json            # Alternative record type
├── references/
│   ├── acl-format-examples.json       # Environment-specific ACL formats
│   ├── search-query-patterns.json     # Proven search query examples
│   └── validation-checkpoints.json    # Success criteria templates
└── workflows/
    ├── minimal-workflow.json          # Quick test workflow
    └── complete-workflow.json         # Full lifecycle workflow
```

#### Resource Content Requirements
- **Validated Templates**: All resources must contain working, tested examples
- **Environment Agnostic**: Templates should work across different OSDU deployments
- **Documentation**: Each resource includes comments explaining usage
- **Versioning**: Resources track OSDU schema versions and API changes

#### Resource Registration
- **FastMCP Integration**: Resources registered with MCP server for discovery
- **URI Pattern**: `file://resources/{category}/{filename}.json`
- **Metadata**: Include description, usage, and last-updated information
- **Access Control**: Resources are read-only reference materials

#### Template Validation Process
1. **Create** resource from successful API responses
2. **Test** resource content with actual OSDU environment
3. **Validate** resource works across different partitions/environments
4. **Document** usage patterns and modification guidance
5. **Update** resources when OSDU schemas or APIs change

### Performance Requirements
- **Generation Time**: < 500ms for prompt content generation
- **Content Size**: 8-12KB formatted content (comprehensive but manageable)
- **Memory Usage**: Minimal overhead for content generation
- **Caching Strategy**: Static content with dynamic tool integration

## Testing Strategy

### Core Testing Principle
Following ADR-010: Test the **prompt function behavior**, not the **workflow execution success**. We verify the prompt returns properly structured guidance, not whether the described workflow actually works in a live OSDU environment.

### Test Categories

1. **Message Format Testing**
   ```python
   async def test_guide_record_lifecycle_returns_proper_message_format():
       result = await guide_record_lifecycle()
       assert isinstance(result, list)
       assert len(result) == 1
       assert result[0]["role"] == "user"
       assert isinstance(result[0]["content"], str)
       assert len(result[0]["content"]) > 1000  # Substantial content
   ```

2. **Content Generation Testing**
   ```python
   async def test_guide_record_lifecycle_generates_content():
       result = await guide_record_lifecycle()
       content = result[0]["content"]
       
       # Verify key sections present
       assert "Record Lifecycle Workflow" in content
       assert "Prerequisites" in content
       assert "Step-by-Step" in content
       assert "Validation" in content
       assert "Troubleshooting" in content
   ```

3. **Tool Reference Testing**
   ```python
   async def test_guide_record_lifecycle_references_current_tools():
       result = await guide_record_lifecycle()
       content = result[0]["content"]
       
       # Verify current MCP tools are referenced
       assert "legaltag_create" in content
       assert "storage_create_update_records" in content
       assert "search_query" in content
   ```

4. **Resource Reference Testing**
   ```python
   async def test_guide_record_lifecycle_references_resources():
       result = await guide_record_lifecycle()
       content = result[0]["content"]
       
       # Verify resource templates are referenced in workflow
       assert "legal-tag-template.json" in content
       assert "processing-parameter-record.json" in content
       assert "acl-format-examples.json" in content
       assert "search-query-patterns.json" in content
   ```

5. **MCP Protocol Compliance**
   ```python
   async def test_guide_record_lifecycle_mcp_integration():
       # Test prompt is discoverable and executable via MCP
       # Test proper integration with FastMCP server
   ```

### What NOT to Test
- **Workflow Execution**: Whether the described workflow actually succeeds
- **OSDU Integration**: Whether MCP tools work with real OSDU instances
- **Content Quality**: Whether the guidance is helpful or accurate
- **Specific Formatting**: Exact markdown structure or wording

## Success Criteria

**✅ Record Lifecycle Workflow Prompt Complete When:**

- [ ] Prompt architecture defined following established ADR patterns
- [ ] `guide_record_lifecycle` prompt implemented and functional
- [ ] Comprehensive workflow content covering all major phases
- [ ] Integration with all relevant MCP tools (legal, schema, storage, search)
- [ ] **MCP Resources implemented and registered**:
  - [ ] `legal-tag-template.json` with working legal tag structure
  - [ ] `processing-parameter-record.json` with complete valid record template
  - [ ] `acl-format-examples.json` with environment-specific formats
  - [ ] `search-query-patterns.json` with proven query examples
- [ ] **Resource-enhanced workflow content** referencing templates at each phase
- [ ] Validation checkpoints and error handling guidance included
- [ ] Testing strategy implemented and passing (including resource reference tests)
- [ ] MCP client integration verified (prompt and resources discoverable)
- [ ] Content generation performance meets requirements
- [ ] Documentation updated with new prompt capability and resource usage

## Benefits

### For AI Assistants
- **Workflow Understanding**: Complete picture of OSDU record operations
- **Integration Patterns**: How to orchestrate multiple OSDU services
- **Template-Driven Execution**: Working examples eliminate format guessing
- **Error Reduction**: Proven templates reduce validation failures
- **Pattern Learning**: Real examples teach proper OSDU structure
- **Validation Methodology**: How to verify operation success

### For Users
- **Learning Tool**: Comprehensive OSDU workflow education with working examples
- **Testing Framework**: Reliable method for validating OSDU environments
- **Template Library**: Copy-paste ready examples for immediate use
- **Error Prevention**: Proven templates reduce trial-and-error cycles
- **Best Practices**: Proper compliance and data management patterns
- **Troubleshooting Guide**: Common issues and solutions

### For Maintainers
- **Integration Testing**: Comprehensive workflow validation
- **Documentation**: Self-documenting service integration patterns
- **Template Maintenance**: Reusable resource templates for multiple workflows
- **Quality Assurance**: Standardized testing methodology with validated examples
- **Training Resource**: Onboarding tool for new team members with real templates

## Future Enhancements

### Phase 2: Advanced Workflows
- Multi-record batch operations
- Complex schema evolution scenarios
- Cross-partition record operations
- Performance optimization patterns

### Phase 3: Interactive Workflows
- Step-by-step guided execution
- Real-time validation feedback
- Error recovery automation
- Workflow customization options

### Phase 4: Analytics Integration
- Workflow performance metrics
- Success rate tracking
- Error pattern analysis
- Optimization recommendations

## Integration with Existing Capabilities

### Prompt Ecosystem
- **Complements** `list_mcp_assets`: Shows what's available vs. how to use it
- **Extends** `guide_search_patterns`: Workflow context for search operations
- **Prepares for** future workflow prompts: Establishes patterns for complex workflows

### Service Integration
- **Legal Service**: Demonstrates compliance setup and management
- **Schema Service**: Shows proper schema validation patterns
- **Storage Service**: Complete record lifecycle management
- **Search Service**: Discovery and validation patterns
- **Foundation**: Environment validation and health checking

### Write Protection Integration
- **Demonstrates** proper permission setup and validation
- **Explains** dual permission model (write vs. delete)
- **Validates** permission requirements at each workflow step

## References

- [Foundation Prompts Specification](foundation-prompts-spec.md)
- [Model Context Protocol Prompts Specification](https://modelcontextprotocol.io/specification/#prompts)
- [ADR-024: Prompt Implementation Pattern](../docs/adr/024-prompt-implementation-pattern.md)
- [ADR-025: Prompt Naming Convention](../docs/adr/025-prompt-naming-convention.md)
- [ADR-026: Content Generation Strategy](../docs/adr/026-content-generation-strategy.md)
- [ADR-010: Testing Philosophy](../docs/adr/010-testing-philosophy-and-strategy.md)
- [ADR-020: Unified Write Protection](../docs/adr/020-unified-write-protection.md)
- [Project Architecture](../docs/project-architect.md)