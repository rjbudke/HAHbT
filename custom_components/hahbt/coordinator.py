"""Coordinator for HAHbT state."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_INTERVAL_SECONDS
from .storage import HahbtStorage

_LOGGER = logging.getLogger(__name__)


class HahbtCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate habit data snapshots for entities and services."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.storage = HahbtStorage(hass)
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def async_config_entry_first_refresh(self) -> None:
        await self.storage.async_load()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        return self.storage.async_snapshot()
