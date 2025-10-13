# ADR Catalog 

Optimized ADR Index for Agent Context

## Index

| id  | title                               | status | details |
| --- | ----------------------------------- | ------ | ------- |
| 001 | MCP Framework Selection             | acc    | [ADR-001](001-mcp-framework-selection.md) |
| 002 | Authentication Strategy             | acc    | [ADR-002](002-authentication-strategy.md) |
| 003 | Configuration Mgmt Approach         | acc    | [ADR-003](003-configuration-management-approach.md) |
| 004 | Error Handling Architecture         | acc    | [ADR-004](004-error-handling-architecture.md) |
| 005 | HTTP Client Implementation          | acc    | [ADR-005](005-http-client-implementation.md) |
| 006 | Project Structure & Packaging       | acc    | [ADR-006](006-project-structure-and-packaging.md) |
| 007 | Tool Implementation Pattern         | acc    | [ADR-007](007-tool-implementation-pattern.md) |
| 008 | Async‑First Design                  | acc    | [ADR-008](008-async-first-design.md) |
| 009 | Service URL Management              | acc    | [ADR-009](009-service-url-management.md) |
| 010 | Testing Philosophy & Strategy       | acc    | [ADR-010](010-testing-philosophy-and-strategy.md) |
| 011 | OAuth Scope Simplification          | acc    | [ADR-011](011-oauth-scope-simplification.md) |
| 012 | Multi‑Provider Auth Architecture    | acc    | [ADR-012](012-multi-provider-authentication-architecture.md) |
| 013 | Service Client Architecture Pattern | acc    | [ADR-013](013-service-client-architecture-pattern.md) |
| 014 | Write Protection Pattern            | acc    | [ADR-014](014-write-protection-pattern.md) |
| 015 | Sensitive Data Handling Pattern     | acc    | [ADR-015](015-sensitive-data-handling-pattern.md) |
| 016 | Structured Logging & Observability  | acc    | [ADR-016](016-structured-logging-and-observability-pattern.md) |
| 017 | Non‑JSON Response Handling          | acc    | [ADR-017](017-non-json-response-handling.md) |
| 018 | Member Identifier Handling Pattern  | prop   | [ADR-018](018-member-identifier-handling-pattern.md) |
| 019 | Tool Naming Convention              | acc    | [ADR-019](019-tool-naming-convention.md) |
| 020 | Unified Write Protection w/ Dual Model | acc    | [ADR-020](020-unified-write-protection.md) |
| 021 | Record Validation Pattern           | acc    | [ADR-021](021-record-validation-pattern.md) |
| 022 | Confirmation Requirement Pattern    | acc    | [ADR-022](022-confirmation-requirement-pattern.md) |
| 023 | Enhanced Audit Logging Pattern      | acc    | [ADR-023](023-enhanced-audit-logging-pattern.md) |
| 024 | Prompt Implementation Pattern        | acc    | [ADR-024](024-prompt-implementation-pattern.md) |
| 025 | Prompt Naming Convention             | acc    | [ADR-025](025-prompt-naming-convention.md) |
| 026 | Content Generation Strategy          | acc    | [ADR-026](026-content-generation-strategy.md) |
| 027 | MCP Resources Implementation Pattern | acc    | [ADR-027](027-mcp-resources-implementation-pattern.md) |
| 028 | Data Domain Configuration Pattern    | acc    | [ADR-028](028-data-domain-configuration-pattern.md) |
| 029 | Multi-Cloud Authentication          | acc    | [ADR-029](029-multi-cloud-authentication.md) |

---

## ADR Records

--------------------------------------------
```yaml
id: 001
title: MCP Framework Selection
status: accepted
date: 2025-05-15
decision: Use FastMCP framework to implement the MCP server.
why: |
• \~70 % less boilerplate than raw MCP
• Built‑in type safety & JSON‑RPC handling
• Familiar CLI‑style pattern
• Active community & docs
tradeoffs:
positive: \[fast-dev, fewer protocol bugs, auto validation]
negative: \[framework lock‑in, less low‑level control]
```

--------------------------------------------
```yaml
id: 002
title: Authentication Strategy
status: accepted
date: 2025-05-15
decision: Use Azure DefaultAzureCredential with configurable exclusions.
why: |
• Works across all Azure hosting scenarios
• Zero secrets in code, automatic refresh
• Mirrors proven CLI chain
tradeoffs:
positive: \[unified auth, secure, future‑proof]
negative: \[Azure‑specific, order awareness]
```
--------------------------------------------
```yaml
id: 003
title: Configuration Management Approach
status: accepted
date: 2025-05-15
decision: Environment‑first config with YAML fallback.
why: |
• Easy overrides in cloud/container
• Secure handling of secrets
• Mirrors CLI behaviour
tradeoffs:
positive: \[flexible, debuggable, secure]
negative: \[two layers to manage, verbose env vars]
```
---------------------------------------------------

-------------------------------------------
```yaml
id: 004
title: Error Handling Architecture
status: accepted
date: 2025-05-15
decision: Structured error hierarchy + decorator handling.
why: |
• Consistent JSON error shape for AI
• Actionable messages, no secrets
• Easy reuse across tools
updates: Add OSMCPValidationError for 400 validation faults.
tradeoffs:
positive: \[uniform UX, secure, extendable]
negative: \[decorator discipline, overhead]
```
-------------------------------------------

-------------------------------------------
```yaml
id: 005
title: HTTP Client Implementation
status: accepted
date: 2025-05-15
decision: aiohttp wrapper with pooling, retries, timeouts.
why: |
• Async‑native & efficient
• Mature, flexible library
• Re‑uses connections
tradeoffs:
positive: \[performance, reliability, async fit]
negative: \[extra dependency, session mgmt]
```
-------------------------------------------

-------------------------------------------
```yaml
id: 006
title: Project Structure & Packaging
status: accepted
date: 2025-05-15
decision: Standard src‑layout Python package.
why: |
• Follows packaging best practices
• Clear separation & test mirroring
• Easy for new devs
tradeoffs:
positive: \[familiar, scalable, tooling‑friendly]
negative: \[boilerplate, long import paths]
```
-------------------------------------------

--------------------------------------------------
```yaml
id: 007
title: Tool Implementation Pattern
status: accepted
date: 2025-05-15
decision: Pure async functions + decorators for x‑cutting concerns.
why: |
• Simple, testable, FastMCP‑aligned
• Low boilerplate, functional style
updates: Added resource cleanup & structured logging hooks.
tradeoffs:
positive: \[consistency, quick dev, easy tests]
negative: \[avoid hidden state, decorator opacity]
```
--------------------------------------------------

---------------------------------------------------
```yaml
id: 008
title: Async‑First Design
status: accepted
date: 2025-05-15
decision: End‑to‑end async/await throughout stack.
why: |
• Excellent I/O concurrency
• Scales without threads
• Matches MCP protocol
tradeoffs:
positive: \[resource‑efficient, scalable]
negative: \[debug complexity, async learning curve]
```
---------------------------------------------------

------------------------------------------
```yaml
id: 009
title: Service URL Management
status: accepted
date: 2025-05-16
decision: Enum + dict mapping for base URLs.
why: |
• Central management & type‑safe
• Easy to update versions
updates: Documented adding new services (Partition).
tradeoffs:
positive: \[no duplication, discoverable, testable]
negative: \[need update on version change]
```
------------------------------------------

---------------------------------------------------------
```yaml
id: 010
title: Testing Philosophy & Strategy
status: accepted
date: 2025-05-16
decision: Behaviour‑driven tests focusing on observable outputs.
why: |
• Maintains stability through refactors
• Easier to read & write
• Reduced mocking complexity
updates: Added patterns for write‑protection & sensitive‑data tests.
tradeoffs:
positive: \[robust, readable, fast]
negative: \[initial BDD learning, more integration tests]
```
---------------------------------------------------------

-------------------------------------------------
```yaml
id: 011
title: OAuth Scope Simplification
status: accepted
date: 2025-05-16
decision: Always use `{CLIENT_ID}/.default` scope; remove config.
why: |
• Eliminates JWT audience errors
• Simplifies user config
• Aligns with Azure best practice
tradeoffs:
positive: \[fewer errors, simpler docs]
negative: \[less flexible for non‑OSDU endpoints]
```
-------------------------------------------------

------------------------------------------
```yaml
id: 012
title: Multi‑Provider Authentication Architecture
status: accepted
date: 2025-05-16
decision: Auto‑detect provider via env vars with optional override.
why: |
• Zero config in most cases
• Mirrors CLI pattern
• Preps for AWS & GCP
tradeoffs:
positive: \[simple, extensible, minimal changes]
negative: \[code duplication per provider]
```
------------------------------------------

----------------------------------------------
```yaml
id: 013
title: Service Client Architecture Pattern
status: accepted
date: 2025-05-17
decision: Service‑specific clients inheriting from OsduClient.
why: |
• Code reuse of HTTP/auth layers
• Isolates service logic, headers
tradeoffs:
positive: \[consistent, low duplication]
negative: \[inheritance hierarchy to maintain]
```
----------------------------------------------

-----------------------------------------------
```yaml
id: 014
title: Write Protection Pattern
status: accepted
date: 2025-05-17
decision: Env var `OSDU_MCP_PARTITION_ALLOW_WRITE` gates destructive ops.
why: |
• Safety by default
• Explicit enablement for writes
tradeoffs:
positive: \[prevents data loss, audit‑friendly]
negative: \[extra config step, surprises users]
```
-----------------------------------------------

---------------------------------------------
```yaml
id: 015
title: Sensitive Data Handling Pattern
status: accepted
date: 2025-05-17
decision: Three‑tier exclude/redact/expose model for sensitive props.
why: |
• Security‑by‑default
• Flexible access levels
• Audit logging on expose
tradeoffs:
positive: \[strong security, compliance]
negative: \[param complexity, extra branches]
```
---------------------------------------------

------------------------------------
```yaml
id: 016
title: Structured Logging & Observability
status: accepted
date: 2025-05-17
decision: JSON logs with trace correlation & standard fields.
why: |
• Machine‑readable aggregation
• Security & auditability
tradeoffs:
positive: \[easy analysis, tracing, compliance]
negative: \[verbosity, storage cost]
```
------------------------------------

------------------------------------
```yaml
id: 017
title: Non‑JSON Response Handling
status: accepted
date: 2025-05-17
decision: Wrap plain‑text responses into JSON `{response: <text>}`.
why: |
• Robust against OSDU plain‑text errors
• Consistent downstream handling
tradeoffs:
positive: \[graceful errors, debugging]
negative: \[masks content‑type differences]
```

------------------------------------
```yaml
id: 018
title: Member Identifier Handling Pattern
status: proposed
date: 2025-05-17
decision: Auto‑detect member ID format (email vs OID) with format utilities.
why: |
• Different providers use different formats
• Transparent handling for AI assistants
• No user configuration needed
implementation: |
• Detect email by @ character
• Detect OID by UUID v4 pattern
• Return format in responses
tradeoffs:
positive: \[seamless multi‑format, future‑proof]
negative: \[detection complexity, false positives]
```

-------------------------------------------
\\

-------------------------------------------
```yaml
id: 019
title: Tool Naming Convention
status: accepted
date: 2025-05-19
decision: Adopt resource_action naming pattern for all MCP tools.
why: |
• Inconsistent naming across services created friction
• Poor autocomplete and AI discoverability
• Mixed verb-object patterns confused users
implementation: |
• Format: {resource}_{action}
• Singular resources: partition, legaltag
• User-centric: entitlements_mine
• Direct cutover in development phase
impact: |
• 14 tools renamed across 3 services
• All documentation updated
• Tests and imports refactored
tradeoffs:
positive: [consistent namespace, better AI discovery, intuitive patterns]
negative: [migration effort, documentation churn]
```

-------------------------------------------
```yaml
id: 020
title: Unified Write Protection with Dual Permission Model
status: accepted
date: 2025-05-19
updated: 2025-05-20
decision: Use dual permission model with OSDU_MCP_ENABLE_WRITE_MODE and OSDU_MCP_ENABLE_DELETE_MODE.
why: |
• Separate controls for data modification vs destruction
• Enable data creation while preventing deletion
• Enhanced operational safety and governance
implementation: |
• OSDU_MCP_ENABLE_WRITE_MODE for create/update operations
• OSDU_MCP_ENABLE_DELETE_MODE for delete/purge operations
• Client-side permission checking methods
• Operation-specific error messages
impact: |
• Granular control over destructive operations
• Enhanced security through defense-in-depth
• Support for compliance requirements
tradeoffs:
positive: [enhanced safety, granular control, audit-friendly]
negative: [additional config complexity, dual variable management]
```

-------------------------------------------
```yaml
id: 021
title: Record Validation Pattern
status: accepted
date: 2025-05-20
decision: Implement comprehensive client-side record validation with descriptive error messages.
why: |
• Early error detection before expensive API calls
• Improved user experience with actionable guidance
• Ensure OSDU compliance requirements
implementation: |
• Required field validation (kind, acl, legal, data)
• Structural validation for ACL and legal objects
• Descriptive error messages with context
• Batch validation with record-specific errors
impact: |
• Reduced API failures due to validation errors
• Better user experience and development efficiency
• Enhanced data quality and compliance
tradeoffs:
positive: [early error detection, clear guidance, compliance]
negative: [client-side overhead, maintenance burden]
```

-------------------------------------------
```yaml
id: 022
title: Confirmation Requirement Pattern
status: accepted
date: 2025-05-20
decision: Require explicit confirmation for highly destructive operations via boolean parameter.
why: |
• Prevent accidental execution of irreversible operations
• Force explicit acknowledgment of destructive consequences
• Support audit trail and compliance requirements
implementation: |
• Boolean confirm parameter (must be explicitly true)
• Client-side validation before permission checks
• Clear error messages explaining consequences
• Applied to purge and cascading delete operations
impact: |
• Enhanced protection against accidental data loss
• Clear audit trail of intentional destructive actions
• Educational error messages for users
tradeoffs:
positive: [accident prevention, audit trail, user education]
negative: [parameter complexity, potential user friction]
```

-------------------------------------------
```yaml
id: 023
title: Enhanced Audit Logging Pattern
status: accepted
date: 2025-05-20
decision: Implement risk-based logging with operation-specific log levels and audit metadata.
why: |
• Support compliance and governance requirements
• Appropriate log levels based on operation risk
• Rich context for monitoring and incident response
implementation: |
• INFO for read operations, WARNING for delete, ERROR for purge
• Destructive and permanent operation indicators
• Standardized metadata fields across operations
• Success/failure logging with context
impact: |
• Enhanced compliance and audit capabilities
• Better operational visibility and monitoring
• Support for data governance requirements
tradeoffs:
positive: [compliance support, rich context, monitoring-friendly]
negative: [increased storage, processing overhead, complexity]
```

--------------------------------------------
```yaml
id: 024
title: Prompt Implementation Pattern
status: accepted
date: 2025-06-19
decision: Use pure async functions returning List[Message] with content generation via dedicated generator classes.
why: |
• MCP protocol compliance with proper Message format
• FastMCP alignment with function-based registration
• Testability of data provider vs. consumer
• Separation of concerns between prompt logic and content generation
• Consistency with tool patterns while serving unique purpose
implementation: |
• Function signature: async def prompt_name() -> List[Message]
• Message structure: [{"role": "user", "content": "..."}]
• Generator classes for content creation
• Registration via mcp.prompt() decorator
tradeoffs:
positive: [MCP compliance, clear separation, testable, maintainable]
negative: [additional generator classes, two-layer architecture]
```

--------------------------------------------
```yaml
id: 025
title: Prompt Naming Convention
status: accepted
date: 2025-06-19
decision: Use descriptive naming for prompts that clearly indicates their discovery and guidance purpose.
why: |
• Different purpose from tools (content delivery vs. actions)
• User mental model of prompts as assistance not operations
• Clear distinction improves discoverability
• Future-proof for various prompt types
implementation: |
• Discovery prompts: {verb}_{subject} (list_mcp_assets)
• Guidance prompts: {verb}_{context} (guide_data_ingestion)
• Interactive prompts: {action}_{workflow} (create_legal_tag_wizard)
• Descriptive over resource-action pattern
tradeoffs:
positive: [clear distinction, purpose-driven, extensible, natural language]
negative: [learning curve, consistency overhead, documentation needs]
```

--------------------------------------------
```yaml
id: 026
title: Content Generation Strategy
status: accepted
date: 2025-06-19
decision: Use static content generation with dynamic elements via dedicated generator classes.
why: |
• Hybrid approach balances accuracy with performance
• Static content ensures comprehensive coverage
• Dynamic elements reflect current server state
• Generator classes provide clear organization
• Template-based approach ensures consistency
implementation: |
• AssetsGenerator class with section-based methods
• Static template content for stable information
• Dynamic discovery for current capabilities (future)
• Error handling with graceful degradation
• Performance target: <500ms generation, 5-10KB content
tradeoffs:
positive: [accuracy, performance, maintainable, consistent, extensible]
negative: [maintenance overhead, code-based content, generator complexity]
```

--------------------------------------------
```yaml
id: 027
title: MCP Resources Implementation Pattern
status: accepted
date: 2025-06-19
decision: Implement file-based MCP Resources using JSON templates with structured discovery and validation patterns.
why: |
• Working templates eliminate format-guessing errors in OSDU workflows
• Template-driven approach transforms error-prone trial-and-error into reliable execution
• MCP protocol compliance using standard Resources capability
• JSON files are maintainable and easy to update
implementation: |
• Directory structure: templates/ for working examples, references/ for guidance
• Resource registration with get_workflow_resources() function
• FastMCP integration with automatic resource discovery
• Template validation against OSDU API requirements
impact: |
• Dramatic reduction in OSDU format-guessing errors
• Reliable template-driven workflow execution
• Enhanced AI assistant discoverability and usability
tradeoffs:
positive: [error elimination, workflow reliability, AI-friendly, maintainable, extensible]
negative: [template maintenance, file management, validation overhead, discovery complexity]
```

--------------------------------------------
```yaml
id: 028
title: Data Domain Configuration Pattern
status: accepted
date: 2025-06-19
decision: Implement environment-variable based data domain configuration with sensible defaults and clear domain-to-deployment mapping.
why: |
• OSDU ACLs require deployment-specific data domain identifiers
• Different deployments use different domains (contoso.com, dataservices.energy)
• Eliminates ACL format errors caused by incorrect domains
• Provides environment flexibility with convenient defaults
implementation: |
• OSDU_MCP_SERVER_DOMAIN environment variable
• Default: contoso.com (Standard OSDU)
• Clear deployment-to-domain mapping documentation
• Template domain injection at runtime
impact: |
• Eliminates domain-related ACL validation failures
• Environment portability across OSDU deployments
• Consistent domain usage across all tools and resources
tradeoffs:
positive: [ACL accuracy, deployment flexibility, error reduction, clear mapping]
negative: [configuration requirement, documentation burden, template complexity]
```

--------------------------------------------
```yaml
id: 029
title: Multi-Cloud Authentication
status: accepted
date: 2025-01-13
decision: Native multi-cloud authentication with AWS boto3, GCP ADC, and manual OAuth token support.
why: |
• Enable AWS and GCP users with first-class authentication
• Provide fallback for custom OAuth providers
• Maintain seamless developer experience across clouds
• Zero breaking changes to existing tools
implementation: |
• USER_TOKEN mode for manual OAuth tokens (highest priority)
• AWS mode with boto3 SDK credential chain
• GCP mode with Application Default Credentials
• Priority-based automatic detection
• JWT validation for manual tokens
• Native SDK integration for token refresh
impact: |
• AWS/GCP users get same experience as Azure users
• Custom OAuth providers supported via manual tokens
• Zero changes to any of 31 MCP tools
• Comprehensive test coverage for all modes
tradeoffs:
positive: [multi-cloud support, auto-discovery, zero API changes, native SDKs]
negative: [dependency growth, testing complexity, support burden]
```