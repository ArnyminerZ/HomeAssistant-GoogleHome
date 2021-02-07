import json
import requests
from homeassistant.helpers.entity import Entity
from typing import Callable, Optional, Dict, Any

from glocaltokens.client import GLocalAuthenticationTokens

import logging
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_NAME,
    ATTR_ICON,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_IP_ADDRESS,
    CONF_FRIENDLY_NAME,
    CONF_DEVICES,
    CONF_PATH
)
from homeassistant.helpers import ConfigType
from homeassistant.helpers.typing import HomeAssistantType, DiscoveryInfoType

from .const import (
    DOMAIN
)

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_FRIENDLY_NAME): cv.string,
        vol.Required(CONF_PATH): cv.string
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: core.HomeAssistant,
        config_entry: config_entries.ConfigEntry,
        async_add_entities,
):
    """Set up the sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    client = GLocalAuthenticationTokens(
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD]
    )
    sensors = [GoogleHomeVolumeSensor(client, device) for device in config[CONF_DEVICES]]
    async_add_entities(sensors, update_before_end=True)


async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    client = GLocalAuthenticationTokens(
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD]
    )
    sensors = [GoogleHomeVolumeSensor(client, device) for device in config[CONF_DEVICES]]
    async_add_entities(sensors, update_before_end=True)


class GoogleHomeVolumeSensor(Entity):
    """Representation of a Google Home device"""

    def __init__(self, client: GLocalAuthenticationTokens, device: Dict[str, str, str]):
        super().__init__()
        self.client = client
        self.friendly_name: str = device[CONF_FRIENDLY_NAME]
        self.ip: str = device[CONF_IP_ADDRESS]
        self.path: str = device[CONF_PATH]
        self.attrs: Dict[str, Any] = {
            ATTR_NAME: self.friendly_name,
            ATTR_ICON: "mdi:google-home"
        }
        self._name = device.get("name", self.friendly_name)
        self._state = None
        self._available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self.ip

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        google_devices = self.client.get_google_devices_json()

        self._available = False
        found_device = False
        for element in google_devices:
            token = element["localAuthToken"]
            name = element["deviceName"]
            if token is None:
                continue

            if name == self.friendly_name:
                found_device = True

                get_request = requests.get(
                    f"https://{self.ip}:8443/setup{self.path}",
                    headers={'cast-local-authorization-token': token},
                    verify=False,
                )
                request_json = get_request.text
                self._available = True
                self._state = request_json

        if not found_device:
            _LOGGER.error(f"Could not find the set device ({self.friendly_name}).")
