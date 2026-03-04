# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
AI Context: This changelog helps AI assistants understand the project's evolution.
Each entry includes not just what changed, but WHY it changed and what patterns emerged.
Key architectural decisions are linked to their ADRs.
-->

## [0.9.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.8.0...v0.9.0) (2026-02-17)


### Features

* Add custom OAuth scope support for v1.0 token OSDU environments ([d9c4cc2](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/d9c4cc27b683205c28483203b850f40622db96fc))
* add native multi-cloud authentication support (AWS, GCP, manual OAuth) ([ac43a79](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ac43a7989e0d260ee72d7ada41d454f5a90ff0b0))
* **auth:** add custom OAuth scope support for v1.0 token environments ([4d65ceb](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/4d65ceb2334d9a58d6857736f1aa1a7c153e3e0b)), closes [#108](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/108)


### Bug Fixes

* readme ([9d03614](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/9d036143b7395b9fd86009c6d1ef64c397d6d24f))

## [0.8.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.7.0...v0.8.0) (2025-06-20)


### Features

* enhance guide_record_lifecycle with interactive workflow and visual dashboards ([b641f0d](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/b641f0d0996668395c5949806c1c65262dcef91f))


### Bug Fixes

* add missing originator parameter to legaltag_create tool ([0d7b6d2](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/0d7b6d2bfc76886490a93096a14618e1b680332d))
* add missing originator parameter to legaltag_create tool ([f92e9d5](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/f92e9d5ecd74d82eb0b09a658a5d1f610ede0f69)), closes [#94](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/94)
* improve workflow interactivity with clear user decision points ([856d5b9](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/856d5b910011589ec2a2ec98ed59957d8546854d))
* **prompt:** remove timestamps and clarify safety assessment language ([a50e4ba](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/a50e4baf44d028337fb272d531a11efa30691ff3))

## [0.7.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.6.0...v0.7.0) (2025-06-19)


### Features

* implement comprehensive MCP prompts and resources with workflow guidance ([75e9167](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/75e91679ec1e050522c693b94d666548400d9ca4))


### Bug Fixes

* resolve CI quality check failures ([01bb2c6](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/01bb2c65af3d96b822cf45f16c71a4cfcfa67b6b))
* resolve code quality issues in MCP resources implementation ([353250c](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/353250ccbb501e6460a8559ab420127c30ad3c46))

## [0.6.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.5.0...v0.6.0) (2025-06-19)


### Features

* create comprehensive search service specification ([4ba76a7](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/4ba76a745635bfbd5d6b82afae32591874bb503a))
* implement Search Service with comprehensive Elasticsearch capabilities ([871e34b](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/871e34bd3b7d683b13a947550f6a85fed3c4a7ca))
* **prompts:** add comprehensive search patterns guidance ([4f85ba0](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/4f85ba0648834358cc8b5373656fb648fd39de64))
* **search:** implement core search tools with Elasticsearch support ([dd307a7](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/dd307a7deb63c66419dccfde6cb3167e4401f0c2))
* **search:** implement SearchClient with Elasticsearch integration ([634d7bb](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/634d7bbf15487c307b902337634ecd8b6ad5fb06))
* **server:** register search tools and prompt in MCP server ([5097fd0](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/5097fd0fe9837ed1641a26fe7848c22cbd4c8157))

## [0.5.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.4.0...v0.5.0) (2025-06-19)


### Features

* implement MCP prompts capability with asset discovery ([06815b9](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/06815b9a0c47ee0e62f6d2f974d98a054c859aa1))
* implement MCP prompts capability with asset discovery ([dd8049c](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/dd8049cdcbd2163dee66b49875db241a73da2438))


### Bug Fixes

* resolve code quality issues ([0aad5c6](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/0aad5c6111cffd30d4e2ab957d2ab4d1578ff56e))

## [0.4.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.3.0...v0.4.0) (2025-05-29)


### Features

* simplify Copilot issue template to minimal structure ([6abd665](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/6abd6651a0e84c4800e2f0edc52f8607804dbdcc))


### Bug Fixes

* **github:** update uv.lock automatically in Release Please workflow ([213c522](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/213c522d58a6139cee1e7a2f0ad928be84fcb52e))

## [0.3.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.2.0...v0.3.0) (2025-05-29)


### Features

* **github:** add automated labeling for AI agent assignments and issue creation ([0e89139](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/0e89139a7a2bd666968ce3e9dcfdd47c5370c58a))


### Bug Fixes

* **github:** improve Copilot assignment workflow feedback and documentation ([2172e22](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/2172e22d97f5d76b1a9b0789ae7663bc9650db5c))
* **github:** improve Copilot assignment workflow feedback and status clarity ([e6333e5](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/e6333e5cc8a6b54953cf896508a2b87b7ced1292))
* **github:** properly verify Copilot assignment success by checking issue state ([eba7d40](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/eba7d409a5a2ca6e5b8cd2685335dd20840307bd))
* **github:** remove non-functional Copilot assignment workflow ([3c7d958](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/3c7d958d4cd215b4932855bdddb61362ea994286))
* **github:** remove non-functional Copilot assignment workflow ([12e9fb1](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/12e9fb153fa8230f39e08b87fa5a59a3e073213e))

## [0.2.0](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.1.3...v0.2.0) (2025-05-24)


### Features

* configure release-please to only bump versions for source code changes ([5fb97bd](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/5fb97bde93b9e3466e800b73745ae471256b2999))
* configure release-please to only bump versions for source code changes ([4c6ad68](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/4c6ad684a6ced04c0031a2addbfa939dd2fbace7)), closes [#64](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/64)


### Bug Fixes

* **github:** Fix Copilot bot username case sensitivity in workflow ([ab57382](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ab57382a6e72839e72be7f3263acf9f2a528847f))
* **github:** Fix Copilot bot username case sensitivity in workflow ([a47b358](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/a47b358cca62e3677918d3bab427d7953633a061))
* prevent release-please infinite loop and improve config maintainability ([4bf2046](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/4bf2046a26efebb4c23000acb4712e93795e8d92))

## [0.1.4](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.1.3...v0.1.4) (2025-05-24)


### Bug Fixes

* **github:** Fix Copilot bot username case sensitivity in workflow ([ab57382](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ab57382a6e72839e72be7f3263acf9f2a528847f))
* **github:** Fix Copilot bot username case sensitivity in workflow ([a47b358](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/a47b358cca62e3677918d3bab427d7953633a061))


### Documentation

* add release badge to README ([f51f599](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/f51f599be772c6cb783e4f087ff5076140d1ff86))
* add release badge to README ([24f1c94](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/24f1c942b58b02d0e90ed8300b5d34971631874d))

## [0.1.3](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.1.2...v0.1.3) (2025-05-24)


### Bug Fixes

* **github:** Fix copilot-assign workflow 404 error ([02448cb](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/02448cb7494151fa1f4ae66bb777e4750d8881cc)), closes [#57](https://github.com/danielscholl-osdu/osdu-mcp-server/issues/57)

## [0.1.2](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.1.1...v0.1.2) (2025-05-23)


### Bug Fixes

* **github:** Fix Auto-Assign Copilot Workflow Error Handling ([ad30b3e](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/ad30b3eeb620e00cb725374dc91e99521381b999))

## [0.1.1](https://github.com/danielscholl-osdu/osdu-mcp-server/compare/v0.1.0...v0.1.1) (2025-05-23)


### Bug Fixes

* **github_actions:** add virtual environment setup to release workflow ([8b018b4](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/8b018b4ed27d5cb30727656b7189f5c9b57edbcc))
* **github_actions:** add virtual environment setup to release workflow ([330a901](https://github.com/danielscholl-osdu/osdu-mcp-server/commit/330a90160fae5ecf40abd283dc62d218ddf0c512))

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
