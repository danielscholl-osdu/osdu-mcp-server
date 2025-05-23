"""Tests for the exceptions module."""

import pytest
from mcp import McpError

from osdu_mcp_server.shared.exceptions import (
    OSMCPAPIError,
    OSMCPAuthError,
    OSMCPConfigError,
    OSMCPConnectionError,
    OSMCPError,
    handle_osdu_exceptions,
)


def test_exception_hierarchy():
    """Test that all exceptions inherit from OSMCPError."""
    assert issubclass(OSMCPAuthError, OSMCPError)
    assert issubclass(OSMCPAPIError, OSMCPError)
    assert issubclass(OSMCPConfigError, OSMCPError)
    assert issubclass(OSMCPConnectionError, OSMCPError)


def test_api_error_with_status_code():
    """Test OSMCPAPIError with status code."""
    error = OSMCPAPIError("API failed", status_code=404)
    assert str(error) == "API failed"
    assert error.status_code == 404


def test_api_error_without_status_code():
    """Test OSMCPAPIError without status code."""
    error = OSMCPAPIError("API failed")
    assert str(error) == "API failed"
    assert error.status_code is None


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_auth_error():
    """Test exception handler with authentication error."""

    @handle_osdu_exceptions
    async def failing_func():
        raise OSMCPAuthError("Auth failed")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Authentication error: Auth failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_api_error():
    """Test exception handler with API error."""

    @handle_osdu_exceptions
    async def failing_func():
        raise OSMCPAPIError("API failed", status_code=500)

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "OSDU API error (HTTP 500): API failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_config_error():
    """Test exception handler with configuration error."""

    @handle_osdu_exceptions
    async def failing_func():
        raise OSMCPConfigError("Config missing")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Configuration error: Config missing" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_connection_error():
    """Test exception handler with connection error."""

    @handle_osdu_exceptions
    async def failing_func():
        raise OSMCPConnectionError("Connection lost")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Connection error: Connection lost" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_base_error():
    """Test exception handler with base OSDU error."""

    @handle_osdu_exceptions(default_message="Custom error")
    async def failing_func():
        raise OSMCPError("Base error")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Custom error: Base error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_unexpected_error():
    """Test exception handler with unexpected error."""

    @handle_osdu_exceptions
    async def failing_func():
        raise ValueError("Unexpected")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Unexpected error in OSDU operation: Unexpected" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_success():
    """Test exception handler with successful execution."""

    @handle_osdu_exceptions
    async def successful_func():
        return "success"

    result = await successful_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_with_parameters():
    """Test exception handler as decorator with parameters."""

    @handle_osdu_exceptions(default_message="Test operation failed")
    async def failing_func():
        raise OSMCPError("Error")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "Test operation failed: Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_handle_osdu_exceptions_without_parameters():
    """Test exception handler as decorator without parameters."""

    @handle_osdu_exceptions
    async def failing_func():
        raise OSMCPError("Error")

    with pytest.raises(McpError) as exc_info:
        await failing_func()

    assert "OSDU operation failed: Error" in str(exc_info.value)
