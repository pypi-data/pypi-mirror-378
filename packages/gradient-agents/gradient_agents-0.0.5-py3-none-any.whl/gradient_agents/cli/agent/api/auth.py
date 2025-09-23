"""Authentication and token management for API services."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os


@dataclass
class ApiCredentials:
    """API credentials for authentication."""

    api_token: str
    base_url: Optional[str] = None

    @classmethod
    def from_environment(
        cls, token_env_var: str = "API_TOKEN", base_url_env_var: str = "API_BASE_URL"
    ) -> "ApiCredentials":
        """Create credentials from environment variables."""
        api_token = os.getenv(token_env_var)
        if not api_token:
            raise ValueError(
                f"API token not found in environment variable '{token_env_var}'"
            )

        base_url = os.getenv(base_url_env_var)
        return cls(api_token=api_token, base_url=base_url)


class AuthProvider(ABC):
    """Abstract interface for authentication providers."""

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if the provider has valid authentication."""
        pass


class BearerTokenAuthProvider(AuthProvider):
    """Bearer token authentication provider."""

    def __init__(self, credentials: ApiCredentials):
        self.credentials = credentials
        self._base_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credentials.api_token}",
        }

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return self._base_headers.copy()

    def is_authenticated(self) -> bool:
        """Check if the provider has valid authentication."""
        return bool(self.credentials.api_token)

    def add_custom_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add custom headers to the base auth headers."""
        merged_headers = self.get_auth_headers()
        merged_headers.update(headers)
        return merged_headers
