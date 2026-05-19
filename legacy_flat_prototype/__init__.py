# custom_components/hahbt/__init__.py

import logging
from datetime import timezone
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the HAHbT component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HAHbT from a config entry."""
    habit_id = entry.data["habit_id"]
    habit_name = entry.data["habit_name"]

    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_{habit_id}.json")
    data = await store.async_load()
    if data is None:
        data = {"timestamps": []}
    else:
        # Migrate existing timestamps to include timezone info if missing
        timestamps = data.get("timestamps", [])
        updated = False
        for i, ts in enumerate(timestamps):
            parsed_ts = dt_util.parse_datetime(ts)
            if parsed_ts is None:
                # Try appending "+00:00" to assume UTC
                ts_with_tz = ts + "+00:00"
                parsed_ts = dt_util.parse_datetime(ts_with_tz)
                if parsed_ts is None:
                    _LOGGER.warning("Could not parse timestamp '%s' during migration", ts)
                    continue
                else:
                    parsed_ts = parsed_ts.replace(tzinfo=dt_util.UTC)
                    timestamps[i] = parsed_ts.isoformat()
                    updated = True
            elif parsed_ts.tzinfo is None:
                # Assume UTC if no timezone info
                parsed_ts = parsed_ts.replace(tzinfo=dt_util.UTC)
                timestamps[i] = parsed_ts.isoformat()
                updated = True
            else:
                # Normalize to UTC
                parsed_ts = parsed_ts.astimezone(dt_util.UTC)
                timestamps[i] = parsed_ts.isoformat()
                updated = True
        if updated:
            _LOGGER.info("Migrated timestamps for habit '%s' to include timezone info.", habit_name)
            await store.async_save({"timestamps": timestamps})

    # Include 'habit_id' in habit_data
    hass.data[DOMAIN][habit_id] = {
        "habit_id": habit_id,
        "habit_name": habit_name,
        "timestamps": data["timestamps"],
        "store": store,
        "sensors": [],
    }

    # Forward setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Define the service handler inside async_setup_entry
    async def handle_log_habit(call):
        """Handle the service call to log a habit."""
        habit_id_call = call.data.get("habit_id")

        if habit_id_call not in hass.data[DOMAIN]:
            _LOGGER.error("Habit ID %s not found", habit_id_call)
            return

        habit_data = hass.data[DOMAIN][habit_id_call]
        timestamps = habit_data["timestamps"]
        now = dt_util.utcnow()
        now_iso = now.isoformat()
        timestamps.append(now_iso)

        # Save updated timestamps
        await habit_data["store"].async_save({"timestamps": timestamps})

        # Update sensors
        for sensor in habit_data.get("sensors", []):
            sensor.async_schedule_update_ha_state(True)

    # Register the service if not already registered
    if f"{DOMAIN}.log_habit" not in hass.services.async_services().get(DOMAIN, {}):
        hass.services.async_register(DOMAIN, "log_habit", handle_log_habit)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a HAHbT config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    habit_id = entry.data["habit_id"]
    hass.data[DOMAIN].pop(habit_id)
    return True