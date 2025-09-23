"""DigitalOcean API implementation for Galileo traces service."""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from .traces_service import (
    TracesService,
    TraceRequest,
    Trace,
    TracesTokenResponse,
    TraceStatus,
)
from .http_client import HttpClient, ApiResponse
from .auth import AuthProvider


class DigitalOceanTracesService(TracesService):
    """DigitalOcean API implementation of Galileo traces service."""

    def __init__(
        self,
        http_client: HttpClient,
        auth_provider: AuthProvider,
        base_url: str = "https://api.digitalocean.com/v2/",
        traces_endpoint: str = "galileo/traces",
    ):
        self.http_client = http_client
        self.auth_provider = auth_provider
        self.base_url = base_url.rstrip("/") + "/"
        self.traces_endpoint = traces_endpoint

    def _build_url(self, path: str) -> str:
        """Build full URL for API endpoint."""
        return urljoin(self.base_url, f"{self.traces_endpoint}/{path.lstrip('/')}")

    def _get_headers(
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Get headers with authentication."""
        if not self.auth_provider.is_authenticated():
            raise ValueError("Authentication provider is not authenticated")

        headers = self.auth_provider.get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)
        return headers

    async def create_trace(self, trace_request: TraceRequest) -> Trace:
        """Create a new trace."""
        url = self._build_url("")
        headers = self._get_headers()

        payload = {
            "name": trace_request.name,
        }
        if trace_request.description:
            payload["description"] = trace_request.description
        if trace_request.metadata:
            payload["metadata"] = trace_request.metadata
        if trace_request.tags:
            payload["tags"] = trace_request.tags

        response = await self.http_client.post(url, json=payload, headers=headers)

        if not response.is_success:
            raise Exception(f"Failed to create trace: {response.error}")

        if not response.data:
            raise Exception("No data returned from create trace API")

        return Trace.from_dict(response.data)

    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID."""
        url = self._build_url(trace_id)
        headers = self._get_headers()

        response = await self.http_client.get(url, headers=headers)

        if response.status_code == 404:
            return None

        if not response.is_success:
            raise Exception(f"Failed to get trace {trace_id}: {response.error}")

        if not response.data:
            return None

        return Trace.from_dict(response.data)

    async def list_traces(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[TraceStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Trace]:
        """List traces with optional filtering."""
        url = self._build_url("")
        headers = self._get_headers()

        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status is not None:
            params["status"] = status.value
        if tags:
            params["tags"] = ",".join(tags)

        response = await self.http_client.get(url, headers=headers, params=params)

        if not response.is_success:
            raise Exception(f"Failed to list traces: {response.error}")

        if not response.data:
            return []

        # Handle both direct array and wrapped array formats
        traces_data = response.data
        if isinstance(traces_data, dict) and "traces" in traces_data:
            traces_data = traces_data["traces"]
        elif isinstance(traces_data, dict) and "data" in traces_data:
            traces_data = traces_data["data"]

        if not isinstance(traces_data, list):
            return []

        return [Trace.from_dict(trace_data) for trace_data in traces_data]

    async def get_traces_token(
        self, trace_id: Optional[str] = None
    ) -> TracesTokenResponse:
        """Get a traces token for accessing trace data."""
        path = f"token"
        if trace_id:
            path = f"{trace_id}/token"

        url = self._build_url(path)
        headers = self._get_headers()

        response = await self.http_client.get(url, headers=headers)

        if not response.is_success:
            raise Exception(f"Failed to get traces token: {response.error}")

        if not response.data:
            raise Exception("No data returned from traces token API")

        return TracesTokenResponse.from_dict(response.data)

    async def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace. Returns True if successful."""
        url = self._build_url(trace_id)
        headers = self._get_headers()

        response = await self.http_client.delete(url, headers=headers)

        if response.status_code == 404:
            return False  # Already deleted or never existed

        return response.is_success

    async def update_trace(
        self,
        trace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Trace:
        """Update an existing trace."""
        url = self._build_url(trace_id)
        headers = self._get_headers()

        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        if tags is not None:
            payload["tags"] = tags

        if not payload:
            # No updates requested, just return current trace
            current_trace = await self.get_trace(trace_id)
            if not current_trace:
                raise Exception(f"Trace {trace_id} not found")
            return current_trace

        response = await self.http_client.put(url, json=payload, headers=headers)

        if not response.is_success:
            raise Exception(f"Failed to update trace {trace_id}: {response.error}")

        if not response.data:
            raise Exception("No data returned from update trace API")

        return Trace.from_dict(response.data)
