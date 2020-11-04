"""Config flow for Vektiva Smarwi integration."""
import logging

import voluptuous

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOSTS

from .smarwi_control import SmarwiControl
from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = voluptuous.Schema({CONF_HOSTS: str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    ctl = SmarwiControl(data[CONF_HOSTS])

    if not await ctl.authenticate():
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": ctl.title}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vektiva Smarwi."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
