# ADR-021: Record Validation Pattern

## Status
**Accepted** - 2025-05-20

## Context
The Storage Service handles complex record structures with strict validation requirements for OSDU compliance. Records must contain specific required fields and follow specific structural patterns for access control lists (ACL) and legal compliance information.

Without comprehensive client-side validation, users receive cryptic API errors that are difficult to understand and resolve. This leads to poor user experience and increased support burden.

## Decision
Implement comprehensive client-side record validation with structured, descriptive error messages that guide users toward correct record structure.

## Implementation

### Validation Method Pattern
```python
def validate_record(self, record: Dict[str, Any]) -> None:
    """Validate basic record structure.
    
    Args:
        record: Record to validate
        
    Raises:
        OSMCPValidationError: If record validation fails with descriptive message
    """
    required_fields = ["kind", "acl", "legal", "data"]
    for field in required_fields:
        if field not in record:
            raise OSMCPValidationError(
                f"Missing required field '{field}' in record. Records must contain: {', '.join(required_fields)}"
            )
    
    # Validate ACL structure
    if "acl" in record:
        acl = record["acl"]
        if not isinstance(acl, dict):
            raise OSMCPValidationError(
                "ACL must be an object. Access control lists must be dictionary objects"
            )
        if "viewers" not in acl or "owners" not in acl:
            raise OSMCPValidationError(
                "ACL must contain both 'viewers' and 'owners' arrays. Access control lists define who can read and modify the record"
            )
        if not isinstance(acl["viewers"], list) or not isinstance(acl["owners"], list):
            raise OSMCPValidationError(
                "ACL viewers and owners must be arrays. Access control lists must contain arrays of group names"
            )
    
    # Validate Legal structure
    if "legal" in record:
        legal = record["legal"]
        if not isinstance(legal, dict):
            raise OSMCPValidationError(
                "Legal must be an object. Legal information must be a dictionary object"
            )
        if "legaltags" not in legal or "otherRelevantDataCountries" not in legal:
            raise OSMCPValidationError(
                "Legal must contain both 'legaltags' and 'otherRelevantDataCountries' arrays. Legal information is required for compliance"
            )
        if not isinstance(legal["legaltags"], list) or not isinstance(legal["otherRelevantDataCountries"], list):
            raise OSMCPValidationError(
                "Legal legaltags and otherRelevantDataCountries must be arrays. Legal information must contain arrays of strings"
            )
```

### Batch Validation Pattern
```python
async def create_update_records(self, records: List[Dict[str, Any]], 
                                skip_dupes: bool = False) -> Dict[str, Any]:
    """Create or update records with validation."""
    # Validate all records before processing
    for i, record in enumerate(records):
        try:
            self.validate_record(record)
        except OSMCPValidationError as e:
            raise OSMCPValidationError(
                f"Record {i + 1} validation failed: {e}"
            )
    
    # Proceed with API call only after all records pass validation
    # ...
```

### Error Message Guidelines
1. **Specific Field Names**: Always mention the exact field that failed validation
2. **Context Explanation**: Explain why the field is required or what format is expected
3. **Actionable Guidance**: Provide clear steps to fix the validation error
4. **Batch Context**: For batch operations, indicate which record failed
5. **OSDU Compliance**: Reference OSDU requirements when applicable

## Rationale
1. **User Experience**: Clear, actionable error messages reduce confusion
2. **Early Error Detection**: Catch issues before expensive API calls
3. **Compliance Assurance**: Ensure records meet OSDU structural requirements
4. **Development Efficiency**: Faster feedback loop for developers
5. **API Cost Reduction**: Fewer failed API calls due to validation errors
6. **Documentation**: Error messages serve as inline documentation

## Validation Scope
### Required Validations
- **Structural validation**: Required top-level fields (kind, acl, legal, data)
- **Type validation**: Correct data types for each field
- **ACL validation**: Proper viewers/owners array structure
- **Legal validation**: Required compliance fields
- **Format validation**: Array vs. object type checking

### Optional Validations (Future Extensions)
- **Schema validation**: Validate data against kind-specific schemas
- **Legal tag validation**: Verify legal tags exist and are valid
- **ACL group validation**: Verify group names exist in entitlements
- **Kind validation**: Validate kind format and existence
- **Business rule validation**: Domain-specific validation rules

## Consequences
**Positive:**
- Improved user experience with clear error messages
- Earlier error detection reduces API call failures
- Self-documenting validation through descriptive messages
- Consistent validation pattern across all record operations
- Reduced support burden from validation-related issues
- Enhanced data quality and OSDU compliance

**Negative:**
- Additional client-side processing overhead
- Maintenance burden to keep validation in sync with API changes
- Potential for validation logic drift between client and server
- Increased code complexity in client implementations

## Related ADRs
- ADR-004: Error Handling Architecture (exception hierarchy)
- ADR-013: Service Client Architecture Pattern (client method organization)
- ADR-016: Structured Logging and Observability Pattern (error context logging)

## Notes
- Validation should be comprehensive but not overly restrictive
- Error messages should be helpful for both humans and AI assistants
- Consider making validation configurable for advanced users
- Validation logic should be testable independently from API calls