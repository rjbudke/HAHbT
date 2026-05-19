"""Button platform for HAHbT."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUS_ACTIVE
from .coordinator import HahbtCoordinator
from .entity import HahbtHabitEntity
from .services import async_log_button_event


def should_expose_log_button(status: str) -> bool:
    """Return whether a habit status should expose a quick-log button."""

    return status == STATUS_ACTIVE


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HAHbT buttons."""

    coordinator: HahbtCoordinator = entry.runtime_data
    known_habits: set[str] = set()

    def add_missing_entities() -> None:
        new_entities: list[HabitLogButton] = []
        for habit in coordinator.data["habits"]:
            if not should_expose_log_button(habit.status) or habit.habit_id in known_habits:
                continue
            known_habits.add(habit.habit_id)
            new_entities.append(HabitLogButton(coordinator, habit))
        if new_entities:
            async_add_entities(new_entities)

    add_missing_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_missing_entities))


class HabitLogButton(HahbtHabitEntity, ButtonEntity):
    """Quick-log button for a habit."""

    def __init__(self, coordinator: HahbtCoordinator, habit) -> None:
        super().__init__(coordinator, habit)
        self._attr_name = "Log"
        self._attr_unique_id = f"{self.habit_id}_log"
        self._attr_icon = habit.icon or "mdi:plus-circle"

    async def async_press(self) -> None:
        await async_log_button_event(self.coordinator, self.habit_id)
