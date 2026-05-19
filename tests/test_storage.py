"""Tests for HAHbT storage behavior."""

from __future__ import annotations

from datetime import UTC, datetime
import unittest

from _ha_stubs import install

install()

from custom_components.hahbt.const import (
    STATUS_ACTIVE,
    STATUS_ARCHIVED,
    STATUS_INACTIVE,
)
from custom_components.hahbt.models import Habit
from custom_components.hahbt.storage import HahbtStorage


class HahbtStorageTests(unittest.IsolatedAsyncioTestCase):
    """Cover core storage lifecycle and logging rules."""

    def setUp(self) -> None:
        self.storage = HahbtStorage.__new__(HahbtStorage)
        self.storage.hass = None
        self.storage.habits = {}
        self.storage.events = {}

        async def async_save() -> None:
            return None

        self.storage.async_save = async_save

    async def test_create_habit_defaults_to_active(self) -> None:
        habit = await self.storage.async_create_habit(name="Mow Lawn")

        self.assertEqual(habit.status, STATUS_ACTIVE)
        self.assertEqual(habit.slug, "mow_lawn")
        self.assertIn(habit.habit_id, self.storage.habits)

    async def test_log_event_allowed_for_active_habit(self) -> None:
        habit = await self.storage.async_create_habit(name="Haircut")

        event = await self.storage.async_log_event(
            habit_id=habit.habit_id,
            source="service",
        )

        self.assertEqual(event.habit_id, habit.habit_id)
        self.assertEqual(len(self.storage.events), 1)

    async def test_log_event_blocked_for_inactive_habit(self) -> None:
        habit = Habit(
            habit_id="habit_inactive",
            name="Vaped",
            slug="vaped",
            created_at=datetime.now(UTC),
            status=STATUS_INACTIVE,
        )
        self.storage.habits[habit.habit_id] = habit

        with self.assertRaisesRegex(ValueError, "inactive"):
            await self.storage.async_log_event(
                habit_id=habit.habit_id,
                source="service",
            )

    async def test_log_event_blocked_for_archived_habit(self) -> None:
        habit = Habit(
            habit_id="habit_archived",
            name="Trimmed Fingernails",
            slug="trimmed_fingernails",
            created_at=datetime.now(UTC),
            status=STATUS_ARCHIVED,
        )
        self.storage.habits[habit.habit_id] = habit

        with self.assertRaisesRegex(ValueError, "archived"):
            await self.storage.async_log_event(
                habit_id=habit.habit_id,
                source="service",
            )

    async def test_update_habit_can_change_status(self) -> None:
        habit = await self.storage.async_create_habit(name="Pooped")

        updated = await self.storage.async_update_habit(
            habit_id=habit.habit_id,
            status=STATUS_INACTIVE,
        )

        self.assertEqual(updated.status, STATUS_INACTIVE)
