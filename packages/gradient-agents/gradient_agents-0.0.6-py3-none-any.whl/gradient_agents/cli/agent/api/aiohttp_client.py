"""Async HTTP client implementation using aiohttp."""

from __future__ import annotations
import asyncio
import json
from typing import Dict, Any, Optional
import aiohttp

from .http_client import HttpClient, ApiResponse


class AioHttpClient(HttpClient):
    """Async HTTP client implementation using aiohttp."""

    def __init__(
        self,
        base_headers: Optional[Dict[str, str]] = None,
        default_timeout: float = 30.0,
        connector_limit: int = 100,
    ):
        self.base_headers = base_headers or {}
        self.default_timeout = default_timeout
        self.connector_limit = connector_limit
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=self.connector_limit)
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.base_headers,
            )
        return self._session

    def _merge_headers(
        self, additional_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Merge base headers with additional headers."""
        headers = self.base_headers.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Make an HTTP request and return standardized response."""
        session = await self._get_session()
        merged_headers = self._merge_headers(headers)

        # Override session timeout if specified
        request_timeout = None
        if timeout is not None:
            request_timeout = aiohttp.ClientTimeout(total=timeout)

        try:
            async with session.request(
                method=method,
                url=url,
                headers=merged_headers,
                params=params,
                data=data,
                json=json_data,
                timeout=request_timeout,
            ) as response:
                response_headers = dict(response.headers)
                status_code = response.status

                # Try to parse JSON response
                try:
                    response_data = await response.json()
                except (aiohttp.ContentTypeError, json.JSONDecodeError):
                    # If not JSON, get text and wrap it
                    text_content = await response.text()
                    response_data = {"content": text_content} if text_content else None

                # Determine if there's an error
                error_message = None
                if not (200 <= status_code < 300):
                    if isinstance(response_data, dict):
                        error_message = (
                            response_data.get("error")
                            or response_data.get("message")
                            or f"HTTP {status_code} error"
                        )
                    else:
                        error_message = f"HTTP {status_code} error"

                return ApiResponse(
                    status_code=status_code,
                    data=response_data,
                    error=error_message,
                    headers=response_headers,
                )

        except aiohttp.ClientError as e:
            return ApiResponse(
                status_code=0,  # Connection/client error
                error=f"Client error: {str(e)}",
            )
        except asyncio.TimeoutError:
            return ApiResponse(
                status_code=0,
                error="Request timeout",
            )
        except Exception as e:
            return ApiResponse(
                status_code=0,
                error=f"Unexpected error: {str(e)}",
            )

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async GET request."""
        return await self._make_request(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async POST request."""
        return await self._make_request(
            method="POST",
            url=url,
            headers=headers,
            data=data,
            json_data=json,
            timeout=timeout,
        )

    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async PUT request."""
        return await self._make_request(
            method="PUT",
            url=url,
            headers=headers,
            data=data,
            json_data=json,
            timeout=timeout,
        )

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async DELETE request."""
        return await self._make_request(
            method="DELETE",
            url=url,
            headers=headers,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Clean up resources (close sessions, etc.)."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
