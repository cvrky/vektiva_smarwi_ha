"""Platform for light integration."""
import logging
import time

import voluptuous

import homeassistant.helpers.config_validation
# Import the device class from the component that you want to support
from homeassistant.components.cover import PLATFORM_SCHEMA, CoverEntity, DEVICE_CLASS_WINDOW, ATTR_POSITION
from homeassistant.components.cover import SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_SET_POSITION
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
class VektivaSmarwi(CoverEntity):
    def __init__(self, ctli: SmarwiControlItem):
        self._ctli = ctli
        self._name = None
        self._id = None
        self._fw = None
        self._opening = None
        self._closing = None
        self._closed = None
        self._position = 0
        self._requested_position = 0
        self.__last_change = time.time()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def device_info(self):
        return {
            'identifiers': {("cover", self._id)},
            'name': self._name,
            'manufacturer': 'Vektiva',
            'model': "Smarwi",
            'sw_version': self._fw
        }

    @property
    def device_class(self):
        return DEVICE_CLASS_WINDOW

    @property
    def supported_features(self):
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION

    @property
    def current_cover_position(self):
        return self._position

    @property
    def is_opening(self):
        return self._opening

    @property
    def is_closing(self):
        return self._closing

    @property
    def is_closed(self):
        return self._closed

    async def async_open_cover(self, **kwargs):
        """Open window."""
        self.__last_change = time.time()
        self._requested_position = 100
        await self._ctli.open()

    async def async_close_cover(self, **kwargs):
        """Close window."""
        self.__last_change = time.time()
        self._requested_position = 0
        await self._ctli.close()

    async def async_set_cover_position(self, **kwargs):
        """Move the window to a specific position."""
        self.__last_change = time.time()
        self._requested_position = int(kwargs[ATTR_POSITION])
        await self._ctli.set_position(self._requested_position)

    async def async_update(self):
        response = await self._ctli.get_status()
        if not self._id:
            self._id = response["id"]
            self._name = response["cid"]
            self._fw = response["fw"]
        if response["pos"] == 'c':
            self._position = 0
            self._closed = True
            self._opening = False
            self._closing = False
        elif response["pos"] == 'o':
            if self.__last_change > time.time() - 11:
                if self._position > self._requested_position:
                    self._closed = False
                    self._opening = False
                    self._closing = True
                else:
                    self._closed = False
                    self._opening = True
                    self._closing = False
            else:
                self._position = self._requested_position
                self._closed = False
                self._opening = False
                self._closing = False
