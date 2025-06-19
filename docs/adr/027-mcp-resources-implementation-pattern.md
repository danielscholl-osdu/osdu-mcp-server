# ADR-027: MCP Resources Implementation Pattern

## Status
**Accepted** - 2025-06-19

## Context
The implementation of workflow-style prompts revealed a critical challenge: users need access to working templates and reference examples to avoid format-guessing errors. The OSDU platform has complex data structures (ACL formats, record schemas, legal tags) that are difficult to construct correctly without examples.

MCP provides a Resources capability that allows servers to expose read-only files to AI assistants. This creates an opportunity to provide working templates that eliminate trial-and-error in OSDU workflows.

## Decision
Implement **file-based MCP Resources using JSON templates** with structured discovery and validation patterns.

## Rationale
1. **Error Reduction**: Working templates eliminate format-guessing errors that plague OSDU workflows
2. **Template-Driven Workflows**: Transform error-prone trial-and-error into reliable template-based execution
3. **MCP Protocol Compliance**: Uses standard MCP Resources capability for intended purpose
4. **Maintainable Structure**: JSON files are easy to update and validate
5. **Resource Discovery**: Structured registration enables AI assistants to find relevant templates

## Implementation Details

### Resource Directory Structure
```
src/osdu_mcp_server/resources/
├── templates/           # Working templates for direct use
│   ├── legal-tag-template.json
│   └── processing-parameter-record.json
└── references/          # Reference examples and patterns
    ├── acl-format-examples.json
    └── search-query-patterns.json
```

### Resource Registration Pattern
```python
def get_workflow_resources() -> List[Resource]:
    """Discover and register all workflow resources."""
    resources = []
    base_path = Path(__file__).parent / "resources"
    
    # Templates - working examples for direct use
    templates_path = base_path / "templates"
    if templates_path.exists():
        for json_file in templates_path.glob("*.json"):
            resources.append(Resource(
                uri=f"template://{json_file.stem}",
                name=f"Template: {json_file.stem.replace('-', ' ').title()}",
                description=f"Working template for {json_file.stem.replace('-', ' ')}",
                mimeType="application/json"
            ))
    
    # References - examples and patterns
    references_path = base_path / "references"
    if references_path.exists():
        for json_file in references_path.glob("*.json"):
            resources.append(Resource(
                uri=f"reference://{json_file.stem}",
                name=f"Reference: {json_file.stem.replace('-', ' ').title()}",
                description=f"Reference examples for {json_file.stem.replace('-', ' ')}",
                mimeType="application/json"
            ))
    
    return resources
```

### FastMCP Integration
```python
# server.py registration
from .resources import get_workflow_resources

# Register resources with FastMCP
for resource in get_workflow_resources():
    mcp.add_resource(resource)
```

### JSON Validation Strategy
- **Template Validation**: Working templates must be valid OSDU data structures
- **Reference Validation**: Reference examples include format notes and alternatives
- **Schema Compliance**: Templates follow OSDU API requirements exactly
- **Version Consistency**: Templates updated when OSDU API versions change

## Resource Categories

### Templates (Direct Use)
- **Purpose**: Copy-paste ready structures that work immediately
- **Format**: Valid JSON that can be used as-is with minimal customization
- **Examples**: legal-tag-template.json, processing-parameter-record.json
- **Validation**: Must pass OSDU API validation

### References (Guidance)
- **Purpose**: Format examples and pattern guidance
- **Format**: JSON with comments, alternatives, and explanations
- **Examples**: acl-format-examples.json, search-query-patterns.json
- **Validation**: Educational accuracy, not API compliance

## Content Generation Integration
Resources complement the static content generation strategy (ADR-026):
- **Static Templates**: Provide stable, tested structures
- **Dynamic Discovery**: Resource registration reflects current capabilities
- **Performance**: File-based resources load quickly
- **Maintenance**: Template updates don't require code changes

## Benefits
1. **Error Elimination**: Working templates prevent format-guessing failures
2. **Workflow Reliability**: Template-driven approach ensures consistent success
3. **AI Assistant Friendly**: Standard MCP Resources are easily discoverable
4. **Maintenance Efficiency**: JSON files easier to update than code
5. **Validation Clarity**: Clear separation between working templates and reference examples

## Consequences

### Positive
- **Dramatic Error Reduction**: Eliminates most OSDU format-guessing errors
- **Improved UX**: Template-driven workflows are more reliable and faster
- **Resource Discovery**: AI assistants can find and use relevant templates automatically
- **Maintainable**: JSON templates easier to update than embedded code
- **Extensible**: New templates can be added without code changes

### Negative
- **Template Maintenance**: Need to keep templates current with OSDU API changes
- **File Management**: Additional files to track and version
- **Validation Overhead**: Templates must be validated against OSDU APIs
- **Discovery Complexity**: Resource registration adds code complexity

## Template Maintenance Strategy
1. **API Version Tracking**: Monitor OSDU API changes that affect templates
2. **Validation Testing**: Automated tests verify templates work with current APIs
3. **Update Process**: Template updates follow same review process as code
4. **Version Documentation**: Template changes documented in commit messages

## Success Metrics
- **Error Rate Reduction**: Measure decrease in OSDU format validation errors
- **Workflow Success Rate**: Track completion rate of multi-step OSDU workflows
- **Template Usage**: Monitor which templates are most frequently accessed
- **User Feedback**: Collect feedback on template usefulness and accuracy

## Future Enhancements
1. **Dynamic Templates**: Generate templates based on current OSDU schema versions
2. **Validation API**: Endpoint to validate user data against templates
3. **Template Composition**: Combine multiple templates for complex workflows
4. **Environment-Specific Templates**: Templates customized for different OSDU deployments

## Related ADRs
- **ADR-024**: Prompt Implementation Pattern - prompts that leverage these resources
- **ADR-025**: Prompt Naming Convention - descriptive naming that complements resources
- **ADR-026**: Content Generation Strategy - resources complement static content generation
- **ADR-028**: Data Domain Configuration Pattern - templates use environment-specific domains