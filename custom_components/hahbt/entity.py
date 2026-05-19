"""Shared entity helpers for HAHbT."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_ARCHIVED
from .coordinator import HahbtCoordinator
from .models import Habit


class HahbtHabitEntity(CoordinatorEntity[HahbtCoordinator]):
    """Base entity tied to a habit."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HahbtCoordinator, habit: Habit) -> None:
        super().__init__(coordinator)
        self.habit_id = habit.habit_id

    @property
    def habit(self) -> Habit:
        return next(
            habit
            for habit in self.coordinator.data["habits"]
            if habit.habit_id == self.habit_id
        )

    @property
    def available(self) -> bool:
        return super().available and self.habit.status != STATUS_ARCHIVED

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"status": self.habit.status}

    @property
    def device_info(self) -> DeviceInfo:
        habit = self.habit
        return DeviceInfo(
            identifiers={(DOMAIN, self.habit_id)},
            name=habit.name,
            manufacturer="HAHbT",
            model="Habit Stream",
        )
