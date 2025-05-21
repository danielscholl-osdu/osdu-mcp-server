# Technical Debt Specification: Tool Naming Standardization

## Overview

This specification implements a standardized naming pattern for all MCP tools to improve consistency and discoverability across the OSDU MCP Server.

## Current State

### Tool Organization
```
tools/
├── partition/
│   ├── list_partitions.py
│   ├── get_partition.py
│   └── create_partition.py
├── legal/
│   ├── list_legal_tags.py
│   ├── get_legal_tag.py
│   └── create_legal_tag.py
└── entitlements/
    └── get_my_groups.py
```

### Tool Names
- `list_partitions`, `get_partition`, `create_partition`
- `list_legal_tags`, `get_legal_tag`, `create_legal_tag`
- `get_my_groups`

## New Pattern

### File Organization
```
tools/
├── partition/
│   ├── list.py
│   ├── get.py
│   └── create.py
├── legal/
│   ├── list.py
│   ├── get.py
│   └── create.py
└── entitlements/
    └── mine.py
```

### Tool Naming Convention
- `partition_list`, `partition_get`, `partition_create`
- `legaltag_list`, `legaltag_get`, `legaltag_create`  
- `entitlements_mine`

## Migration Requirements

### 1. Code Changes
- Rename 14 tool files following new pattern
- Update function names to match new pattern
- Update all imports in server.py
- Update all test files and imports
- Update all internal references

### 2. Documentation Updates
- Update README.md with new tool names
- Update partition-service-spec.md
- Update legal-service-spec.md
- Update entitlements-service-minimal-spec.md
- Add changelog notes to each updated spec

### 3. ADR Updates
> Ensure we update accordingly in both adr.md and adr-optimized.md
- Create ADR-019 documenting the naming convention
- Update ADR-006 (Project Structure) examples
- Update ADR-007 (Tool Implementation Pattern) guidance
- Update ADR-010 (Testing Philosophy) with test naming

### 4. Test Migration
```
# Current test structure
tests/tools/partition/test_list_partitions.py
tests/tools/legal/test_create_legal_tag.py

# New test structure  
tests/tools/partition/test_list.py
tests/tools/legal/test_create.py
```

## Validation Checklist

- [ ] All tests pass after migration
- [ ] No old tool names remain (grep verification)
- [ ] Documentation is consistent
- [ ] ADRs updated with new examples
- [ ] Manual testing of each tool confirms functionality

## Success Criteria

1. All 14 tools follow new naming pattern
2. All tests pass without modification
3. Documentation reflects new names consistently
4. No references to old names remain in codebase