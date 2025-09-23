"""API services package for Galileo traces and DigitalOcean integration."""

# Core interfaces
from .http_client import HttpClient, ApiResponse
from .traces_service import (
    TracesService,
    TraceRequest,
    Trace,
    TracesTokenResponse,
    TraceStatus,
)
from .auth import AuthProvider, ApiCredentials, BearerTokenAuthProvider

# Implementations
from .aiohttp_client import AioHttpClient
from .digitalocean_traces import DigitalOceanTracesService

# Factory for easy instantiation
from .factory import ApiServiceFactory

__all__ = [
    # Core interfaces
    "HttpClient",
    "ApiResponse",
    "TracesService",
    "TraceRequest",
    "Trace",
    "TracesTokenResponse",
    "TraceStatus",
    "AuthProvider",
    "ApiCredentials",
    # Implementations
    "AioHttpClient",
    "BearerTokenAuthProvider",
    "DigitalOceanTracesService",
    # Factory
    "ApiServiceFactory",
]
