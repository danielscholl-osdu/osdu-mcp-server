"""Tests for the OsduClient class focusing on behavior, not implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from aioresponses import aioresponses

from osdu_mcp_server.shared.osdu_client import OsduClient
from osdu_mcp_server.shared.exceptions import OSMCPAPIError, OSMCPConnectionError


@pytest.mark.asyncio
async def test_osdu_client_get_success():
    """Test successful GET request returns correct data."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with aioresponses() as mocked:
        # Mock the HTTP response
        mocked.get(
            "https://test-osdu.com/api/test",
            payload={"result": "success"},
            status=200
        )

        client = OsduClient(mock_config, mock_auth)
        result = await client.get("/api/test")

        # Test behavior - correct result returned
        assert result == {"result": "success"}

        await client.close()


@pytest.mark.asyncio
async def test_osdu_client_post_with_data():
    """Test POST request correctly sends data and returns result."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with aioresponses() as mocked:
        # Mock the HTTP response
        mocked.post(
            "https://test-osdu.com/api/create",
            payload={"id": "123", "created": True},
            status=201
        )

        client = OsduClient(mock_config, mock_auth)
        result = await client.post("/api/create", {"name": "test", "value": 42})

        # Test behavior - correct result returned
        assert result == {"id": "123", "created": True}

        await client.close()


@pytest.mark.asyncio
async def test_osdu_client_handles_api_errors():
    """Test that API errors are converted to OSMCPAPIError with status code."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with aioresponses() as mocked:
        # Mock an error response
        mocked.get(
            "https://test-osdu.com/api/bad",
            status=400,
            body="Bad request: invalid parameter"
        )

        client = OsduClient(mock_config, mock_auth)

        # Test behavior - raises correct exception
        with pytest.raises(OSMCPAPIError) as exc_info:
            await client.get("/api/bad")

        assert "Request failed: Bad request: invalid parameter" in str(exc_info.value)
        assert exc_info.value.status_code == 400

        await client.close()


@pytest.mark.asyncio
async def test_osdu_client_retries_on_connection_error():
    """Test that connection errors trigger retries with exponential backoff."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with aioresponses() as mocked:
        # First two calls fail, third succeeds
        mocked.get(
            "https://test-osdu.com/api/flaky",
            exception=aiohttp.ClientError("Connection failed")
        )
        mocked.get(
            "https://test-osdu.com/api/flaky",
            exception=aiohttp.ClientError("Connection failed")
        )
        mocked.get(
            "https://test-osdu.com/api/flaky",
            payload={"result": "success"},
            status=200
        )

        with patch("asyncio.sleep") as mock_sleep:
            client = OsduClient(mock_config, mock_auth)
            result = await client.get("/api/flaky")

            # Test behavior - eventually returns success
            assert result == {"result": "success"}

            # Test behavior - used exponential backoff
            assert mock_sleep.call_count == 2
            mock_sleep.assert_any_call(1)  # First retry: 1 second
            mock_sleep.assert_any_call(2)  # Second retry: 2 seconds

            await client.close()


@pytest.mark.asyncio
async def test_osdu_client_fails_after_max_retries():
    """Test that connection errors eventually fail after max retries."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with aioresponses() as mocked:
        # All calls fail
        for _ in range(3):
            mocked.get(
                "https://test-osdu.com/api/broken",
                exception=aiohttp.ClientError("Connection failed")
            )

        with patch("asyncio.sleep") as mock_sleep:
            client = OsduClient(mock_config, mock_auth)

            # Test behavior - raises connection error after retries
            with pytest.raises(OSMCPConnectionError) as exc_info:
                await client.get("/api/broken")

            assert "Connection error: Connection failed" in str(exc_info.value)

            # Test behavior - performed correct number of retries
            assert mock_sleep.call_count == 2

            await client.close()


@pytest.mark.asyncio
async def test_osdu_client_reuses_session():
    """Test that the client reuses the same session for multiple requests."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    with patch("osdu_mcp_server.shared.osdu_client.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = OsduClient(mock_config, mock_auth)

        # Make multiple requests
        await client._ensure_session()
        await client._ensure_session()

        # Test behavior - session created only once
        mock_session_class.assert_called_once()

        # Test behavior - close cleans up session
        await client.close()
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_osdu_client_correctly_formats_headers():
    """Test that client sets correct headers on requests."""
    mock_config = MagicMock()
    mock_config.get_required.side_effect = lambda section, key: {
        ("server", "url"): "https://test-osdu.com",
        ("server", "data_partition"): "test-partition"
    }[(section, key)]
    mock_config.get.return_value = 30

    mock_auth = AsyncMock()
    mock_auth.get_access_token.return_value = "test-token"

    # Mock at the session level to capture headers
    with patch("osdu_mcp_server.shared.osdu_client.ClientSession") as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"result": "success"}

        # Create a context manager for the request
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None

        # Mock the session
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(return_value=mock_context)
        mock_session_class.return_value = mock_session

        client = OsduClient(mock_config, mock_auth)
        await client.get("/api/test")

        # Verify headers were set correctly
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        headers = call_args[1]["headers"]

        assert headers["Authorization"] == "Bearer test-token"
        assert headers["data-partition-id"] == "test-partition"
        assert headers["Content-Type"] == "application/json"

        await client.close()
