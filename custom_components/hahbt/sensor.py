"""Sensor platform for HAHbT."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import STATUS_ARCHIVED
from .coordinator import HahbtCoordinator
from .entity import HahbtHabitEntity
from .models import Habit, HabitEvent


@dataclass(frozen=True, slots=True)
class HabitSensorDescription:
    """Describe a habit sensor."""

    key: str
    name: str
    icon: str | None
    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None
    native_unit_of_measurement: str | None
    value_fn: Callable[[datetime, list[HabitEvent]], Any]


SENSOR_TYPES: tuple[HabitSensorDescription, ...] = (
    HabitSensorDescription(
        key="latest_occurrence",
        name="Latest Occurrence",
        icon="mdi:clock-check-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=None,
        native_unit_of_measurement=None,
        value_fn=lambda now, events: events[-1].occurred_at if events else None,
    ),
    HabitSensorDescription(
        key="time_since_last",
        name="Time Since Last",
        icon="mdi:timer-outline",
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        value_fn=lambda now, events: _time_since_last_hours(now, events),
    ),
    HabitSensorDescription(
        key="count_today",
        name="Count Today",
        icon="mdi:calendar-today",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,
        value_fn=lambda now, events: _count_today(now, events),
    ),
    HabitSensorDescription(
        key="count_this_week",
        name="Count This Week",
        icon="mdi:calendar-week",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,
        value_fn=lambda now, events: _count_this_week(now, events),
    ),
    HabitSensorDescription(
        key="count_total",
        name="Count Total",
        icon="mdi:counter",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,
        value_fn=lambda now, events: len(events),
    ),
    HabitSensorDescription(
        key="average_interval",
        name="Average Interval",
        icon="mdi:chart-timeline-variant",
        device_class=SensorDeviceClass.DURATION,
        state_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        value_fn=lambda now, events: _average_interval_hours(events),
    ),
)


def should_expose_metric_entities(status: str) -> bool:
    """Return whether a habit status should expose metric entities."""

    return status != STATUS_ARCHIVED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HAHbT sensors."""

    coordinator: HahbtCoordinator = entry.runtime_data
    known_entities: set[tuple[str, str]] = set()

    def add_missing_entities() -> None:
        new_entities: list[HabitMetricSensor] = []
        for habit in coordinator.data["habits"]:
            if not should_expose_metric_entities(habit.status):
                continue
            for description in SENSOR_TYPES:
                entity_key = (habit.habit_id, description.key)
                if entity_key in known_entities:
                    continue
                known_entities.add(entity_key)
                new_entities.append(HabitMetricSensor(coordinator, habit, description))
        if new_entities:
            async_add_entities(new_entities)

    add_missing_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_missing_entities))


class HabitMetricSensor(HahbtHabitEntity, SensorEntity):
    """Expose a computed metric for a habit."""

    def __init__(
        self,
        coordinator: HahbtCoordinator,
        habit: Habit,
        description: HabitSensorDescription,
    ) -> None:
        super().__init__(coordinator, habit)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{habit.habit_id}_{description.key}"
        self._attr_icon = description.icon
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self) -> Any:
        events = self.coordinator.data["events_by_habit"].get(self.habit_id, [])
        return self.entity_description.value_fn(dt_util.utcnow(), events)


def _time_since_last_hours(now: datetime, events: list[HabitEvent]) -> float | None:
    if not events:
        return None
    delta = now - events[-1].occurred_at.astimezone(UTC)
    return round(delta.total_seconds() / 3600, 2)


def _count_today(now: datetime, events: list[HabitEvent]) -> int:
    local_now = dt_util.as_local(now)
    today = local_now.date()
    return sum(1 for event in events if dt_util.as_local(event.occurred_at).date() == today)


def _count_this_week(now: datetime, events: list[HabitEvent]) -> int:
    local_now = dt_util.as_local(now)
    current_iso_week = local_now.isocalendar()[:2]
    return sum(
        1
        for event in events
        if dt_util.as_local(event.occurred_at).isocalendar()[:2] == current_iso_week
    )


def _average_interval_hours(events: list[HabitEvent]) -> float | None:
    if len(events) < 2:
        return None
    intervals = [
        (current.occurred_at - previous.occurred_at).total_seconds() / 3600
        for previous, current in zip(events, events[1:], strict=False)
    ]
    return round(mean(intervals), 2)
