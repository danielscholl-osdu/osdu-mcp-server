"""Search patterns guidance prompt."""

from typing import List, Dict, Any
from ..shared.exceptions import handle_osdu_exceptions
from ..shared.logging_manager import get_logger

# Define Message type for development/testing
Message = Dict[str, Any]

logger = get_logger(__name__)


@handle_osdu_exceptions
async def guide_search_patterns() -> List[Message]:
    """Provide search pattern guidance for OSDU operations.

    Returns:
        List[Message]: Search pattern guidance content
    """
    content = """# OSDU Search Patterns Guide

## Available Search Tools

- **search_query**: General search with Elasticsearch syntax
- **search_by_id**: Find specific records by ID
- **search_by_kind**: Find all records of specific type

## Quick Start Examples

### Text Search
```python
search_query(query="well*")
search_query(query="(well AND log)")
```

### Field Search
```python
search_query(query="data.UWI:\\"8690\\"")
search_query(query="data.Name:*test*")
search_query(query="data.SpudDate:[2020-01-01 TO 2023-12-31]")
```

### ID Search
```python
search_by_id(id="opendes:reference-data:12345")
```

### Kind Search
```python
search_by_kind(kind="*:osdu:well:*")
search_by_kind(kind="opendes:osdu:wellbore:1.0.0")
```

## Common Query Patterns

### Boolean Operators
- AND: `(data.A:\\"value1\\") AND (data.B:\\"value2\\")`
- OR: `data.Field:(\\"value1\\" OR \\"value2\\")`
- NOT: `data.Field:* AND NOT data.Field:\\"excluded\\"`

### Wildcards
- Single character: `data.Code:?00`
- Multiple characters: `data.Name:well*`
- Partial match: `data.Description:*offshore*`

### Range Queries
- Numeric: `data.Depth:[1000 TO 5000]`
- Date: `data.SpudDate:[2020-01-01 TO 2023-12-31]`
- Exclusive: `data.Value:{100 TO 200}`

### Common Fields
- `data.UWI` - Unique Well Identifier
- `data.WellID` - Well reference
- `data.Name` - Record name
- `data.SpudDate` - Well spud date
- `id` - Record identifier

## Multi-Step Workflows

1. **Explore Data**: Start with `search_by_kind(kind="*:*:*:*", limit=5)` to see available types
2. **Focus Search**: Use discovered kinds in targeted searches
3. **Field Discovery**: Examine results to find searchable field paths
4. **Refine Query**: Build specific field queries using discovered paths

## Performance Tips

- Use specific kinds instead of `*:*:*:*` when possible
- Add field prefixes (e.g., `data.`) for better performance
- Use reasonable limits to avoid timeouts
- Combine filters with AND/OR for precision

## Common Use Cases

### Find Wells by Area
```python
search_query(
    query="data.SpatialLocation.CountryID:\\"US\\"",
    kind="*:osdu:well:*"
)
```

### Find Recent Records
```python
search_query(
    query="createTime:[2024-01-01 TO *]",
    limit=20
)
```

### Discovery Workflow
```python
# Step 1: See what's available
search_by_kind(kind="*:*:*:*", limit=10)

# Step 2: Focus on specific type
search_by_kind(kind="*:osdu:wellbore:*", limit=50)

# Step 3: Search within that type
search_query(
    query="data.Name:*test*",
    kind="opendes:osdu:wellbore:1.0.0"
)
```"""

    logger.info(
        "Generated search patterns guidance",
        extra={"operation": "guide_search_patterns"},
    )

    return [{"role": "user", "content": content}]
