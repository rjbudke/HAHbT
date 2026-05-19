"""Config flow for HAHbT."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class HahbtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HAHbT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create the single integration entry."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="HAHbT",
            data={},
        )
