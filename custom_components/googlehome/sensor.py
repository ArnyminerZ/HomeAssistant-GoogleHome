import json
import logging
import http3

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from glocaltokens.client import GLocalAuthenticationTokens
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
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import HomeAssistantType, DiscoveryInfoType
from typing import Callable, Optional, Dict, Any, List

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
            logging.info("Eureka:" + str(eureka))
            attrs[ATTR_BSSID] = eureka["bssid"]
            attrs[ATTR_BUILD_VERSION] = eureka["build_version"]
            attrs[ATTR_CAST_BUILD_VERSION] = eureka["cast_build_revision"]
            attrs[ATTR_HOTSPOT_BSSID] = eureka["hotspot_bssid"]
            attrs[ATTR_IP_ADDRESS] = eureka["ip_address"]
            attrs[ATTR_LOCALE] = eureka["locale"]
            attrs[ATTR_LOCATION_COUNTRY_CODE] = eureka["location"]["country_code"]
            attrs[ATTR_LOCATION_LATITUDE] = eureka["location"]["latitude"]
            attrs[ATTR_LOCATION_LONGITUDE] = eureka["location"]["longitude"]
            attrs[ATTR_MAC] = eureka["mac_address"]
            attrs[ATTR_SSID] = eureka["ssid"]
            attrs[ATTR_TIME_FORMAT] = eureka["time_format"]
            attrs[ATTR_TIMEZONE] = eureka["timezone"]
            attrs[ATTR_UPTIME] = eureka["uptime"]
            attrs[ATTR_VERSION] = eureka["version"]

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
                client = http3.AsyncClient()

                eureka_request = await client.get(
                    f"https://{self.ip}:8443/setup/eureka_info",
                    headers={'cast-local-authorization-token': token},
                    verify=False,
                )
                self.eureka = json.loads(eureka_request.text)

                get_request = await client.get(
                    f"https://{self.ip}:8443/setup{self.path}",
                    headers={'cast-local-authorization-token': token},
                    verify=False,
                )
                request_json = get_request.text
                self._available = True
                self._state = request_json

        if not found_device:
            _LOGGER.error(f"Could not find the set device ({self.friendly_name}).")
