"""HTTP client interface for API operations."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class ApiResponse:
    """Response from an API call."""

    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return not self.is_success


class HttpClient(ABC):
    """Abstract interface for HTTP client operations."""

    @abstractmethod
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async GET request."""
        pass

    @abstractmethod
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async POST request."""
        pass

    @abstractmethod
    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async PUT request."""
        pass

    @abstractmethod
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> ApiResponse:
        """Perform an async DELETE request."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources (close sessions, etc.)."""
        pass
