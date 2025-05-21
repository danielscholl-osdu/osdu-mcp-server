# ADR-019: Tool Naming Convention

## Status
**Accepted** - 2025-05-19

## Context
During Phase 2 development, tool naming patterns became inconsistent across services:
- Partition service: `list_partitions`, `get_partition`, `create_partition`
- Legal service: `list_legal_tags`, `get_legal_tag`, `create_legal_tag`
- Entitlements service: `get_my_groups`

This inconsistency creates several problems:
1. **Poor discoverability** - Related tools don't group together in autocomplete
2. **Cognitive overhead** - Different naming patterns to remember per service
3. **AI friction** - Inconsistent patterns make it harder for AI assistants to discover and suggest tools

## Decision
Adopt a consistent `resource_action` naming convention for all MCP tools:

### Naming Pattern
- Format: `{resource}_{action}`
- Resource names are singular (`partition` not `partitions`)
- Compound resources become single words (`legaltag` not `legal_tag`)
- User-centric operations use `_mine` suffix

### File Structure
```
tools/
├── partition/
│   ├── list.py       # partition_list()
│   ├── get.py        # partition_get()
│   └── create.py     # partition_create()
├── legal/
│   ├── list.py       # legaltag_list()
│   ├── get.py        # legaltag_get()
│   └── create.py     # legaltag_create()
└── entitlements/
    └── mine.py       # entitlements_mine()
```

## Consequences

### Positive
- **Consistent namespace**: All tools follow the same pattern
- **Better autocomplete**: Related tools group together (e.g., `partition_*`)
- **AI-friendly**: Predictable patterns improve discoverability
- **Intuitive**: Resource-first thinking aligns with user mental models
- **Simplified imports**: Cleaner file organization

### Negative
- **Migration effort**: All existing tools need renaming
- **Documentation updates**: All references must be updated
- **Test updates**: Test files and functions need renaming

### Migration Strategy
Since we're in development phase with no production users:
1. Direct cutover without backward compatibility
2. Update all tools in a single commit
3. Update documentation and tests simultaneously
4. No deprecation period needed

## Implementation
The refactoring includes:
1. Renaming 14 tool files across 3 services
2. Updating function names to match new pattern
3. Updating all imports in server.py
4. Updating test files and test function names
5. Updating README and all documentation
6. Updating related ADRs with new examples

This decision significantly improves the developer experience and AI assistant integration while establishing a pattern that scales well for future services.