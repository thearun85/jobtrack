from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(tz=UTC)


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    application_id: UUID
    occurred_at: datetime
    recorded_at: datetime = _now()
    version: int = 1


class Applied(BaseEvent):
    event_type: Literal["applied"] = "applied"


class Rejected(BaseEvent):
    event_type: Literal["rejected"] = "rejected"
    reason: str | None = None


class Ghosted(BaseEvent):
    event_type: Literal["ghosted"] = "ghosted"
