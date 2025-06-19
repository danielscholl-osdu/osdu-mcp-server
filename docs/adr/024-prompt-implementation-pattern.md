# ADR-024: Prompt Implementation Pattern

## Status
**Accepted** - 2025-06-19

## Context
MCP prompts are a distinct capability from tools, requiring their own implementation patterns. Prompts provide guided interaction and discovery content to AI assistants, returning formatted messages rather than data operations. They need consistent patterns that align with FastMCP, are testable, and follow the established architectural principles while serving their unique purpose of content delivery.

## Decision
Use **pure async functions** returning `List[Message]` with content generation via dedicated generator classes.

## Rationale
1. **MCP Protocol Compliance**: Returns proper `List[Message]` format as specified by MCP
2. **FastMCP Alignment**: Functions work naturally with `mcp.prompt()` registration
3. **Testability**: Easy to test data provider (function) vs. data consumer (AI model)
4. **Separation of Concerns**: Content generation isolated in dedicated generator classes
5. **Consistency**: Follows same async function pattern as tools (ADR-007)
6. **Maintainability**: Clear boundaries between prompt logic and content generation

## Implementation Pattern

### Function Signature
```python
async def prompt_name() -> List[Message]:
    """
    Prompt description explaining purpose and usage.
    
    Returns:
        List containing user message with comprehensive content
    """
    pass
```

### Message Structure
```python
# Return format - MCP Message protocol compliance
[
    {
        "role": "user",
        "content": "formatted_content_string"
    }
]
```

### Content Generation
```python
async def list_mcp_assets() -> List[Message]:
    """Example prompt implementation."""
    generator = AssetsGenerator()
    content = generator.generate_comprehensive_overview()
    
    return [{"role": "user", "content": content}]
```

### Registration Pattern
```python
# server.py
from .prompts import list_mcp_assets

mcp.prompt()(list_mcp_assets)  # type: ignore[arg-type]
```

## Content Generator Pattern

### Separation of Concerns
- **Prompt Function**: Orchestrates content generation and returns MCP-compliant format
- **Generator Class**: Handles content creation, formatting, and dynamic discovery
- **Clear Interface**: Generator provides specific methods for different content sections

### Generator Structure
```python
class AssetsGenerator:
    """Generate dynamic documentation for server capabilities."""
    
    def generate_comprehensive_overview(self) -> str:
        """Main content generation entry point."""
        pass
    
    def _generate_section_name(self) -> str:
        """Private methods for specific content sections."""
        pass
```

## Testing Strategy

### Focus Areas
1. **Message Format Testing**: Verify `List[Message]` structure compliance
2. **Function Contract Testing**: Ensure async execution and return types
3. **Content Generation Testing**: Verify content is generated without errors
4. **Integration Testing**: Confirm FastMCP registration works

### What NOT to Test
- **Content Quality**: Whether the content is "good" or "helpful"
- **AI Interpretation**: How models use the prompt content
- **Subjective Content**: Whether explanations make sense to humans

### Test Example
```python
@pytest.mark.asyncio
async def test_prompt_returns_proper_message_format():
    """Test prompt returns properly formatted MCP messages."""
    result = await list_mcp_assets()
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert isinstance(result[0]["content"], str)
    assert len(result[0]["content"]) > 0
```

## Alternatives Considered

1. **Class-Based Prompts**
   - **Pros**: Encapsulation, state management
   - **Cons**: Over-engineered for content delivery, doesn't match FastMCP patterns
   - **Decision**: Functions are sufficient for stateless content generation

2. **Inline Content Generation**
   - **Pros**: Simpler, all code in one place
   - **Cons**: Large prompt functions, harder to test content generation separately
   - **Decision**: Separation via generator classes improves maintainability

3. **Template-Based Content**
   - **Pros**: External templates, easy content updates
   - **Cons**: Additional dependencies, more complex for dynamic content
   - **Decision**: Python-based generation provides better dynamic capabilities

4. **Static Content Files**
   - **Pros**: Simple to maintain, version control friendly
   - **Cons**: Cannot reflect current server state, no dynamic discovery
   - **Decision**: Dynamic generation required for accurate server representation

## Consequences

**Positive:**
- Clear separation between prompt orchestration and content generation
- MCP protocol compliance ensured by consistent return format
- Easy to test prompt functions independently of content quality
- Generator classes provide reusable content creation patterns
- Consistent with existing tool patterns (ADR-007)
- Enables dynamic content that reflects current server state

**Negative:**
- Additional generator classes to maintain
- Two-layer architecture (prompt + generator) increases complexity slightly
- Content generation performance depends on generator implementation
- Requires discipline to keep prompt functions focused on orchestration

## Guidelines

### Prompt Function Responsibilities
- Parameter handling (if any)
- Generator instantiation and orchestration
- MCP Message format compliance
- Error handling for content generation failures

### Generator Class Responsibilities
- Content creation and formatting
- Dynamic server state discovery
- Section-based content organization
- Performance optimization for content generation

### Naming Patterns
- Prompt functions: Descriptive names reflecting purpose (see ADR-025)
- Generator classes: `{Purpose}Generator` pattern
- Content methods: `generate_{section}_section()` pattern

## Future Considerations

1. **Performance**: Content generation should complete within reasonable timeframes
2. **Caching**: Consider caching strategies for expensive content generation
3. **Extensibility**: Generator pattern supports future content types and formats
4. **Dynamic Discovery**: Framework supports automatic tool/capability discovery

## References
- [ADR-007: Tool Implementation Pattern](007-tool-implementation-pattern.md) - Similar patterns for tools
- [ADR-008: Async-First Design](008-async-first-design.md) - Async/await requirements
- [ADR-010: Testing Philosophy and Strategy](010-testing-philosophy-and-strategy.md) - Testing approach
- [Model Context Protocol Prompts Specification](https://modelcontextprotocol.io/specification/#prompts)