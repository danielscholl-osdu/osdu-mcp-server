# GitHub Copilot Instructions for OSDU MCP Server

This is a Python-based Model Context Protocol (MCP) server that provides AI assistants with access to OSDU platform capabilities. The project follows an AI-driven development workflow with strict architectural patterns.

## Project Overview

OSDU MCP Server enables AI assistants to interact with the Open Subsurface Data Universe (OSDU) platform. It provides tools for managing partitions, legal tags, schemas, and storage records with built-in safety features.

## Code Standards

### Required Before Each Commit
Run these commands to ensure code quality:
```bash
uv run mypy .           # Type checking (must pass)
uv run flake8 src/      # Linting (must pass)
uv run black src/ tests/ # Format code
uv run pytest           # All tests must pass (80% coverage minimum)
```

### Development Flow
- Setup: `uv sync && uv pip install -e .[dev]`
- Test: `uv run pytest`
- Type check: `uv run mypy .`
- Format: `uv run black src/ tests/`
- Full check: `uv run mypy . && uv run flake8 src/ && uv run pytest`

## Repository Structure
- `src/osdu_mcp_server/`: Main package
  - `shared/`: Core infrastructure (auth, config, clients)
  - `tools/`: MCP tool implementations (one file per tool)
  - `server.py`: FastMCP server configuration
- `tests/`: Test suite mirroring src structure
- `docs/adr/`: Architectural Decision Records (MUST read before major changes)
- `specs/`: Service specifications

## Key Architectural Patterns

1. **Tool Naming**: Use `{resource}_{action}` format (e.g., `partition_get`, `storage_create_update_records`)
2. **Service Clients**: All service clients inherit from `OsduClient` (see `shared/clients/`)
3. **Error Handling**: Use `@handle_osdu_exceptions` decorator on all tools
4. **Write Protection**: Destructive operations require environment variables:
   - `OSDU_MCP_ENABLE_WRITE_MODE=true` for create/update
   - `OSDU_MCP_ENABLE_DELETE_MODE=true` for delete/purge
5. **Testing**: Write behavior-driven tests (test what users see, not implementation)

## Guidelines for Changes

### When Adding New Tools
1. Follow the existing pattern in `src/osdu_mcp_server/tools/`
2. Use the standard tool structure with `@handle_osdu_exceptions`
3. Add comprehensive docstrings with Args/Returns sections
4. Implement write protection for destructive operations
5. Write behavior-driven tests with >80% coverage

### When Modifying Architecture
1. Check relevant ADRs in `docs/adr/` first
2. If changing patterns, create or update an ADR
3. Update AI_EVOLUTION.md with lessons learned
4. Ensure all existing tests still pass

### Commit Message Format
Use Conventional Commits for Release Please automation:
- `feat:` New feature (minor version)
- `fix:` Bug fix (patch version)
- `chore:` Maintenance (no version change)
- `docs:` Documentation only
- `test:` Test improvements

### Issue Creation and Labels
When creating GitHub issues, apply appropriate labels from these categories:
1. **Type** (required): bug, enhancement, documentation, refactor, cleanup, testing, security, performance
2. **Priority**: high-priority, medium-priority, low-priority
3. **Service**: service:partition, service:legal, service:schema, service:storage, service:entitlements
4. **Component**: configuration, dependencies, github_actions, code-quality, ADR
5. **Status**: needs-triage, blocked, breaking-change, help wanted, good first issue

Example: `gh issue create -l "bug,service:storage,high-priority"`
See `docs/label-strategy.md` for complete guidelines.

## Important Context

- This project uses DefaultAzureCredential for authentication (ADR-002)
- All async operations use aiohttp with connection pooling
- The project follows a phased development approach
- Security by default: write operations are disabled unless explicitly enabled
- Check CONTRIBUTING.md for the full AI-driven workflow

## Testing Requirements

- Minimum 80% test coverage required
- Tests should be behavior-driven (ADR-010)
- Mock at service boundaries only (HTTP calls, auth)
- Use `aioresponses` for HTTP mocking
- Run `uv run pytest` to execute all tests

## Common Tasks Suitable for Copilot

- Adding new tools following existing patterns
- Improving test coverage
- Fixing type errors reported by mypy
- Updating documentation
- Adding validation for edge cases
- Improving error messages

## Tasks to Avoid Assigning to Copilot

- Major architectural changes
- Security-related modifications
- Changes to authentication flow
- Cross-service refactoring
- Initial service client implementations