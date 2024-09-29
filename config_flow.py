# custom_components/hahbt/config_flow.py

import uuid
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_HABIT_NAME, CONF_HABIT_ID

@config_entries.HANDLERS.register(DOMAIN)
class HahbtConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for HAHbT."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            habit_name = user_input[CONF_HABIT_NAME]
            habit_id = str(uuid.uuid4())

            await self.async_set_unique_id(habit_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=habit_name,
                data={
                    CONF_HABIT_NAME: habit_name,
                    CONF_HABIT_ID: habit_id,
                },
            )

        data_schema = vol.Schema({vol.Required(CONF_HABIT_NAME): str})

        return self.async_show_form(step_id="user", data_schema=data_schema)
