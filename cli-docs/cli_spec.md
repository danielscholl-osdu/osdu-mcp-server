# OSDU CLI Technical Specification

## 1. Introduction

This specification document provides a detailed technical description of the OSDU Command Line Interface (CLI) implementation. It serves as a comprehensive reference for developers working with the codebase, including those who may use AI tools to extend or maintain the CLI.

The OSDU CLI is a command-line tool designed to interact with the Open Subsurface Data Universe (OSDU) platform. It provides a consistent interface for accessing OSDU services across different cloud providers and deployment models.

## 2. Package Structure

### 2.1 Directory Structure

The OSDU CLI follows a modular structure with clear separation of concerns:

```
src/osducli/
├── __init__.py       # Version information
├── __main__.py       # Main entry point and command discovery
├── auth/             # Authentication mechanisms
│   ├── aws_token_credential.py
│   ├── credentials.py
│   ├── msal_interactive.py
│   ├── msal_non_interactive.py
│   └── token_credential.py
├── click_cli.py      # Click extensions and utilities
├── cliclient.py      # OSDU API client
├── commands/         # CLI commands organized by service
│   ├── config/       # Configuration management
│   ├── crs/          # Coordinate reference system
│   ├── dataload/     # Data loading
│   ├── entitlements/ # Access control
│   ├── legal/        # Legal tags
│   ├── schema/       # Schema management
│   ├── search/       # Search functionality
│   ├── storage/      # Storage operations
│   ├── ...           # Other services
├── config.py         # Configuration management
├── log.py            # Logging utilities
├── state.py          # State management
├── util/             # Utility functions
│   ├── exceptions.py
│   ├── file.py
│   ├── prompt.py
│   ├── pypi.py
│   └── service_info.py
└── wbddms_client.py  # Wellbore domain client
```

### 2.2 Key Components

1. **Entry Points**
   - `__main__.py`: Main CLI entry point
   - `click_cli.py`: Click framework customizations

2. **Core Infrastructure**
   - `config.py`: Configuration management
   - `state.py`: CLI state tracking
   - `log.py`: Logging infrastructure

3. **API Clients**
   - `cliclient.py`: Main OSDU API client
   - Service-specific clients (Search, Storage, etc.)

4. **Authentication**
   - Multiple authentication providers in `auth/`
   - Cloud provider-specific implementations

5. **Commands**
   - Organized by service in `commands/`
   - Each command in its own module

6. **Utilities**
   - `util/`: Common utilities and helpers
   - `exceptions.py`: Custom exception classes

## 3. Command Architecture and Discovery

### 3.1 Command Discovery Mechanism

The OSDU CLI uses a dynamic discovery mechanism to find and register commands:

```python
def get_commands_from_pkg(pkg) -> dict:
    """Dynamically and recursively get all click commands within the specified package"""
    # keep_groups defines command groups that should remain as groups
    keep_groups = ["osducli.commands.legal", "osducli.commands.list", "osducli.commands.unit"]
    pkg_obj = importlib.import_module(pkg)
    pkg_path = os.path.dirname(pkg_obj.__file__)
    commands = {}
    
    # Iterate through all modules in the package
    for module in pkgutil.iter_modules([pkg_path]):
        module_obj = importlib.import_module(f"{pkg}.{module.name}")

        # Regular module with _click_command
        if not module.ispkg:
            if hasattr(module_obj, "_click_command"):
                commands[module.name] = module_obj._click_command
                
        # Subpackage - recursive discovery
        else:
            group_commands = get_commands_from_pkg(f"{pkg}.{module.name}")
            # Flatten single-command groups unless explicitly kept
            if len(group_commands) == 1 and f"{pkg}.{module.name}" not in keep_groups:
                click_command = list(group_commands.values())[0]
                click_command.context_settings["help_option_names"] = ["-h", "--help"]
                commands[module.name.replace("_", "-")] = click_command
            # Keep multi-command groups
            elif len(group_commands) >= 1:
                commands[module.name.replace("_", "-")] = CustomClickGroup(
                    context_settings={"help_option_names": ["-h", "--help"]},
                    help=module_obj.__doc__,
                    commands=group_commands,
                )
    return commands
```

The main CLI group is defined using:

```python
@click.group(
    cls=CustomMainClickGroup,
    commands=get_commands_from_pkg("osducli.commands"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
```

### 3.2 Command Execution Flow

1. CLI Entry: User invokes the CLI with command and arguments
2. Dynamic Discovery: Commands are discovered and registered
3. Command Selection: Click parses arguments to determine command
4. State Initialization: Global state object created
5. Parameter Processing: Command parameters processed
6. Command Execution: Selected command function executed
7. Output Formatting: Results formatted according to preferences
8. Error Handling: Exceptions captured and formatted

### 3.3 Custom Click Classes

Custom Click classes are used to enhance the CLI experience:

- `CustomClickGroup`: Enhanced Click group with custom help formatting
- `CustomMainClickGroup`: Top-level group with version checking
- `CustomClickCommand`: Enhanced Click command with consistent help text

## 4. Authentication System

### 4.1 Authentication Architecture

The authentication system is built around the `BaseCredentials` interface with multiple implementations:

```
BaseCredentials (interface)
├── TokenCredential         # OAuth refresh token authentication
├── MsalInteractiveCredential    # Azure interactive authentication
├── MsalNonInteractiveCredential # Azure service principal
└── AwsTokenCredential      # AWS authentication
```

### 4.2 Credential Interface

All credential classes implement a common interface:

```python
class BaseCredentials:
    @property
    def access_token(self) -> str:
        """Get the current access token"""
        pass
        
    def refresh_token(self) -> str:
        """Refresh and return a new access token"""
        pass
```

### 4.3 Authentication Implementations

#### 4.3.1 TokenCredential (OAuth Refresh Token)

```python
class TokenCredential(BaseCredentials):
    def __init__(self, client_id, token_endpoint, refresh_token, client_secret):
        self._client_id = client_id
        self._token_endpoint = token_endpoint
        self._refresh_token = refresh_token
        self._client_secret = client_secret
        
    @property
    def access_token(self) -> str:
        # Check expiration and refresh if needed
        if datetime.now().timestamp() > self.__access_token_expire_date:
            self.refresh_token()
        return self.__access_token
        
    def refresh_token(self) -> str:
        # OAuth2 refresh token grant
        result = self._refresh_access_token()
        if "access_token" in result:
            self.__access_token = result["access_token"]
            self.__access_token_expire_date = datetime.now().timestamp() + result["expires_in"]
        return self.__access_token
```

#### 4.3.2 MsalInteractiveCredential (Azure Interactive)

```python
class MsalInteractiveCredential(BaseCredentials):
    def __init__(self, client_id, authority, scopes, token_cache=None):
        self._client_id = client_id
        self._authority = authority
        self._scopes = scopes
        self._token_cache = token_cache
        
    def refresh_token(self) -> str:
        # MSAL browser-based authentication
        cache = msal.SerializableTokenCache()
        if os.path.exists(self._token_cache):
            with open(self._token_cache, encoding="utf8") as cachefile:
                cache.deserialize(cachefile.read())
                
        app = msal.PublicClientApplication(
            self._client_id, authority=self._authority, token_cache=cache
        )
        
        # Try to use cached token
        accounts = app.get_accounts()
        if accounts:
            chosen = accounts[0]
            result = app.acquire_token_silent([self._scopes], account=chosen)
            
        # If no token in cache, interactive login
        if not result:
            result = app.acquire_token_interactive([self._scopes])
            if cache.has_state_changed:
                with open(self._token_cache, "w", encoding="utf8") as cachefile:
                    cachefile.write(cache.serialize())
                    
        self.__access_token = result["access_token"]
        return self.__access_token
```

#### 4.3.3 AWS and Other Providers

Similar patterns are implemented for AWS and other cloud providers, each following the BaseCredentials interface with provider-specific implementations.

### 4.4 Credential Selection

Credentials are selected in `cliclient.py` based on configuration:

```python
authentication_mode = config.get("core", CONFIG_AUTHENTICATION_MODE)

if authentication_mode == "refresh_token":
    credentials = refresh_token_credentials(config)
elif authentication_mode == "msal_interactive":
    credentials = msal_interactive_credentials(config)
elif authentication_mode == "msal_non_interactive":
    credentials = msal_non_interactive_credentials(config)
elif authentication_mode == AWS_CLOUD_PROVIDER:
    credentials = aws_token_credentials(config)
elif authentication_mode in [
    AZURE_CLOUD_PROVIDER,
    BAREMETAL_PROVIDER,
    GOOGLE_CLOUD_PROVIDER,
    IBM_CLOUD_PROVIDER,
]:
    credentials = get_credentials(authentication_mode)
```

## 5. Configuration System

### 5.1 Configuration Storage

Configuration is stored in INI-style files using Python's `configparser` with support for environment variables:

```python
class CLIConfig(BaseConfigManager):
    def __init__(self, config_dir, config_env_var_prefix, config_file_name=None):
        # Default configuration path
        self.config_dir = os.environ.get(f"{env_var_prefix.upper()}_CONFIG_DIR", default_config_dir)
        self.config_file_name = config_file_name or CLIConfig._DEFAULT_CONFIG_FILE_NAME
        self.config_path = os.path.join(self.config_dir, self.config_file_name)
        self._env_var_format = f"{env_var_prefix.upper()}_{{section}}_{{option}}"
        
        # Load configuration
        self.config_parser = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self.config_parser.read(self.config_path)
```

### 5.2 Configuration Hierarchy

Configuration values are resolved in this order:
1. Environment variables (highest priority)
2. Configuration file values
3. Default values (lowest priority)

```python
def get(self, section, option, default=_UNSET):
    # Check environment variables first
    env = self.env_var_name(section, option)
    if env in os.environ:
        return os.environ[env]
        
    # Then check configuration file
    try:
        if self.config_parser:
            return self.config_parser.get(section, option)
        raise configparser.NoOptionError(option, section)
    except (configparser.NoSectionError, configparser.NoOptionError) as ex:
        last_ex = ex
        
    # Finally use default if provided
    if default is _UNSET:
        raise last_ex
    return default
```

### 5.3 Configuration Commands

The CLI provides commands for configuration management:

- `config update`: Interactive configuration setup
- `config list`: List available configurations
- `config default`: Set the default configuration
- `config info`: Show current configuration

### 5.4 Integration with State

Configuration is integrated with the CLI state:

```python
class State:
    """Global state passed to all click commands"""
    def __init__(self):
        self.debug = False
        self.config_path = None
        self.config = None
        self.output = None
        self.jmes = None
```

## 6. Client Library and API Interaction

### 6.1 CliOsduClient Implementation

The main client class is `CliOsduClient`, which extends `BaseClient` from the OSDU API SDK:

```python
class CliOsduClient(BaseClient):
    def __init__(self, config: CLIConfig):
        # Load configuration
        self.config = config
        self.server_url = config.get("core", CONFIG_SERVER)
        data_partition = config.get("core", CONFIG_DATA_PARTITION_ID)
        authentication_mode = config.get("core", CONFIG_AUTHENTICATION_MODE)
        
        # Create appropriate credentials
        credentials = create_credentials_for_mode(authentication_mode, config)
        
        # Initialize base client
        token_refresher = BaseTokenRefresher(credentials)
        super().__init__(
            config_manager=config, 
            data_partition_id=data_partition, 
            token_refresher=token_refresher
        )
```

### 6.2 API Request Methods

The client provides wrapper methods for common HTTP operations:

```python
def cli_get_returning_json(self, config_url_key, url_extra_path, ok_status_codes=None):
    url = self.url_from_config(config_url_key, url_extra_path)
    response = self.make_request(method=HttpMethod.GET, url=url)
    self.check_status_code(response, ok_status_codes)
    return response.json()

def cli_post_returning_json(self, config_url_key, url_extra_path, data, ok_status_codes=None):
    url = self.url_from_config(config_url_key, url_extra_path)
    if isinstance(data, dict):
        data = json.dumps(data)
    response = self.make_request(method=HttpMethod.POST, url=url, data=data)
    self.check_status_code(response, ok_status_codes)
    return response.json()
```

### 6.3 Service-Specific Clients

The client creates service-specific clients for different OSDU services:

```python
def get_search_client(self) -> SearchClient:
    search_url = self.url_from_config(CONFIG_SEARCH_URL, "")
    if search_url.endswith("/"):
        search_url = search_url[:-1]
    return SearchClient(
        search_url=search_url,
        config_manager=self.config,
        data_partition_id=self.data_partition_id,
        token_refresher=self.token_refresher
    )
```

### 6.4 URL Construction

URLs are constructed from configuration values:

```python
def url_from_config(self, config_url_key: str, url_extra_path: str) -> str:
    unit_url = self.config.get("core", config_url_key)
    url = urljoin(self.server_url, unit_url) + url_extra_path
    return url
```

### 6.5 Response Validation

Responses are validated consistently:

```python
def check_status_code(self, response: requests.Response, ok_status_codes: list = None):
    if ok_status_codes is None:
        ok_status_codes = [200]
    if response.status_code not in ok_status_codes:
        raise HTTPError(response=response)
```

## 7. Command Implementation Patterns

### 7.1 Standard Command Structure

Commands follow a consistent structure:

```python
# Command definition
@click.command(cls=CustomClickCommand)
@click.option("-p", "--path", help="...", type=click.Path(...), required=True)
@handle_cli_exceptions
@command_with_output("results[*].{...}")
def _click_command(state: State, path: str):
    """Command description"""
    return implementation_function(state, path)

# Command implementation
def implementation_function(state: State, path: str):
    """Actual implementation with docstring
    
    Args:
        state: Global state
        path: The path argument
        
    Returns:
        dict: The result data
    """
    client = CliOsduClient(state.config)
    # Implementation logic...
    return result_data
```

### 7.2 Command Parameter Definition

Parameters are defined using Click's option decorator:

```python
@click.option(
    "-p", "--path",
    help="Path to a record or records to add.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
```

### 7.3 Output Formatting

Output formatting is handled by the `command_with_output` decorator:

```python
@command_with_output("results[*].{Id:id,Kind:kind,CreateTime:createTime}")
```

This decorator applies JMESPath transformations and formats output as JSON or tables.

## 8. Error Handling and Output Formatting

### 8.1 Error Handling Decorator

The `handle_cli_exceptions` decorator provides consistent error handling:

```python
def handle_cli_exceptions(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
            try:
                error_content = ex.response.json()
                logger.error("Message: %s", error_content.get("message"))
            except json.JSONDecodeError:
                logger.error("Response: %s", ex.response.content)
        except CliError as ex:
            logger.error("Error %s", ex.message)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.error(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osdu config update'", ex.args[0]
            )
        sys.exit(1)
    return decorated
```

### 8.2 Output Formatting

The `command_with_output` decorator handles output formatting:

```python
def command_with_output(table_transformer=None):
    def wrapper_for_params(func):
        @click.option("-o", "--output", type=click.Choice(["json"]), help="Output format...")
        @click.option("--filter", help="JMESPath string for filtering output...", callback=jmes_callback)
        @functools.wraps(func)
        @global_params
        def func_wrapper(*args, **kwargs):
            state = args[0]
            kwargs.pop("output")
            kwargs.pop("filter")
            result = func(*args, **kwargs)
            
            # Apply JMESPath filtering
            if result is not None:
                if type(result) in [dict, list]:
                    if state.jmes is not None or table_transformer is not None:
                        jmes = state.jmes if state.jmes is not None else table_transformer
                        query_expression = compile_jmespath(jmes)
                        result = query_expression.search(result, Options(collections.OrderedDict))
                        
                    # Format as JSON or table
                    if state.output == "json":
                        print(json.dumps(result, indent=2))
                    else:
                        result_list = result if isinstance(result, list) else [result]
                        table_output = _TableOutput(False)
                        print(table_output.dump(result_list))
        return func_wrapper
    return wrapper_for_params
```

### 8.3 Table Formatting

The `_TableOutput` class handles table formatting:

```python
class _TableOutput:
    def __init__(self, should_sort_keys=False):
        self.should_sort_keys = should_sort_keys
        
    def _auto_table_item(self, item):
        # Convert item to tabular format
        new_entry = collections.OrderedDict()
        try:
            keys = sorted(item) if self.should_sort_keys else item.keys()
            for k in keys:
                if item[k] is not None and not isinstance(item[k], (list, dict, set)):
                    new_entry[self._capitalize_first_char(k)] = item[k]
        except AttributeError:
            # Handle non-dict items
            if isinstance(item, list):
                for col, val in enumerate(item):
                    new_entry[f"Column{col + 1}"] = val
            else:
                new_entry["Result"] = item
        return new_entry
        
    def dump(self, data):
        table_data = self._auto_table(data)
        table_str = tabulate(
            table_data, 
            headers="keys", 
            tablefmt="simple", 
            disable_numparse=True
        ) if table_data else ""
        if table_str == "\n":
            raise ValueError("Unable to extract fields for table.")
        return table_str + "\n"
```

## 9. Testing and Development

### 9.1 Testing Framework

The codebase uses pytest as the primary testing framework, with:
- A base test class `BaseTestCase` in `tests/base_test_case.py`
- Test helpers in `tests/helpers.py`
- Test data in JSON files under `tests/commands/*/data/`

### 9.2 Development Commands

Development commands are defined in `pyproject.toml`:

```
[project.optional-dependencies]
dev = [
    # formatting
    "black",
    "isort",
    # linting
    "pylint",
    "ruff",
    # testing
    "pytest",
    "pytest-mock",
    "pytest-cov",
    "mock",
    "testfixtures",
    # other frameworks
    "setuptools",
    "tox",
    "docutils"
]
```

### 9.3 Test Execution

Tests can be run using:
- `pytest ./tests`: Run all tests
- `pytest ./tests/commands/legal/test_add.py`: Run specific test file
- `pytest --cov=src ./tests`: Run tests with coverage

## 10. Extension Points

### 10.1 Adding New Commands

To add a new command:

1. Create a new module in the appropriate `commands/` subdirectory
2. Define a `_click_command` function with Click decorators
3. Implement the command functionality in a separate function
4. Document the command with docstrings

### 10.2 Adding New Authentication Methods

To add a new authentication method:

1. Create a new class inheriting from `BaseCredentials`
2. Implement the `access_token` property and `refresh_token` method
3. Add credential creation in `credentials.py`
4. Update the authentication mode handling in `CliOsduClient`

### 10.3 Adding New Service Clients

To add a new service client:

1. Create a new client class inheriting from `BaseClient`
2. Implement service-specific methods
3. Add a factory method in `CliOsduClient`
4. Create command modules for the new service

## 11. Conclusion

The OSDU CLI provides a flexible, extensible interface to OSDU services with consistent command patterns, robust error handling, and flexible output formatting. This specification document serves as a comprehensive guide to the implementation details to aid in understanding, maintaining, and extending the codebase.