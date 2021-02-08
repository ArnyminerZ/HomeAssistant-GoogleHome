import json
import requests
from homeassistant.helpers.entity import Entity
from typing import Callable, Optional, Dict, Any, List

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

from .const import *

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
    sensors: List[Entity] = list()
    for device in config[CONF_DEVICES]:
        _LOGGER.info("Adding device:" + str(device))
        sensors.append(GoogleHomeVolumeSensor(client, device))
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
        hass: HomeAssistantType,
        config,
        async_add_entities: Callable,
        discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    client = GLocalAuthenticationTokens(
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD]
    )
    sensors: List[Entity] = list()
    for device in config[CONF_DEVICES]:
        _LOGGER.info("Adding device:" + str(device))
        sensors.append(GoogleHomeVolumeSensor(client, device))
    async_add_entities(sensors, update_before_add=True)


class GoogleHomeVolumeSensor(Entity):
    """Representation of a Google Home device"""

    def __init__(self, client: GLocalAuthenticationTokens, device: Dict[str, str]):
        super().__init__()
        self.client = client
        self.friendly_name: str = device["name"]
        self.ip: str = device["ip"]
        self.path: str = device["path"]
        self.attrs: Dict[str, Any] = {
            ATTR_NAME: self.friendly_name
        }
        self.eureka = None
        self._name = self.friendly_name
        self._state = None
        self._available = False
        self._icon = "mdi:google-home"

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
    def icon(self) -> str:
        return self._icon

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        attrs = self.attrs
        eureka = self.eureka
        if eureka is not None:
            attrs[ATTR_BUILD_TYPE] = eureka["build_info"]["build_type"]
            attrs[ATTR_BUILD_CAST_REVISION] = eureka["build_info"]["cast_build_revision"]
            attrs[ATTR_BUILD_CAST_CONTROL_VERSION] = eureka["build_info"]["cast_control_version"]
            attrs[ATTR_BUILD_PREVIEW_CHANNEL_STATE] = eureka["build_info"]["preview_channel_state"]
            attrs[ATTR_RELEASE_TRACK] = eureka["build_info"]["release_track"]
            attrs[ATTR_BUILD_NUMBER] = eureka["build_info"]["system_build_number"]

            attrs[ATTR_LOCALE] = eureka["detail"]["locale"]["display_string"]
            attrs[ATTR_TIMEZONE_OFFSET] = eureka["detail"]["timezone"]["offset"]
            attrs[ATTR_TIMEZONE_STRING] = eureka["detail"]["timezone"]["display_string"]

            attrs[ATTR_MAC] = eureka["device_info"]["mac_address"]
            attrs[ATTR_UPTIME] = eureka["device_info"]["uptime"]
            attrs[ATTR_NAME] = eureka["name"]
        attrs[ATTR_ICON] = self._icon
        return attrs

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

                eureka_request = requests.get(
                    f"https://{self.ip}:8443/setup/eureka_info",
                    headers={'cast-local-authorization-token': token},
                    verify=False,
                )
                self.eureka = json.loads(eureka_request.text)

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
