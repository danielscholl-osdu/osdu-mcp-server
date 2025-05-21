# OSDU CLI Product Requirements Document

## 1. Executive Summary

The OSDU CLI (Command Line Interface) is a comprehensive command-line tool for interacting with the Open Subsurface Data Universe (OSDU) platform. It enables users to perform a wide range of operations against OSDU services including data management, search, schema management, and workflow orchestration across multiple cloud providers. This tool is designed for both interactive use and automation scenarios, providing a consistent interface to the OSDU ecosystem.

## 2. Product Overview

### 2.1 Purpose

The OSDU CLI provides a command-line interface to interact with the Open Subsurface Data Universe platform, allowing users to:
- Manage data records and files in the OSDU data ecosystem
- Execute searches and queries against the data platform
- Manage metadata, schemas, and legal tags
- Control access through entitlements
- Execute and monitor workflows
- Interact with specialized domain services like Wellbore DDMS

### 2.2 Target Users

- Data engineers and scientists working with subsurface data
- DevOps engineers managing OSDU deployments
- Automation scripts and CI/CD pipelines
- Data administrators managing OSDU platform configuration
- Application developers building on top of OSDU

### 2.3 Key Features

- **Multiple Authentication Methods**: Support for various authentication mechanisms across cloud providers (AWS, Azure, GCP, IBM, bare metal)
- **Configuration Management**: Ability to manage multiple named configurations for different environments
- **Comprehensive Command Set**: Commands for all major OSDU services
- **Flexible Output Formats**: Support for human-readable tables and machine-readable JSON
- **Advanced Filtering**: JMESPath query support for filtering command output
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux systems

## 3. Technical Architecture

### 3.1 Core Components

#### 3.1.1 Command Structure
- **Entry Point**: Main CLI interface defined in `__main__.py`
- **Dynamic Command Discovery**: Automatically discovers commands in the commands directory
- **Click Framework**: Uses Python's Click library for command declaration and parameter handling
- **Custom Command Groups**: Provides custom Click command groups for consistent help text and behavior

#### 3.1.2 Authentication System
- **Multiple Providers**: Supports AWS, Azure, GCP, IBM, and bare metal deployments
- **Authentication Methods**:
  - Generic OAuth Refresh Token
  - MSAL Interactive (browser-based)
  - MSAL Non-Interactive (service principal)
  - AWS Token Authentication
  - Cloud provider-specific methods
- **Token Management**: Handles token acquisition, refreshing, and caching

#### 3.1.3 Client Library
- **CliOsduClient**: Core client class for API interactions
- **Service-Specific Clients**: Specialized clients for different OSDU services
- **HTTP Operations**: Standardized methods for GET, POST, PUT, DELETE operations
- **Error Handling**: Consistent error handling across all operations

#### 3.1.4 Configuration System
- **Config Storage**: Uses INI-style configuration files
- **Environment Variable Support**: Environment variables with `OSDUCLI_` prefix can override settings
- **Multiple Configurations**: Support for managing multiple named configurations
- **Secure Storage**: Sensitive information stored with appropriate file permissions

### 3.2 Error Handling

- **Centralized Error Management**: Common decorator for consistent error handling
- **Detailed Error Messages**: User-friendly error messages with appropriate debug information
- **HTTP Error Processing**: Extracts detailed information from API error responses
- **Configuration Error Detection**: Detects configuration issues and guides users to resolution

### 3.3 Output Formatting

- **Table Output**: Human-readable tabular output for interactive use
- **JSON Output**: Machine-readable JSON output for scripting
- **JMESPath Filtering**: Advanced filtering capabilities using JMESPath queries
- **Debug Mode**: Comprehensive debug output for troubleshooting

## 4. Command Categories

### 4.1 Configuration Commands
- **config update**: Interactive configuration setup
- **config list**: List available configurations
- **config default**: Set default configuration
- **config info**: Display current configuration details

### 4.2 Data Management Commands
- **storage add/get/delete**: Manage data records
- **file download/info/metadata**: Handle file operations
- **schema add/get/list**: Manage data schemas
- **legal add/delete/info/listtags**: Manage legal tags

### 4.3 Query and Search Commands
- **search query**: Execute complex search queries
- **search id/kind**: Search by ID or kind
- **list records**: List available records

### 4.4 Access Control Commands
- **entitlements groups/members**: Manage access control groups and users
- **entitlements mygroups**: View current user's group memberships

### 4.5 Domain-Specific Commands
- **crs areas/list/transforms**: Coordinate reference systems
- **unit list/info**: Unit conversion service
- **wellbore_ddms well_log**: Wellbore data management

### 4.6 Workflow Management
- **workflow register/unregister**: Manage workflow definitions
- **workflow list/get/status**: Monitor workflows
- **workflow runs**: Manage workflow executions

### 4.7 Utility Commands
- **version**: Display CLI version information
- **status**: Check service availability

## 5. User Experience

### 5.1 Command Structure
- All commands follow a consistent pattern: `osdu <command> [subcommand] [options]`
- Commands are organized hierarchically by service
- Common options are available across all commands (`--debug`, `--config`, `--output`, `--filter`)
- Help text is accessible via `-h/--help` flags

### 5.2 Interaction Patterns
- **Interactive Configuration**: Guided setup for first-time users
- **Command Output**: Both human-readable tables and machine-readable JSON
- **Error Handling**: Clear error messages with resolution suggestions
- **Configuration Switching**: Easy switching between environments

### 5.3 Performance Considerations
- Token caching for better performance
- Efficient command execution
- Minimal dependencies for faster installation

## 6. Deployment and Installation

### 6.1 Distribution Method
- Python package available on PyPI
- Requirements: Python 3.12+
- Installation via pip: `pip install osducli`

### 6.2 Dependencies
- Primary dependencies: click, jmespath, tabulate, requests
- Cloud provider-specific dependencies: boto3, msal, google-auth
- OSDU API SDK dependency

### 6.3 Compatibility
- Compatible with Windows, macOS, and Linux
- Works with all major OSDU deployments across cloud providers

## 7. Security Considerations

### 7.1 Authentication Security
- Secure storage of credentials with appropriate file permissions
- Support for non-interactive authentication for automated scenarios
- No hardcoding of credentials in the source code

### 7.2 Data Security
- Secure transport via HTTPS
- No caching of sensitive data
- Proper error handling to avoid information leakage

## 8. Development and Testing

### 8.1 Development Guidelines
- Consistent command implementation patterns
- Comprehensive help text documentation
- Proper error handling and output formatting
- Unit tests for all commands

### 8.2 Testing Approach
- Unit tests for all commands
- Test fixtures for API responses
- Mock objects for service interactions
- VCR for recording/replaying HTTP interactions

## 9. Future Enhancements

### 9.1 Potential Improvements
- Advanced automation capabilities
- Additional output formats (CSV, YAML)
- Interactive shell mode for multiple commands
- Command auto-completion for shells
- Enhanced logging and diagnostic capabilities
- Integration with more OSDU services as they become available

### 9.2 Version Roadmap
- Current version: 0.0.45 (Alpha)
- Path to Beta: Complete implementation of all core services
- Path to Production: Enhanced stability, comprehensive documentation, and broader cloud provider support

## 10. Conclusion

The OSDU CLI is a powerful tool for interacting with the Open Subsurface Data Universe platform. It provides a consistent, cross-platform interface for managing data, executing queries, and interacting with OSDU services. With support for multiple authentication methods, configuration management, and flexible output formats, it meets the needs of both interactive users and automation scenarios.

As the OSDU platform continues to evolve, the CLI will expand to support new services and capabilities, maintaining its role as an essential tool for OSDU users and administrators.