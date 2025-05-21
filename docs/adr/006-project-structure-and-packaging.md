# ADR-006: Project Structure and Packaging

## Status
**Accepted** - 2025-05-15

## Context
The project needs a clear structure that supports development, testing, packaging, and deployment. The structure should be familiar to Python developers and support the planned multi-phase development approach.

## Decision
Use **standard Python package structure** with src layout and clear separation of concerns.

## Rationale
1. **Standard Convention**: Follows Python packaging best practices
2. **Clear Separation**: Shared infrastructure separate from tools
3. **Easy Testing**: Test modules mirror source structure
4. **Scalable**: Easy to add new tools and phases
5. **Tool Ecosystem**: Works well with modern Python tools (uv, pytest, etc.)

## Alternatives Considered
1. **Flat Structure**
   - **Pros**: Simple for small projects
   - **Cons**: Becomes unmaintainable as project grows
   - **Decision**: Won't scale for multi-phase development

2. **Microservice Structure** (separate repos)
   - **Pros**: Independent deployment, technology choices
   - **Cons**: Coordination overhead, shared code issues
   - **Decision**: Overkill for current scope

3. **Monorepo with Multiple Packages**
   - **Pros**: Shared tooling, easy refactoring across packages
   - **Cons**: Complex build system, unclear boundaries
   - **Decision**: Unnecessary complexity for current size

## Consequences
**Positive:**
- Familiar structure for Python developers
- Clear module boundaries
- Easy to navigate and understand
- Supports automatic discovery patterns

**Negative:**
- Some boilerplate with __init__.py files
- Need discipline to maintain clean boundaries
- Import paths can be verbose

## Implementation Notes
```
osdu_mcp_server/
├── src/osdu_mcp_server/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI entry point
│   ├── server.py                # FastMCP server
│   ├── shared/                  # Shared infrastructure
│   │   ├── config_manager.py
│   │   ├── auth_handler.py
│   │   └── osdu_client.py
│   └── tools/                   # MCP tools
│       └── health_check.py
├── tests/                       # Mirror source structure
│   ├── test_health_check.py
│   └── shared/
└── pyproject.toml              # Modern Python packaging
```

## Package Management
- Use `uv` for dependency management
- `pyproject.toml` for modern Python packaging
- Clear separation of development and runtime dependencies

## Success Criteria
- Easy to add new tools without structural changes
- Clear import paths and module boundaries
- Standard Python tooling works without issues
- New developers can navigate structure intuitively