# ADR-008: Async-First Design

## Status
**Accepted** - 2025-05-15

## Context
The MCP server will handle multiple concurrent requests and needs to interact with external OSDU services efficiently. The design must handle I/O-bound operations without blocking and scale to handle reasonable load.

## Decision
Design the system with **async/await throughout** the stack.

## Rationale
1. **Natural Fit**: MCP protocol supports async operations
2. **I/O Efficiency**: Most operations are I/O-bound (HTTP calls to OSDU)
3. **Concurrency**: Handle multiple tool calls simultaneously
4. **Resource Efficiency**: Better resource utilization than threads
5. **Python Strength**: Python's async implementation is mature and efficient

## Alternatives Considered
1. **Synchronous Implementation**
   - **Pros**: Simpler to reason about, easier debugging
   - **Cons**: Blocks on I/O, poor concurrency, doesn't scale
   - **Decision**: Too limiting for production use

2. **Mixed Sync/Async**
   - **Pros**: Use sync where appropriate
   - **Cons**: Context switching overhead, complex error handling
   - **Decision**: Increases complexity without clear benefits

3. **Thread-Based Concurrency**
   - **Pros**: Familiar model for team
   - **Cons**: Thread overhead, GIL limitations, complex synchronization
   - **Decision**: Less efficient than async for I/O-bound work

## Consequences
**Positive:**
- Excellent I/O concurrency
- Efficient resource utilization
- Scales well with load
- FastMCP works naturally with async

**Negative:**
- All code must be async-aware
- Debugging can be more complex
- Learning curve for developers new to async
- Need to be careful about blocking operations

## Implementation Notes
```python
# All tools are async
async def health_check() -> dict:
    pass

# All infrastructure is async
class AuthHandler:
    async def get_access_token(self) -> str:
        pass

class OsduClient:
    async def get(self, path: str) -> dict:
        pass

# Main server loop is async
async def main():
    await mcp.run_async()
```

## Guidelines
1. **Never Block**: Use async versions of all I/O operations
2. **Propagate Async**: If function calls async, it must be async
3. **Use asyncio**: Leverage asyncio ecosystem for utilities
4. **Careful with CPU-bound**: Use thread pools for CPU-intensive work
5. **Proper Cleanup**: Use async context managers for resources

## Success Criteria
- Server handles multiple concurrent requests efficiently
- No blocking operations in main request path
- Good performance under load
- Clear async/await usage throughout codebase