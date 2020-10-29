"""Platform for light integration."""
import logging
import time

import voluptuous

import homeassistant.helpers.config_validation
# Import the device class from the component that you want to support
from homeassistant.components.switch import PLATFORM_SCHEMA, ToggleEntity
from homeassistant.const import CONF_HOSTS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .smarwi_control import SmarwiControl, SmarwiControlItem

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Required(CONF_HOSTS): homeassistant.helpers.config_validation.string,
})


# noinspection PyUnusedLocal
def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOSTS]
    ctl = SmarwiControl(host)
    _LOGGER.error(f"=== {ctl.list()}")
    add_entities([VektivaSmarwi(host) for host in ctl.list()])


async def async_setup_entry(hass:HomeAssistant, config_entry:ConfigEntry, async_add_entities):
    ctl = SmarwiControl(config_entry.data["hosts"])
    async_add_entities([VektivaSmarwi(ctli) for ctli in ctl.list()], True)
    return True


# noinspection PyAbstractClass
class VektivaSmarwi(ToggleEntity):
    def __init__(self, ctli: SmarwiControlItem):
        self._ctli = ctli
        self._name = None
        self._id = None
        self._state = None
        self._fw = None
        self.__last_change = time.time()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def is_on(self):
        return self._state

    @property
    def device_info(self):
        return {
            'identifiers': {("switch", self._id)},
            'name': self._name,
            'manufacturer': 'Vektiva',
            'model': "Smarwi",
            'sw_version': self._fw
        }

    async def async_turn_on(self, **kwargs):
        self.__last_change = time.time()
        self._state = True
        await self._ctli.open()

    async def async_turn_off(self, **kwargs):
        self.__last_change = time.time()
        self._state = False
        await self._ctli.close()

    async def async_update(self):
        if self._state is None \
            or self.__last_change < time.time() - 11 \
                :
            response = await self._ctli.get_status()
            self._state = response["pos"] == 'o'
            if not self._id:
                self._id = response["id"]
                self._name = response["cid"]
                self._fw = response["fw"]
