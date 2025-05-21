# ADR-007: Tool Implementation Pattern

## Status
**Accepted** - 2025-05-15

## Context
MCP tools need consistent implementation patterns that work well with FastMCP, provide good error handling, and are easy for developers to understand and extend. Tools will be added in phases, so the pattern must be scalable.

## Decision
Use **pure async functions** with decorators for cross-cutting concerns (error handling, logging).

## Rationale
1. **Simplicity**: Functions are easier to understand than classes
2. **FastMCP Compatibility**: Works naturally with FastMCP's function-based approach
3. **Testability**: Easy to unit test pure functions
4. **Composability**: Decorators add behavior without complexity
5. **Functional Style**: Matches async/await patterns well

## Alternatives Considered
1. **Class-Based Tools**
   - **Pros**: Encapsulation, state management, inheritance
   - **Cons**: More complex, less functional, harder to test
   - **Decision**: Overkill for stateless tool functions

2. **Tool Classes with Registry**
   - **Pros**: Advanced patterns, plugin architecture
   - **Cons**: Over-engineered, doesn't leverage FastMCP strengths
   - **Decision**: Unnecessary complexity

3. **No Pattern Enforcement**
   - **Pros**: Maximum flexibility
   - **Cons**: Inconsistent implementations, harder to maintain
   - **Decision**: Would lead to technical debt

## Consequences
**Positive:**
- Consistent tool implementations across phases
- Easy to test and reason about
- Minimal boilerplate per tool
- Decorators handle cross-cutting concerns

**Negative:**
- Need discipline to avoid stateful tools
- Some advanced patterns may require refactoring
- Decorator magic can be opaque to beginners

## Implementation Notes
```python
@handle_osdu_exceptions
async def health_check(
    include_services: bool = True,
    include_auth: bool = True,
    include_version_info: bool = False
) -> dict:
    """Check OSDU platform connectivity and service health."""
    
    # Initialize dependencies
    config = ConfigManager()
    auth = AuthHandler(config)
    client = OsduClient(config, auth)
    
    try:
        # Implementation logic
        result = await _perform_health_check(...)
        return result
    finally:
        # Cleanup
        await client.close()
```

## Tool Conventions
1. **Pure Functions**: No hidden state, predictable behavior
2. **Type Hints**: All parameters and return types annotated
3. **Docstrings**: Clear descriptions for AI assistant consumption
4. **Resource Cleanup**: Always clean up external resources
5. **Error Handling**: Use decorators for consistent error handling

## Updates
- Added resource cleanup & structured logging hooks

## Success Criteria
- All tools follow the same pattern
- New tools can be implemented quickly
- Testing tools is straightforward
- Documentation is automatically generated from function signatures