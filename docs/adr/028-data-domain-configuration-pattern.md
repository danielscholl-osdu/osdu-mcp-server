# ADR-028: Data Domain Configuration Pattern

## Status
**Accepted** - 2025-06-19

## Context
OSDU Access Control Lists (ACLs) require domain-specific identifiers that vary between different OSDU deployment environments. The domain is not the server FQDN but rather an internal data domain identifier used for tenant isolation and access control.

During workflow implementation, we discovered that ACL format errors were common because the domain component varies between Standard OSDU (`contoso.com`), Microsoft OSDU (`dataservices.energy`), and other deployments (`msft-osdu-test.org`). Without proper domain configuration, users experience frequent ACL validation failures.

## Decision
Implement **environment-variable based data domain configuration** with sensible defaults and clear domain-to-deployment mapping.

## Rationale
1. **Environment Flexibility**: Different OSDU deployments use different data domains
2. **Default Convenience**: Most users work with Standard OSDU (contoso.com)
3. **ACL Format Accuracy**: Correct domain ensures ACL validation passes
4. **Template Consistency**: Resources and examples use appropriate domains
5. **Clear Documentation**: Explicit mapping between deployment types and domains

## Implementation Details

### Environment Variable
```bash
OSDU_MCP_SERVER_DOMAIN=contoso.com  # Standard OSDU default
```

### Configuration Manager Integration
```python
class ConfigManager:
    def get_data_domain(self) -> str:
        """Get the OSDU data domain for ACL formatting."""
        return self.get("server", "domain", "contoso.com")
```

### Domain-to-Deployment Mapping
| Deployment Type | Data Domain | Example Server URL |
|----------------|-------------|-------------------|
| **Standard OSDU** | `contoso.com` | `https://your-osdu-instance.com` |
| **Microsoft Energy Data Services** | `dataservices.energy` | `https://your-instance.energy.azure.com` |
| **Microsoft Test Environment** | `msft-osdu-test.org` | `https://your-test.energy.azure.com` |

### ACL Format Pattern
```json
{
  "viewers": ["data.default.viewers@{domain}"],
  "owners": ["data.default.owners@{domain}"]
}
```

### Template Domain Injection
```python
def get_acl_template(domain: str = None) -> dict:
    """Generate ACL template with appropriate domain."""
    if domain is None:
        config = ConfigManager()
        domain = config.get_data_domain()
    
    return {
        "viewers": [f"data.default.viewers@{domain}"],
        "owners": [f"data.default.owners@{domain}"]
    }
```

## Domain Detection Strategy
While automatic detection was considered, explicit configuration is preferred:

### Manual Configuration (Chosen)
- **Pros**: Explicit, predictable, no false positives
- **Cons**: Requires user configuration knowledge
- **Decision**: Better for production reliability

### Automatic Detection (Rejected)
- **Pros**: Zero configuration for users
- **Cons**: Server URL doesn't reliably indicate data domain
- **Example Problem**: `https://custom.company.com` could use any data domain

## Resource Template Integration
Templates use domain placeholders that are resolved at runtime:

```json
{
  "acl": {
    "viewers": ["data.default.viewers@{{domain}}"],
    "owners": ["data.default.owners@{{domain}}"]
  }
}
```

Resolution occurs when resources are served to AI assistants.

## Configuration Documentation
Clear documentation maps deployment types to required domains:

### Standard OSDU
```bash
export OSDU_MCP_SERVER_DOMAIN=contoso.com
```

### Microsoft Energy Data Services
```bash
export OSDU_MCP_SERVER_DOMAIN=dataservices.energy
```

### Custom/Test Environments
```bash
export OSDU_MCP_SERVER_DOMAIN=your-custom-domain.org
```

## Benefits
1. **ACL Accuracy**: Correct domain ensures ACL validation passes consistently
2. **Deployment Flexibility**: Single configuration works across environments
3. **Template Consistency**: All templates use appropriate domain automatically
4. **Error Reduction**: Eliminates domain-related ACL format errors
5. **Clear Mapping**: Explicit documentation of domain-to-deployment relationships

## Consequences

### Positive
- **Eliminates ACL Format Errors**: Correct domain prevents most ACL validation failures
- **Environment Portability**: Easy to move between different OSDU deployments
- **Template Accuracy**: Resources automatically reflect correct domain
- **Clear Documentation**: Users understand which domain to use
- **Consistent Behavior**: All tools and resources use same domain configuration

### Negative
- **Configuration Requirement**: Users must know and set correct domain
- **Documentation Burden**: Must maintain deployment-to-domain mapping
- **Template Complexity**: Domain injection adds processing overhead
- **Environment Coupling**: Configuration tied to specific OSDU deployment

## Domain Validation
Optional validation to catch common configuration errors:

```python
def validate_domain(domain: str) -> bool:
    """Validate that domain follows expected patterns."""
    known_domains = [
        "contoso.com",           # Standard OSDU
        "dataservices.energy",   # Microsoft OSDU
        "msft-osdu-test.org"     # Microsoft Test
    ]
    
    # Allow known domains or custom domains with proper format
    return domain in known_domains or re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', domain)
```

## Error Handling
Clear error messages when domain configuration issues are detected:

```python
if acl_validation_failed and "domain" in error_message:
    suggest_domain_check = (
        f"ACL domain validation failed. Current domain: {current_domain}. "
        f"Check OSDU_MCP_SERVER_DOMAIN environment variable. "
        f"Common values: contoso.com (Standard OSDU), "
        f"dataservices.energy (Microsoft OSDU)"
    )
```

## Future Enhancements
1. **Auto-Detection**: Attempt domain detection from OSDU API responses
2. **Domain Registry**: Maintain registry of known OSDU deployments and their domains
3. **Validation API**: Endpoint to test ACL format with current domain
4. **Multi-Domain Support**: Support for multi-tenant environments with different domains

## Related ADRs
- **ADR-003**: Configuration Management Approach - environment-first configuration
- **ADR-021**: Record Validation Pattern - includes ACL validation
- **ADR-027**: MCP Resources Implementation Pattern - templates use domain configuration
- **ADR-015**: Sensitive Data Handling Pattern - domain is not sensitive but deployment-specific

## Migration Notes
For existing users:
1. **Default Behavior**: Continues to work with `contoso.com` default
2. **Microsoft Users**: Must set `OSDU_MCP_SERVER_DOMAIN=dataservices.energy`
3. **Template Updates**: Existing templates automatically use new domain configuration
4. **No Breaking Changes**: Backward compatible with existing configurations