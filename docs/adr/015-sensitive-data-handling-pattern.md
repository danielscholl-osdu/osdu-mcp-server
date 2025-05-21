# ADR-015: Sensitive Data Handling Pattern

## Status
**Accepted** - 2025-05-17

## Context
Partition properties contain sensitive information (credentials, keys) that need careful handling to prevent security breaches.

## Decision
Implement a three-tier sensitive data protection model:
1. **Exclude**: Don't return sensitive properties (default when `include_sensitive=false`)
2. **Redact**: Return properties with `<REDACTED>` values (default when `include_sensitive=true`)
3. **Expose**: Return actual values (only when `include_sensitive=true, redact_sensitive_values=false`)

## Implementation
```python
if is_sensitive:
    if not include_sensitive:
        continue  # Exclude
    
    if redact_sensitive_values:
        processed_properties[key] = {
            "sensitive": True,
            "value": "<REDACTED>"
        }
    else:
        processed_properties[key] = prop  # Expose
        sensitive_accessed.append(key)  # Audit log
```

## Rationale
1. **Security by Default**: Sensitive data excluded/redacted by default
2. **Flexibility**: Multiple levels of access control
3. **Audit Trail**: Log sensitive data access
4. **Clear Intent**: Explicit parameters for accessing sensitive data

## Consequences
**Positive:**
- Strong security defaults
- Flexible access control
- Audit compliance
- Clear API contract

**Negative:**
- More complex parameter handling
- Multiple code paths to test