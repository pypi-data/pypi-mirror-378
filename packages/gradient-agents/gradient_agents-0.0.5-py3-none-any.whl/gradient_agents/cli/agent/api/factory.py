"""Factory for creating API service instances."""

from __future__ import annotations
from typing import Optional

from .http_client import HttpClient
from .aiohttp_client import AioHttpClient
from .auth import AuthProvider, BearerTokenAuthProvider, ApiCredentials
from .traces_service import TracesService
from .digitalocean_traces import DigitalOceanTracesService


class ApiServiceFactory:
    """Factory for creating API service instances with proper configuration."""

    @staticmethod
    def create_http_client(
        default_timeout: float = 30.0,
        connector_limit: int = 100,
    ) -> HttpClient:
        """Create a default HTTP client."""
        return AioHttpClient(
            default_timeout=default_timeout,
            connector_limit=connector_limit,
        )

    @staticmethod
    def create_auth_provider_from_env(
        token_env_var: str = "API_TOKEN",
        base_url_env_var: str = "API_BASE_URL",
    ) -> AuthProvider:
        """Create an auth provider from environment variables."""
        credentials = ApiCredentials.from_environment(token_env_var, base_url_env_var)
        return BearerTokenAuthProvider(credentials)

    @staticmethod
    def create_auth_provider(
        api_token: str, base_url: Optional[str] = None
    ) -> AuthProvider:
        """Create an auth provider with explicit credentials."""
        credentials = ApiCredentials(api_token=api_token, base_url=base_url)
        return BearerTokenAuthProvider(credentials)

    @staticmethod
    def create_digitalocean_traces_service(
        api_token: str,
        base_url: str = "https://api.digitalocean.com/v2/",
        http_client: Optional[HttpClient] = None,
        auth_provider: Optional[AuthProvider] = None,
    ) -> TracesService:
        """Create a DigitalOcean traces service with default configuration."""
        if http_client is None:
            http_client = ApiServiceFactory.create_http_client()

        if auth_provider is None:
            auth_provider = ApiServiceFactory.create_auth_provider(api_token, base_url)

        return DigitalOceanTracesService(
            http_client=http_client,
            auth_provider=auth_provider,
            base_url=base_url,
        )

    @staticmethod
    def create_digitalocean_traces_service_from_env(
        token_env_var: str = "DO_API_TOKEN",
        base_url_env_var: str = "DO_API_BASE_URL",
        default_base_url: str = "https://api.digitalocean.com/v2/",
        http_client: Optional[HttpClient] = None,
    ) -> TracesService:
        """Create a DigitalOcean traces service from environment variables."""
        if http_client is None:
            http_client = ApiServiceFactory.create_http_client()

        try:
            auth_provider = ApiServiceFactory.create_auth_provider_from_env(
                token_env_var, base_url_env_var
            )
            # Use base URL from credentials if available, otherwise default
            base_url = auth_provider.credentials.base_url or default_base_url
        except ValueError:
            # Fallback to individual environment variable lookup
            import os

            api_token = os.getenv(token_env_var)
            if not api_token:
                raise ValueError(
                    f"API token not found in environment variable '{token_env_var}'"
                )

            base_url = os.getenv(base_url_env_var, default_base_url)
            auth_provider = ApiServiceFactory.create_auth_provider(api_token, base_url)

        return DigitalOceanTracesService(
            http_client=http_client,
            auth_provider=auth_provider,
            base_url=base_url,
        )
