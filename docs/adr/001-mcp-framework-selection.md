# ADR-001: MCP Framework Selection

## Status
**Accepted** - 2025-05-15

## Context
We need to implement an MCP (Model Context Protocol) server to expose OSDU functionality to AI assistants. The implementation must be reliable, maintainable, and allow for rapid development while ensuring protocol compliance.

## Decision
Use **FastMCP** framework for implementing the MCP server.

## Rationale
1. **Development Speed**: FastMCP reduces boilerplate code by ~70% compared to raw MCP implementation
2. **Type Safety**: Built-in type checking prevents runtime protocol errors
3. **Automatic Protocol Handling**: JSON-RPC conversion is handled automatically
4. **Proven Pattern**: Similar to CLI patterns our team is familiar with
5. **Community Support**: Active maintenance and good documentation

## Alternatives Considered
1. **Raw MCP Implementation**
   - **Pros**: Full control, no framework dependency
   - **Cons**: 3x development time, manual protocol handling, higher error potential
   - **Decision**: Rejected due to time constraints and complexity

2. **Custom Framework**
   - **Pros**: Tailored to our exact needs
   - **Cons**: Maintenance overhead, time to develop, testing burden
   - **Decision**: Rejected due to resource constraints

## Consequences
**Positive:**
- Faster initial development and feature additions
- Reduced protocol-level bugs
- Easy tool registration and management
- Automatic validation and error handling

**Negative:**
- Framework dependency introduces potential lock-in
- Less control over protocol-level optimizations
- Must adapt to framework's conventions

## Implementation Notes
```python
# Simple tool registration pattern
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OSDU MCP Server")

@mcp.tool()
async def health_check() -> dict:
    return {"status": "healthy"}
```

## Success Criteria
- Tool registration takes < 5 lines of code
- Protocol compliance verified through MCP test suite
- Development velocity 2x faster than estimated raw implementation