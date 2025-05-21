"""HTTP client for OSDU API interactions.

This module implements an async HTTP client with connection pooling
and retry logic as defined in ADR-005.
"""

import asyncio
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from .auth_handler import AuthHandler
from .config_manager import ConfigManager
from .exceptions import OSMCPAPIError, OSMCPConnectionError


class OsduClient:
    """Async HTTP client for OSDU APIs with connection pooling and retries."""

    def __init__(self, config: ConfigManager, auth_handler: AuthHandler):
        """Initialize OSDU client.

        Args:
            config: Configuration manager instance
            auth_handler: Authentication handler instance
        """
        self.config = config
        self.auth_handler = auth_handler
        self._session: Optional[ClientSession] = None
        self._base_url = config.get_required("server", "url")
        self._data_partition = config.get_required("server", "data_partition")
        self._timeout = config.get("server", "timeout", 30)

    async def _ensure_session(self) -> ClientSession:
        """Ensure HTTP session is created.

        Returns:
            Active aiohttp session
        """
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self._timeout)
            self._session = ClientSession(timeout=timeout)
        return self._session

    async def _make_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary

        Raises:
            OSMCPAPIError: For API errors
            OSMCPConnectionError: For connection errors
        """
        url = urljoin(self._base_url, path)
        session = await self._ensure_session()

        # Set up headers
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {await self.auth_handler.get_access_token()}"
        headers["data-partition-id"] = self._data_partition
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        # Retry logic with exponential backoff
        max_retries = 3
        base_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise OSMCPAPIError(
                            f"Request failed: {error_text}", response.status
                        )

                    # Return JSON response
                    try:
                        return await response.json()
                    except Exception:
                        # Handle non-JSON responses (e.g., plain text)
                        text = await response.text()
                        return {"response": text}

            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise OSMCPConnectionError(f"Connection error: {e}")

                # Exponential backoff
                delay = base_delay * (2**attempt)
                await asyncio.sleep(delay)

            except Exception as e:
                if "OSMCPAPIError" in str(type(e)):
                    raise
                raise OSMCPAPIError(f"Unexpected error: {e}")

    async def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """GET request with retry logic.

        Args:
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary
        """
        return await self._make_request("GET", path, **kwargs)

    async def post(self, path: str, data: Any, **kwargs: Any) -> Dict[str, Any]:
        """POST request with retry logic.

        Args:
            path: API path
            data: Request body data
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary
        """
        kwargs["json"] = data
        return await self._make_request("POST", path, **kwargs)

    async def put(self, path: str, data: Any, **kwargs: Any) -> Dict[str, Any]:
        """PUT request with retry logic.

        Args:
            path: API path
            data: Request body data
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary
        """
        kwargs["json"] = data
        return await self._make_request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """DELETE request with retry logic.

        Args:
            path: API path
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary
        """
        return await self._make_request("DELETE", path, **kwargs)

    async def close(self) -> None:
        """Clean up HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
