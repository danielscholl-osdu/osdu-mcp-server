# CLAUDE.md

This file guides AI assistants working with the OSDU MCP Server codebase.

## Project Context

OSDU MCP Server provides Model Context Protocol access to the OSDU platform. It adapts proven patterns from the OSDU CLI while being optimized for MCP's headless, long-running service model.

## AI-Driven Development Workflow

This project follows an AI-agent driven workflow. See @CONTRIBUTING.md for the full process.

Key principles:
- Architecture first: ADRs define decisions, specs define behavior
- Test-driven: Minimum 80% coverage, behavior-focused tests (ADR-010)
- Incremental: Build features phase by phase with validation

## Essential Commands

```bash
# Quality checks (run before committing)
uv run mypy . && uv run flake8 src/ && uv run pytest

# Individual commands
uv run pytest                    # Run all tests
uv run pytest -xvs              # Run tests, stop on first failure
uv run mypy .                   # Type checking
uv run flake8 src/              # Linting
uv run black src/ tests/        # Format code

# Git workflow
git checkout -b agent/<issue-number>-<description>
git commit -m "feat: add new feature"  # Conventional commits
gh pr create                           # Create pull request
```

## Key Architecture Patterns

1. **Tool Implementation**: See any file in `src/osdu_mcp_server/tools/` for the pattern
2. **Service Clients**: Inherit from OsduClient, see `shared/clients/`
3. **Error Handling**: Use @handle_osdu_exceptions decorator
4. **Write Protection**: Check ADR-020 for dual permission model
5. **Authentication**: DefaultAzureCredential with configurable exclusions (ADR-002)
6. **Prompt Maintenance**: When adding services/tools, update `AssetsGenerator._generate_tools_section()` in `shared/assets_generator.py`

## Core Documentation

- @CONTRIBUTING.md - AI-driven development workflow
- @docs/adr/README.md - Architectural decisions index
- @docs/project-architect.md - System architecture
- @CHANGELOG.md - Feature history with architectural context
- @AI_EVOLUTION.md - Project evolution story for AI understanding

## Development Guidelines

1. **Commits**: Use conventional commits (feat:, fix:, chore:, docs:, etc.)
2. **Branches**: `agent/<issue>-<description>` format
3. **Testing**: Write behavior-driven tests, not implementation tests
4. **Type Safety**: Fix all mypy errors before committing
5. **Documentation**: Update ADRs when architecture changes

## Issue Creation and Labels

When creating GitHub issues, follow the label strategy defined in @docs/label-strategy.md:

1. **Always include one Type label**: bug, enhancement, documentation, etc.
2. **Add Priority when clear**: high-priority, medium-priority, low-priority
3. **Add Component labels**: configuration, dependencies, etc. (when relevant)
4. **Status labels are optional**: needs-triage, blocked, breaking-change
5. **Always add claude label**: All issues created by Claude should include the `claude` label
6. **Add copilot label**: When the issue is suitable for GitHub Copilot implementation

Example issue creation:
```bash
gh issue create -t "Add retry logic to storage client" \
  -l "enhancement,medium-priority,claude,copilot" \
  -b "The storage client should retry failed requests..."
```

See @docs/label-strategy.md for complete label definitions and examples.

## Current Phase

The project is in active development. Check recent issues and ADRs to understand the current focus areas.

## Working with Other AI Assistants

- **GitHub Copilot**: See `.github/copilot-instructions.md` for GitHub Copilot coding agent guidance
- **Context Sharing**: Key patterns and guidelines are documented consistently across CLAUDE.md and copilot-instructions.md
- **Workflow Integration**: All AI assistants should follow the same architectural patterns and testing standards