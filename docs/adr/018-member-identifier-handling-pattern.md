# ADR-018: Member Identifier Handling Pattern

## Status
**Proposed** - 2025-05-17

## Context
The Entitlements Service manages members that can be identified using different formats depending on the identity provider:
- **Email format**: `user@company.com` (common for users in most providers)
- **OID format**: `12345678-1234-1234-1234-123456789012` (Azure AD users and service principals)

The MCP tools need to handle both formats transparently without requiring users to understand the underlying complexity.

## Decision
Implement automatic member ID format detection with helper utilities for format identification and transparent handling across all Entitlements tools.

## Rationale
1. **Provider Flexibility**: Different cloud providers use different ID formats
2. **User Experience**: AI assistants shouldn't need to worry about ID formats
3. **Transparency**: Tools accept any valid format without configuration
4. **Maintainability**: Central pattern for ID handling

## Implementation
```python
import re
from enum import Enum

class MemberIdFormat(Enum):
    EMAIL = "email"
    OID = "oid" 
    UNKNOWN = "unknown"

def detect_member_format(member_id: str) -> MemberIdFormat:
    """Detect if member ID is email or OID format."""
    # Basic UUID v4 pattern
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    if re.match(uuid_pattern, member_id.lower()):
        return MemberIdFormat.OID
    elif "@" in member_id:
        return MemberIdFormat.EMAIL
    else:
        return MemberIdFormat.UNKNOWN

def format_member_response(member_id: str, member_type: str = None) -> dict:
    """Format member information for consistent responses."""
    format_type = detect_member_format(member_id)
    
    return {
        "id": member_id,
        "format": format_type.value,
        "type": member_type  # USER, SERVICE, etc.
    }
```

## Consequences
**Positive:**
- Seamless handling of different ID formats
- Consistent member representation in responses
- Future-proof for additional providers
- Clear format indication in responses

**Negative:**
- Additional complexity in member handling
- Must maintain format detection logic
- Potential for false positives in detection

## Testing Requirements
- Test both email and OID formats
- Test invalid formats
- Test mixed formats in same group
- Test format detection accuracy

## Success Criteria
- All tools handle both ID formats
- Clear format indication in responses
- No user configuration required
- Comprehensive test coverage