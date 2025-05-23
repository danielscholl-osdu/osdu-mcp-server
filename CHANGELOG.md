# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
AI Context: This changelog helps AI assistants understand the project's evolution.
Each entry includes not just what changed, but WHY it changed and what patterns emerged.
Key architectural decisions are linked to their ADRs.
-->

## 0.1.0 (2025-05-23)


### Features

* add comprehensive badges, Apache license, and enhance project documentation ([1806f0e](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/1806f0e56c0aae14bb4cb4307d767105fc20cca4))
* add GitHub label strategy and automated Copilot assignment ([3d299f4](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/3d299f470c982984e360e4eea305da988b8db890))
* add GitHub label strategy and automated Copilot assignment ([0e7d539](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/0e7d539dfb35f6a3c76bfd38b528c514759d05e8)), closes [#44](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/44)
* enable GitHub Copilot coding agent collaboration ([ce54775](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ce5477518382ff2b96cbaaa81c6d9279cf5ca687))
* enhance CI workflow to run all quality checks before failing ([eebfb55](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/eebfb55dc07ac04e412e57d6c252c61c9d89d30f))
* enhance CI workflow to show all quality check failures ([c19f3e7](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/c19f3e785bc1871a801fc4fbc750accee6304a62))
* enhance CI/CD pipeline and enable multi-AI collaboration ([81768dc](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/81768dc55f543a0b967ff268897d8bf5057a76c1))
* enhance CI/CD pipeline with comprehensive quality checks ([25d194f](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/25d194fac72e71a05d7bc3aa2d9e7c47c5d42b81))


### Bug Fixes

* Add issues:write permission to release workflow for label management ([12dd646](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/12dd646277f2ba5340a32951a1dad97890242bb4))
* Add missing blank lines between functions (E302) ([54cbd79](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/54cbd791adf29db5f05ad2f6ba97ab20033c588b))
* address PR review comments - remove service label references ([1b3c26a](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/1b3c26a85c9eeafba8c3b0b81afca869a98f524a))
* address Python 3.13 deprecation warnings ([ecfb326](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ecfb326294720d094efbd6e4f5ff3e53b0d791e2))
* address Python 3.13 deprecation warnings ([523a66e](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/523a66edd322a26d420084a487d89173cead61f8))
* Convert f-string without placeholders to regular string ([37e979b](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/37e979b40005a8d2f79d110b4d3b6e23593fc700))
* Convert f-string without placeholders to regular string (F541) ([1ebcdf5](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/1ebcdf5c9acb7ef335c685effc48dac0ba68737d))
* **deps:** add aioresponses to dev dependencies ([cdf4409](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/cdf44093d94ca0f545c025bc6ead5d67f49e9f5c))
* **lock/ci:** ensure pytest runs first and add uv.lock update ([90703f4](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/90703f457d2cb7638084be13e6193d5ec4af0b82))
* Remove trailing whitespace (W291) - 16 instances ([aa9e163](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/aa9e16333aa32afddf84345195843fd8bd092aae))
* Remove trailing whitespace from Python client code ([6e2fdd5](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/6e2fdd502fcf85d8db88e9d9631ae73e8af74456))
* Remove trailing whitespace from Python tool files ([dd30212](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/dd3021268a8408c87b53f491bc628b5fced3037c))
* Remove unused imports (F401) - 47 instances ([92d8ebd](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/92d8ebde8663f9692125c05842e4e2da3c4e1968))
* resolve flake8 W503 warnings and add W504 to ignore list ([5c54a92](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/5c54a92a02d1b4654a05ef15412ecb9b41f739a1)), closes [#35](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/35)
* resolve mypy type errors and update logging per ADR-023 ([f6de18c](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/f6de18c727d5e5683ea3d72643c9f8c427742bfc))
* **style:** add missing newlines at end of files (W292) ([7fb1a0f](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/7fb1a0f38dada13571726fa4349d9ad695cb04af))
* **style:** Add missing newlines at end of files (W292) ([cff411c](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/cff411c8b45484c3b2e96dd8d49f57b648ce72d7))


### Documentation

* add AI-aware changelog and streamline documentation ([199751e](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/199751e69865c86b64049c8275591985cd0a4e92))

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
