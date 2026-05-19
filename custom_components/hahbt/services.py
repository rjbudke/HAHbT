"""Service handlers for HAHbT."""

from __future__ import annotations

from datetime import UTC, datetime

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    CONF_HABIT_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_NOTE,
    CONF_NOTES,
    CONF_OCCURRED_AT,
    CONF_STATUS,
    DATA_COORDINATOR,
    DATA_SERVICES_REGISTERED,
    DOMAIN,
    SERVICE_ARCHIVE_HABIT,
    SERVICE_CREATE_HABIT,
    SERVICE_LOG_EVENT,
    SERVICE_UPDATE_HABIT,
    SOURCE_BUTTON,
    SOURCE_SERVICE,
    STATUS_ACTIVE,
    STATUS_ARCHIVED,
    STATUS_INACTIVE,
)
from .coordinator import HahbtCoordinator

CREATE_HABIT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_ICON): vol.Any(None, cv.string),
        vol.Optional(CONF_NOTES): vol.Any(None, cv.string),
    }
)

UPDATE_HABIT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HABIT_ID): cv.string,
        vol.Optional(CONF_NAME): vol.Any(None, cv.string),
        vol.Optional(CONF_ICON): vol.Any(None, cv.string),
        vol.Optional(CONF_NOTES): vol.Any(None, cv.string),
        vol.Optional(CONF_STATUS): vol.In(
            [STATUS_ACTIVE, STATUS_INACTIVE, STATUS_ARCHIVED]
        ),
    }
)

ARCHIVE_HABIT_SCHEMA = vol.Schema({vol.Required(CONF_HABIT_ID): cv.string})

LOG_EVENT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HABIT_ID): cv.string,
        vol.Optional(CONF_OCCURRED_AT): vol.Any(None, cv.datetime),
        vol.Optional(CONF_NOTE): vol.Any(None, cv.string),
    }
)


async def async_register_services(hass: HomeAssistant, coordinator: HahbtCoordinator) -> None:
    """Register the HAHbT services exactly once."""

    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(DATA_SERVICES_REGISTERED):
        return

    async def handle_create_habit(call: ServiceCall) -> None:
        await coordinator.storage.async_create_habit(
            name=call.data[CONF_NAME],
            icon=call.data.get(CONF_ICON),
            notes=call.data.get(CONF_NOTES),
        )
        await coordinator.async_request_refresh()

    async def handle_update_habit(call: ServiceCall) -> None:
        await coordinator.storage.async_update_habit(
            habit_id=call.data[CONF_HABIT_ID],
            name=call.data.get(CONF_NAME),
            icon=call.data.get(CONF_ICON),
            notes=call.data.get(CONF_NOTES),
            status=call.data.get(CONF_STATUS),
        )
        await coordinator.async_request_refresh()

    async def handle_archive_habit(call: ServiceCall) -> None:
        await coordinator.storage.async_archive_habit(call.data[CONF_HABIT_ID])
        await coordinator.async_request_refresh()

    async def handle_log_event(call: ServiceCall) -> None:
        occurred_at = _normalize_datetime(call.data.get(CONF_OCCURRED_AT))
        await coordinator.storage.async_log_event(
            habit_id=call.data[CONF_HABIT_ID],
            occurred_at=occurred_at,
            note=call.data.get(CONF_NOTE),
            source=SOURCE_SERVICE,
        )
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_HABIT,
        handle_create_habit,
        schema=CREATE_HABIT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_HABIT,
        handle_update_habit,
        schema=UPDATE_HABIT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ARCHIVE_HABIT,
        handle_archive_habit,
        schema=ARCHIVE_HABIT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_EVENT,
        handle_log_event,
        schema=LOG_EVENT_SCHEMA,
    )

    domain_data[DATA_COORDINATOR] = coordinator
    domain_data[DATA_SERVICES_REGISTERED] = True


async def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove services when the last config entry unloads."""

    domain_data = hass.data.get(DOMAIN)
    if not domain_data or not domain_data.get(DATA_SERVICES_REGISTERED):
        return

    for service in (
        SERVICE_CREATE_HABIT,
        SERVICE_UPDATE_HABIT,
        SERVICE_ARCHIVE_HABIT,
        SERVICE_LOG_EVENT,
    ):
        hass.services.async_remove(DOMAIN, service)

    domain_data[DATA_SERVICES_REGISTERED] = False


async def async_log_button_event(
    coordinator: HahbtCoordinator,
    habit_id: str,
) -> None:
    """Helper used by button entities to log an immediate event."""

    await coordinator.storage.async_log_event(habit_id=habit_id, source=SOURCE_BUTTON)
    await coordinator.async_request_refresh()


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return dt_util.as_utc(value)
    return value.astimezone(UTC)
