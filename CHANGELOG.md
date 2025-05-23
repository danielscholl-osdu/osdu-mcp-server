# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
AI Context: This changelog helps AI assistants understand the project's evolution.
Each entry includes not just what changed, but WHY it changed and what patterns emerged.
Key architectural decisions are linked to their ADRs.
-->

## [Unreleased]

### Added
- Initial MCP server implementation with FastMCP framework (ADR-001)
- Health check tool for OSDU platform connectivity testing
- Partition service tools: list, get, create, update, delete (ADR-014, ADR-015)
- Legal tag service tools: full CRUD operations with compliance focus
- Schema service tools: list, get, search, create, update
- Storage service tools: complete record management capabilities
- Entitlements tool: get current user's groups and permissions
- Dual write protection model: separate controls for write vs delete operations (ADR-020)
- Enhanced audit logging for compliance and governance (ADR-023)

### Architecture Evolution
- **Authentication**: Implemented DefaultAzureCredential with configurable exclusions (ADR-002) - enables zero-config auth across all Azure hosting scenarios
- **Service Clients**: Established inheritance pattern from OsduClient (ADR-013) - reduces code duplication and ensures consistency
- **Error Handling**: Structured exception hierarchy with AI-friendly messages (ADR-004) - helps AI assistants provide better debugging guidance
- **Testing Philosophy**: Behavior-driven testing approach (ADR-010) - tests what users see, not implementation details

### Patterns Established
- **Tool Naming**: `{resource}_{action}` convention (ADR-019) - improves AI tool discovery
- **Write Protection**: Environment variables control destructive operations (ADR-014, ADR-020)
- **Validation**: Client-side validation before API calls (ADR-021)
- **Confirmation**: Explicit confirmation for destructive operations (ADR-022)

### Development Workflow
- AI-agent driven development process documented in CONTRIBUTING.md
- Conventional commits for Release Please automation
- GitHub Actions CI with comprehensive quality checks

## [0.1.0] - TBD

_This section will be auto-populated by Release Please when the first release is created._

---

<!-- 
AI Learning Notes:
- The project started with a focus on read operations and gradually added write capabilities
- Security and compliance features were added based on OSDU platform requirements
- The dual permission model emerged from the need to separate data modification from deletion
- Each service client follows the same pattern but has service-specific quirks (e.g., Legal API uses v1)
-->