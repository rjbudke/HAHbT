"""The HAHbT integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DATA_COORDINATOR, DOMAIN, PLATFORMS
from .coordinator import HahbtCoordinator
from .services import async_register_services, async_unregister_services

HahbtConfigEntry = ConfigEntry[HahbtCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: HahbtConfigEntry) -> bool:
    """Set up HAHbT from a config entry."""

    coordinator = HahbtCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.data[DOMAIN][DATA_COORDINATOR] = coordinator

    await async_register_services(hass, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HahbtConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    domain_data = hass.data[DOMAIN]
    domain_data.pop(entry.entry_id)
    if len([key for key in domain_data if key != DATA_COORDINATOR]) == 0:
        await async_unregister_services(hass)
        domain_data.pop(DATA_COORDINATOR, None)

    return True
