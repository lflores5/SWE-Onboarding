"""Pydantic models for ticket data used by the API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    """Possible lifecycle states for a ticket."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


def now_utc_iso() -> str:
    """Return the current UTC time as an ISO 8601 formatted string."""
    return datetime.now(timezone.utc).isoformat()


class TicketBase(BaseModel):
    """Fields shared by all ticket representations."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: TicketStatus = TicketStatus.OPEN


class TicketCreate(TicketBase):
    """Payload for creating a new ticket."""


class TicketUpdate(BaseModel):
    """Payload for partially updating an existing ticket."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[TicketStatus] = None


class Ticket(TicketBase):
    """Full ticket representation returned by the API."""

    id: str
    created_at: str
    updated_at: str
