# ADR-003: Configuration Management Approach

## Status
**Accepted** - 2025-05-15

## Context
The MCP server needs flexible configuration that works across development, staging, and production environments. Configuration sources need clear precedence and the system should be easy to debug when misconfigured.

## Decision
Implement **environment-first configuration** with YAML file fallback and clear precedence hierarchy.

## Rationale
1. **Environment Variable Priority**: Enables easy override in containers/cloud deployments
2. **CLI Pattern Consistency**: Mirrors OSDU CLI configuration approach
3. **Debugging Friendly**: Clear precedence rules make troubleshooting easier
4. **Deployment Flexibility**: Works in containerized and non-containerized environments
5. **Security**: Sensitive values stay in environment variables

## Alternatives Considered
1. **YAML-Only Configuration**
   - **Pros**: Single source of truth, version controllable
   - **Cons**: Secrets in files, no environment-specific overrides
   - **Decision**: Rejected due to security concerns

2. **Environment Variables Only**
   - **Pros**: Secure, deployment-friendly
   - **Cons**: Verbose, no structured config, hard to manage defaults
   - **Decision**: Too limiting for complex configurations

3. **Advanced Config Libraries** (e.g., Hydra, OmegaConf)
   - **Pros**: Powerful features, composition
   - **Cons**: Overengineered for our needs, learning curve
   - **Decision**: Unnecessary complexity

## Consequences
**Positive:**
- Easy to override configuration in different environments
- Secure handling of sensitive values
- Simple to understand and debug
- Consistent with team's experience

**Negative:**
- Need to manage two configuration layers
- Requires documentation of all configuration options
- Environment variable names can become verbose

## Implementation Notes
```python
class ConfigManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.env_prefix = "OSDU_MCP_"
        self._file_config = self._load_yaml(config_file)
    
    def get(self, section: str, key: str, default=None):
        # 1. Check environment variables first
        env_key = f"{self.env_prefix}{section.upper()}_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # 2. Check YAML file
        if self._file_config and section in self._file_config:
            return self._file_config[section].get(key, default)
        
        # 3. Return default
        return default
```

## Configuration Precedence
1. **Environment Variables** (highest priority)
2. **YAML Configuration File**
3. **Default Values** (lowest priority)

## Success Criteria
- Configuration loads correctly in all environments
- Environment variables override file values as expected
- Clear error messages when required configuration is missing