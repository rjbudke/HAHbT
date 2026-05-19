"""Storage manager for HAHbT."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
import re
from typing import Any
from uuid import uuid4

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    STATUS_ACTIVE,
    STATUS_ARCHIVED,
    STATUS_INACTIVE,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .models import Habit, HabitEvent

_SLUGIFY_PATTERN = re.compile(r"[^a-z0-9]+")
_VALID_STATUSES = {STATUS_ACTIVE, STATUS_INACTIVE, STATUS_ARCHIVED}


class HahbtStorage:
    """Persist and query habit data."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.habits: dict[str, Habit] = {}
        self.events: dict[str, HabitEvent] = {}

    async def async_load(self) -> None:
        stored = await self._store.async_load() or {}
        habits = stored.get("habits", {})
        events = stored.get("events", {})
        self.habits = {
            habit_id: Habit.from_storage_dict(habit_data)
            for habit_id, habit_data in habits.items()
        }
        self.events = {
            event_id: HabitEvent.from_storage_dict(event_data)
            for event_id, event_data in events.items()
        }

    async def async_save(self) -> None:
        await self._store.async_save(
            {
                "version": STORAGE_VERSION,
                "habits": {
                    habit_id: habit.as_storage_dict()
                    for habit_id, habit in self.habits.items()
                },
                "events": {
                    event_id: event.as_storage_dict()
                    for event_id, event in self.events.items()
                },
            }
        )

    def async_snapshot(self) -> dict[str, Any]:
        habits = sorted(self.habits.values(), key=lambda habit: habit.name.lower())
        events_by_habit: dict[str, list[HabitEvent]] = defaultdict(list)
        for event in self.events.values():
            events_by_habit[event.habit_id].append(event)
        for habit_events in events_by_habit.values():
            habit_events.sort(key=lambda event: event.occurred_at)
        return {
            "habits": habits,
            "events_by_habit": dict(events_by_habit),
        }

    async def async_create_habit(
        self,
        *,
        name: str,
        icon: str | None = None,
        notes: str | None = None,
    ) -> Habit:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Habit name is required")
        if self._find_habit_by_name(normalized_name) is not None:
            raise ValueError(f"Habit '{normalized_name}' already exists")

        habit = Habit(
            habit_id=f"habit_{uuid4().hex}",
            name=normalized_name,
            slug=self._slugify(normalized_name),
            icon=icon,
            notes=notes,
            created_at=datetime.now(UTC),
        )
        self.habits[habit.habit_id] = habit
        await self.async_save()
        return habit

    async def async_update_habit(
        self,
        *,
        habit_id: str,
        name: str | None = None,
        icon: str | None = None,
        notes: str | None = None,
        status: str | None = None,
    ) -> Habit:
        habit = self._get_habit(habit_id)

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("Habit name cannot be blank")
            existing = self._find_habit_by_name(normalized_name)
            if existing is not None and existing.habit_id != habit_id:
                raise ValueError(f"Habit '{normalized_name}' already exists")
            habit.name = normalized_name
            habit.slug = self._slugify(normalized_name)

        if icon is not None:
            habit.icon = icon or None
        if notes is not None:
            habit.notes = notes or None
        if status is not None:
            if status not in _VALID_STATUSES:
                raise ValueError(f"Invalid habit status '{status}'")
            habit.status = status

        await self.async_save()
        return habit

    async def async_archive_habit(self, habit_id: str) -> Habit:
        habit = self._get_habit(habit_id)
        habit.status = STATUS_ARCHIVED
        await self.async_save()
        return habit

    async def async_log_event(
        self,
        *,
        habit_id: str,
        source: str,
        occurred_at: datetime | None = None,
        note: str | None = None,
    ) -> HabitEvent:
        habit = self._get_habit(habit_id)
        if habit.status != STATUS_ACTIVE:
            raise ValueError(
                f"Habit '{habit.name}' is {habit.status} and cannot be logged until reactivated"
            )

        event = HabitEvent(
            event_id=f"event_{uuid4().hex}",
            habit_id=habit_id,
            occurred_at=occurred_at or datetime.now(UTC),
            logged_at=datetime.now(UTC),
            source=source,
            note=note,
        )
        self.events[event.event_id] = event
        await self.async_save()
        return event

    def _get_habit(self, habit_id: str) -> Habit:
        if habit_id not in self.habits:
            raise ValueError(f"Unknown habit_id '{habit_id}'")
        return self.habits[habit_id]

    def _find_habit_by_name(self, name: str) -> Habit | None:
        lowered = name.casefold()
        for habit in self.habits.values():
            if habit.name.casefold() == lowered:
                return habit
        return None

    def _slugify(self, value: str) -> str:
        lowered = value.strip().lower()
        slug = _SLUGIFY_PATTERN.sub("_", lowered).strip("_")
        return slug or f"habit_{uuid4().hex[:8]}"
