# AI Evolution Log

This document tracks the project's evolution in a way that helps AI assistants understand not just what changed, but the context, reasoning, and lessons learned. It complements the CHANGELOG.md with deeper insights.

## Project Genesis

**Context**: OSDU (Open Subsurface Data Universe) is an oil & gas industry data platform. This MCP server makes OSDU accessible to AI assistants.

**Initial Challenge**: How to adapt CLI patterns (session-based, user-interactive) to MCP's headless, long-running service model?

**Key Insight**: Study the CLI for proven patterns but build independently for MCP's unique requirements.

## Architectural Evolution

### Phase 1: Foundation (Health Check)
- **Goal**: Prove connectivity and establish patterns
- **Lesson**: DefaultAzureCredential "just works" across environments when configured properly
- **Pattern**: Every tool follows the same structure: config → auth → client → operation → cleanup

### Phase 2: Read Operations (Partition, Legal, Schema, Storage GET)
- **Goal**: Safe exploration of OSDU data
- **Lesson**: OSDU APIs are inconsistent (Legal uses v1, others use v2)
- **Pattern**: Service-specific clients inherit from OsduClient to handle quirks

### Phase 3: Write Protection (ADR-014)
- **Goal**: Prevent accidental data modification
- **Challenge**: How to make destructive operations safe by default?
- **Solution**: Environment variable gates with clear error messages
- **Evolution**: Later split into dual model (ADR-020) for granular control

### Phase 4: Data Validation (ADR-021)
- **Goal**: Fail fast with helpful errors
- **Lesson**: Client-side validation saves API calls and improves UX
- **Pattern**: Validate structure → validate content → validate permissions

### Phase 5: Audit & Compliance (ADR-023)
- **Goal**: Enterprise-ready logging for governance
- **Innovation**: Risk-based log levels (INFO for reads, WARNING for deletes)
- **Benefit**: Structured logs enable compliance reporting

### Phase 6: Prompts Capability (ADR-024, ADR-025, ADR-026)
- **Goal**: Self-documenting server capabilities for AI assistants
- **Challenge**: How to keep discovery content current as capabilities evolve?
- **Solution**: Static content generation with maintenance patterns
- **Critical Lesson**: Prompts require active maintenance when adding services/tools

## Key Decisions & Their Rationale

1. **FastMCP over raw MCP**: 70% less boilerplate, worth the framework lock-in
2. **Async everywhere**: MCP is naturally async, fighting it causes problems
3. **Behavior-driven tests**: Test what users see, not how it's implemented
4. **Dual permission model**: Creating data is different risk than destroying it

## Patterns for Future Features

When adding new OSDU services:
1. Check if the API version differs from v2 (like Legal's v1)
2. Create a service-specific client inheriting from OsduClient
3. Follow the tool naming convention: `{resource}_{action}`
4. Add write protection for any destructive operations
5. Include structured logging with operation metadata
6. **Update AssetsGenerator**: Add new tools to `_generate_tools_section()` in `shared/assets_generator.py`

## Current State & Next Steps

The server now covers core OSDU services with comprehensive safety features. Future additions should maintain the established patterns while considering:
- Batch operations for performance
- Caching for frequently accessed data
- Natural language interfaces for complex queries
- Cross-service operations (e.g., validate record against schema)

### Multi-AI Collaboration

The project is now optimized for multiple AI assistants:
- **Claude Code**: Primary development with deep architectural understanding
- **GitHub Copilot**: Task-specific development following established patterns
- **Shared Context**: Common patterns documented in both CLAUDE.md and copilot-instructions.md
- **Unified Standards**: All AI assistants follow the same quality checks and testing requirements

This multi-AI approach enables:
- Parallel development on different features
- Specialized AI capabilities (Claude for architecture, Copilot for implementation)
- Consistent code quality regardless of which AI contributes

## Lessons for AI Assistants

1. **Always check ADRs**: They explain the "why" behind patterns
2. **Test behavior, not implementation**: Follow ADR-010
3. **Security by default**: Write operations need explicit enablement
4. **Logs tell stories**: Use structured logging to help future debugging
5. **Patterns > Code**: Understanding patterns helps more than memorizing code

---

## How to Update This Document

Update AI_EVOLUTION.md when:
- Completing a major feature or phase
- Discovering a new pattern that will be reused
- Learning something that changes your approach
- Solving a particularly challenging problem

Example entry format:

```markdown
### Phase X: Feature Name (Date)
- **Goal**: What we set out to achieve
- **Challenge**: What made it difficult
- **Solution**: How we solved it
- **Pattern**: Any reusable pattern that emerged
- **Lesson**: What future developers/AI should know
```

_This document should be updated as part of step 5 in the contribution workflow (Architecture & Documentation Validation)._