"""Typed models for HAHbT."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .const import STATUS_ACTIVE


@dataclass(slots=True)
class Habit:
    """A tracked habit stream."""

    habit_id: str
    name: str
    slug: str
    created_at: datetime
    status: str = STATUS_ACTIVE
    icon: str | None = None
    notes: str | None = None

    def as_storage_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_storage_dict(cls, data: dict[str, Any]) -> "Habit":
        return cls(
            habit_id=data["habit_id"],
            name=data["name"],
            slug=data["slug"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=data.get("status", STATUS_ACTIVE),
            icon=data.get("icon"),
            notes=data.get("notes"),
        )


@dataclass(slots=True)
class HabitEvent:
    """A single logged habit event."""

    event_id: str
    habit_id: str
    occurred_at: datetime
    logged_at: datetime
    source: str
    note: str | None = None

    def as_storage_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["occurred_at"] = self.occurred_at.isoformat()
        data["logged_at"] = self.logged_at.isoformat()
        return data

    @classmethod
    def from_storage_dict(cls, data: dict[str, Any]) -> "HabitEvent":
        return cls(
            event_id=data["event_id"],
            habit_id=data["habit_id"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            logged_at=datetime.fromisoformat(data["logged_at"]),
            source=data["source"],
            note=data.get("note"),
        )
