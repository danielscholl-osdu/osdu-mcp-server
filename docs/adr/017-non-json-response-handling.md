# ADR-017: Non-JSON Response Handling

## Status
**Accepted** - 2025-05-17

## Context
OSDU services sometimes return plain text errors (e.g., 404 responses) instead of JSON, requiring graceful handling.

## Decision
Handle non-JSON responses by wrapping them in a standard JSON structure.

## Implementation
```python
try:
    return await response.json()
except Exception:
    # Handle non-JSON responses (e.g., plain text)
    text = await response.text()
    return {"response": text}
```

## Rationale
1. **Robustness**: Handle all response types
2. **Consistency**: Always return dict/JSON
3. **Debugging**: Preserve original response
4. **Compatibility**: Works with existing error handling

## Consequences
**Positive:**
- Graceful error handling
- Consistent response format
- Better debugging info

**Negative:**
- Hides response type differences
- May mask underlying issues