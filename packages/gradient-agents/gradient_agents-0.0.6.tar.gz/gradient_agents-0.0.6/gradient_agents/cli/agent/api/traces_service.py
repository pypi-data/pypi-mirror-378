"""Galileo traces service interface and data models."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class TraceStatus(Enum):
    """Status of a trace."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TraceRequest:
    """Request to create a new trace."""

    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


@dataclass
class Trace:
    """Represents a Galileo trace."""

    id: str
    name: str
    status: TraceStatus
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    token: Optional[str] = None  # Traces token for this specific trace

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trace":
        """Create a Trace from API response data."""
        status = TraceStatus(data.get("status", "pending"))
        return cls(
            id=data["id"],
            name=data["name"],
            status=status,
            description=data.get("description"),
            metadata=data.get("metadata"),
            tags=data.get("tags"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            token=data.get("token"),
        )


@dataclass
class TracesTokenResponse:
    """Response containing traces token information."""

    token: str
    expires_at: Optional[str] = None
    trace_id: Optional[str] = None
    permissions: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TracesTokenResponse":
        """Create a TracesTokenResponse from API response data."""
        return cls(
            token=data["token"],
            expires_at=data.get("expires_at"),
            trace_id=data.get("trace_id"),
            permissions=data.get("permissions", []),
        )


class TracesService(ABC):
    """Abstract interface for Galileo traces operations."""

    @abstractmethod
    async def create_trace(self, trace_request: TraceRequest) -> Trace:
        """Create a new trace."""
        pass

    @abstractmethod
    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID."""
        pass

    @abstractmethod
    async def list_traces(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[TraceStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Trace]:
        """List traces with optional filtering."""
        pass

    @abstractmethod
    async def get_traces_token(
        self, trace_id: Optional[str] = None
    ) -> TracesTokenResponse:
        """Get a traces token for accessing trace data."""
        pass

    @abstractmethod
    async def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace. Returns True if successful."""
        pass

    @abstractmethod
    async def update_trace(
        self,
        trace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Trace:
        """Update an existing trace."""
        pass
