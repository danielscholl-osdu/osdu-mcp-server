# Specification for OSDU MCP Server (Foundation: Prompts Capability)

## Overview

The Prompts Capability introduces guided interaction functionality to the OSDU MCP Server through the Model Context Protocol's prompts feature. Prompts provide AI assistants with discoverable, formatted content that explains server capabilities, usage patterns, and workflow guidance.

## Purpose & Scope

### Core Purpose
Enable AI assistants to easily discover and understand the OSDU MCP Server's capabilities through structured, conversational prompts rather than requiring prior knowledge of available tools and workflows.

### Primary Goals
1. **Service Discovery**: Help AI assistants understand what OSDU operations are available
2. **Usage Guidance**: Provide clear examples and patterns for common workflows  
3. **Quick Start**: Reduce the learning curve for new users and AI assistants
4. **Self-Documentation**: Make the server capabilities self-describing

### Included Capabilities
- Server asset listing and overview
- Tool discovery with descriptions
- Configuration guidance
- Workflow examples and best practices

### Excluded Capabilities
- Dynamic prompt generation based on user context (future enhancement)
- Interactive multi-turn prompts (beyond MCP specification)
- User-specific customization (future enhancement)

## Architectural Integration

### MCP Protocol Alignment
Prompts are a first-class MCP capability alongside tools and resources. They return Message objects containing structured content that AI assistants can present to users or use for context.

### Server Architecture Impact
- **New Component**: `src/osdu_mcp_server/prompts/` directory
- **Registration Pattern**: Similar to tools, prompts must be registered with FastMCP server
- **Testing Integration**: Prompts follow same testing philosophy as existing components
- **Documentation**: Prompts become part of server capability documentation

### Design Principles
- **Content as Code**: Prompts are structured content wrapped in Python functions
- **Dynamic Discovery**: Prompt content should reflect current server state and available tools
- **Consistency**: Follow established naming and implementation patterns
- **Maintainability**: Prompt content should be easy to update as server capabilities evolve

## First Prompt Specification

### `list_mcp_assets` Prompt

**Function Signature**:
```python
async def list_mcp_assets() -> List[Message]:
```

**Purpose**: Provide comprehensive overview of all OSDU MCP Server capabilities, tools, and usage guidance.

**Parameters**: None (initial implementation)

**Expected Behavior**:
- Return single user message containing formatted server overview
- Include all available tools organized by service
- Provide configuration guidance and setup instructions
- Include common workflow examples
- Show quick start patterns for OSDU operations

**Response Contract**:
```python
[
    {
        "role": "user",
        "content": "# OSDU MCP Server Assets\n\n[formatted content...]"
    }
]
```

**Content Requirements**:
1. **Server Overview**: Identity, status, capability summary
2. **Available Tools**: All tools grouped by service with descriptions
3. **Configuration Guide**: Environment variables and authentication setup
4. **Workflow Examples**: Common OSDU operation patterns
5. **Quick Start**: Getting started guidance for new users

## Implementation Requirements

### Directory Structure
```
src/osdu_mcp_server/
├── prompts/
│   ├── __init__.py
│   └── list_assets.py
└── shared/
    └── [existing shared components]
```

### Registration Integration
Prompts must be registered with the FastMCP server similar to tools:
- Follow existing registration patterns
- Maintain consistency with tool registration approach
- Enable discovery through MCP protocol

### Content Generation Strategy
- **Dynamic Discovery**: Automatically detect available tools and services
- **Template-Based**: Use structured templates for consistent formatting
- **Maintainable**: Easy to update as server capabilities change
- **Performance**: Generate content efficiently without blocking

## Testing Strategy

### Core Testing Principle
Test the **data provider** (prompt function), not the **data consumer** (AI model). We verify that prompts return properly structured data, not how AI models interpret that data.

### Test Categories

1. **Message Format Testing**: Verify prompt returns correct MCP Message structure
   ```python
   # Test: Returns List[Message] with proper structure
   result = await list_mcp_assets()
   assert isinstance(result, list)
   assert result[0]["role"] == "user"
   assert isinstance(result[0]["content"], str)
   ```

2. **Function Contract Testing**: Verify prompt functions execute correctly
   ```python
   # Test: Function executes without errors
   # Test: Returns non-empty content
   # Test: Async execution completes
   ```

3. **Data Generation Testing**: Verify content generation works reliably
   ```python
   # Test: Content string is generated
   # Test: No exceptions during generation
   # Test: Content has minimum expected length
   ```

4. **MCP Protocol Compliance**: Verify integration with MCP server
   ```python
   # Test: Prompt is discoverable via MCP protocol
   # Test: Prompt execution via MCP returns expected format
   ```

### What NOT to Test
- **Content Quality**: Whether the prompt content is "good" or "helpful"
- **AI Interpretation**: How models use the prompt content
- **Subjective Content**: Whether explanations make sense to humans
- **Specific Formatting**: Exact markdown structure or wording

### Testing Philosophy
Following [ADR-010: Testing Philosophy and Strategy](../docs/adr.md#adr-010-testing-philosophy-and-strategy):
- Test observable behavior: function signature, return type, data structure
- Mock minimal dependencies: only external systems, not content generation
- Focus on contract compliance: MCP Message format and protocol requirements

## Future Architectural Decisions

This specification will require new ADRs to be created during implementation:

### Expected ADRs
1. **Prompt Implementation Pattern**: Similar to ADR-007 for tools
   - Function signature standards
   - Content generation approach
   - Error handling patterns
   - Testing standards

2. **Content Generation Strategy**: 
   - Static vs dynamic content approaches
   - Template systems and formatting
   - Performance considerations
   - Maintenance workflows

3. **Prompt Naming Convention**: Extension of ADR-019
   - Naming pattern for prompts
   - Consistency with existing conventions
   - Discoverability considerations

## Success Criteria

**✅ Prompts Capability Complete When:**

- [ ] Prompts capability architecture defined and documented
- [ ] `list_mcp_assets` prompt implemented and functional
- [ ] Prompt registration integrated with FastMCP server
- [ ] Dynamic tool discovery working across all services
- [ ] Content accurately reflects current server capabilities
- [ ] Testing strategy implemented and passing
- [ ] MCP client integration verified
- [ ] Relevant ADRs created and documented

## Benefits

### For AI Assistants
- **Self-Discovery**: Understand server capabilities without prior knowledge
- **Context Awareness**: Get relevant information about available operations
- **Usage Guidance**: Learn proper patterns and workflows

### For Users
- **Reduced Learning Curve**: Easier to understand what server can do
- **Better Experience**: Clear guidance and examples for common tasks
- **Self-Service**: Less need for external documentation

### For Maintainers
- **Self-Documenting**: Server capabilities automatically documented
- **Consistency**: Standardized way to communicate capabilities
- **Extensibility**: Framework for adding more guided interactions

## Integration with Existing Services

### Health Check Enhancement
The `list_mcp_assets` prompt can include real-time server health information to provide current status context.

### Tool Discovery
Prompt content should dynamically reflect all registered tools from:
- Foundation (health_check)
- Partition Service
- Entitlements Service  
- Legal Service
- Schema Service
- Storage Service

### Configuration Integration
Leverage existing ConfigManager to provide accurate setup guidance based on current configuration patterns.

## References

- [Model Context Protocol Prompts Specification](https://modelcontextprotocol.io/specification/#prompts)
- [Project Architecture](../docs/project-architect.md)
- [Architecture Decision Records](../docs/adr.md)
- [ADR-007: Tool Implementation Pattern](../docs/adr/007-tool-implementation-pattern.md)
- [ADR-010: Testing Philosophy](../docs/adr/010-testing-philosophy-and-strategy.md)