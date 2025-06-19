# ADR-025: Prompt Naming Convention

## Status
**Accepted** - 2025-06-19

## Context
With the introduction of MCP prompts capability, we need a naming convention that distinguishes prompts from tools while maintaining discoverability and consistency. Tools follow the `{resource}_{action}` pattern (ADR-019), but prompts serve a fundamentally different purpose:

- **Tools**: Perform actions on resources (`partition_list`, `storage_get_record`)
- **Prompts**: Provide guidance, discovery, and interactive content

Prompts are descriptive and assistance-oriented rather than action-oriented, requiring their own naming approach.

## Decision
Adopt **descriptive naming** for prompts that clearly indicates their discovery and guidance purpose.

### Naming Pattern

#### Discovery Prompts
- Format: `{verb}_{subject}` where verb indicates discovery action
- Examples: `list_mcp_assets`, `discover_capabilities`, `explore_workflows`

#### Guidance Prompts (Future)
- Format: `{verb}_{context}` where verb indicates guidance action
- Examples: `guide_data_ingestion`, `troubleshoot_authentication`, `plan_record_creation`

#### Interactive Prompts (Future)
- Format: `{action}_{workflow}` where action indicates interactive process
- Examples: `create_legal_tag_wizard`, `setup_authentication_flow`

### Prompt Categories

1. **Discovery Prompts**: Help users understand server capabilities
   - Purpose: Server introspection and capability overview
   - Pattern: `list_*`, `discover_*`, `explore_*`
   - Example: `list_mcp_assets`

2. **Guidance Prompts**: Provide step-by-step instructions
   - Purpose: Workflow guidance and best practices
   - Pattern: `guide_*`, `help_*`, `explain_*`
   - Example: `guide_data_ingestion`

3. **Interactive Prompts**: Multi-step guided processes
   - Purpose: Complex workflow orchestration
   - Pattern: `create_*_wizard`, `setup_*_flow`
   - Example: `create_legal_tag_wizard`

## Rationale

### Why Not Extend Tool Naming Pattern?
1. **Different Purpose**: Prompts don't act on resources, they provide information
2. **User Mental Model**: Users think of prompts as "help" not "actions"
3. **Discoverability**: Clear distinction helps users understand capabilities
4. **Future-Proof**: Allows for prompt-specific patterns without tool conflicts

### Why Descriptive Over Resource-Action?
1. **Content-Oriented**: Prompts deliver content, not perform operations
2. **Natural Language**: Descriptive names match how users think about assistance
3. **Clarity**: Immediately obvious what the prompt provides
4. **Extensibility**: Supports various prompt types without forced patterns

## Implementation

### File Structure
```
prompts/
├── list_assets.py         # list_mcp_assets()
├── guide_workflows.py     # guide_data_workflows() (future)
└── troubleshoot_auth.py   # troubleshoot_authentication() (future)
```

### Function Naming
```python
# Discovery prompts
async def list_mcp_assets() -> List[Message]:
async def discover_capabilities() -> List[Message]:
async def explore_workflows() -> List[Message]:

# Guidance prompts (future)
async def guide_data_ingestion() -> List[Message]:
async def troubleshoot_authentication() -> List[Message]:
async def help_schema_validation() -> List[Message]:

# Interactive prompts (future)  
async def create_legal_tag_wizard() -> List[Message]:
async def setup_authentication_flow() -> List[Message]:
```

### Registration Pattern
```python
# server.py - Prompts section
from .prompts import (
    list_mcp_assets,
    guide_data_ingestion,    # future
    troubleshoot_authentication,  # future
)

# Register prompts
mcp.prompt()(list_mcp_assets)
# mcp.prompt()(guide_data_ingestion)    # future
```

## Alternatives Considered

1. **Extend Tool Pattern to Prompts**
   - **Pros**: Consistent with existing tools
   - **Cons**: Confusing (prompts aren't resource actions), forces unnatural naming
   - **Decision**: Prompts need their own pattern due to different purpose

2. **Generic Naming (help, info, docs)**
   - **Pros**: Simple, familiar terms
   - **Cons**: Not descriptive enough, doesn't scale, unclear purpose
   - **Decision**: Too generic for specific prompt functions

3. **Prefixed Tool Pattern (prompt_list_assets)**
   - **Pros**: Clear prompt identification
   - **Cons**: Redundant prefix, verbose, doesn't improve discoverability
   - **Decision**: Prefix adds noise without value

4. **Question-Style Naming (what_can_i_do)**
   - **Pros**: Natural language feel
   - **Cons**: Inconsistent with function naming conventions, unclear scope
   - **Decision**: Doesn't match Python naming conventions

## Consequences

### Positive
- **Clear Distinction**: Prompts clearly distinguished from tools
- **Purpose-Driven**: Names immediately convey what content is provided
- **Extensible**: Pattern supports future prompt categories
- **Natural Language**: Aligns with how users think about getting help
- **No Conflicts**: Won't conflict with tool naming patterns

### Negative
- **Learning Curve**: Users need to understand two naming patterns
- **Consistency Overhead**: Need to maintain prompt-specific conventions
- **Documentation**: Additional patterns to document and explain

## Guidelines

### Naming Rules
1. **Be Descriptive**: Name should clearly indicate what content is provided
2. **Use Verbs**: Start with action words that indicate the type of assistance
3. **Avoid Acronyms**: Use full words for clarity (`assets` not `ast`)
4. **Consider Scope**: Name should reflect the breadth of content provided
5. **Future-Proof**: Consider how names will work with additional prompts

### Verb Guidelines
- **list_**: Comprehensive overviews and capability listings
- **discover_**: Exploration and discovery-oriented content
- **guide_**: Step-by-step instructions and workflows
- **help_**: Assistance with specific problems or concepts
- **troubleshoot_**: Problem-solving and diagnostic assistance
- **explain_**: Educational content about concepts or features

### Avoid
- Generic terms that don't convey specific purpose
- Resource-action patterns from tools
- Overly long names that are hard to type
- Technical jargon that obscures purpose

## Future Considerations

1. **Prompt Categories**: As we add more prompts, may need sub-categories
2. **Interactive Prompts**: May require special naming for multi-step processes
3. **Domain-Specific**: Consider OSDU-specific terminology for specialized prompts
4. **Internationalization**: Pattern should work with translated content

## Examples

### Current Implementation
- `list_mcp_assets`: Comprehensive server capability overview

### Planned Future Prompts
- `guide_data_ingestion`: Step-by-step data loading workflow
- `troubleshoot_authentication`: Authentication problem solving
- `discover_schemas`: Available schema exploration
- `help_legal_tags`: Legal tag guidance and best practices
- `explain_write_protection`: Write protection concept explanation

## References
- [ADR-019: Tool Naming Convention](019-tool-naming-convention.md) - Tool naming patterns for comparison
- [ADR-024: Prompt Implementation Pattern](024-prompt-implementation-pattern.md) - Prompt implementation requirements
- [Foundation Prompts Specification](../../specs/foundation-prompts-spec.md) - Original prompt requirements