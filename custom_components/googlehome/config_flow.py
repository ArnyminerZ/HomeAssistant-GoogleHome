from copy import deepcopy
import voluptuous as vol
import logging
from typing import Optional, Dict, Any

from glocaltokens.client import GLocalAuthenticationTokens

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries, core
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get_registry,
)
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_IP_ADDRESS,
    CONF_FRIENDLY_NAME,
    CONF_DEVICES,
    CONF_PATH
)

from .const import (
    DOMAIN, AVAILABLE_GET_PATHS
)

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)
DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_FRIENDLY_NAME): cv.string,
        vol.Required(CONF_PATH): cv.string,
        vol.Optional("add_another"): cv.boolean,
    }
)

_LOGGER = logging.getLogger(__name__)


def validate_path(path: str) -> bool:
    return path in AVAILABLE_GET_PATHS


def validate_auth(username: str, password: str) -> None:
    client = GLocalAuthenticationTokens(
        username=username,
        password=password
    )
    atoken = client.get_master_token()
    if atoken is None:
        raise ValueError


class GoogleHomeCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        errors: Dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            try:
                validate_auth(username, user_input[CONF_PASSWORD])
            except ValueError:
                _LOGGER.error(f"Tried to configure Google Home account with invalid credentials. Username: {username}")
                errors["base"] = "auth"
            if not errors:
                self.data = user_input
                self.data[CONF_DEVICES] = []
                return await self.async_step_device()

        return self.async_show_form(step_id="user", data_schema=AUTH_SCHEMA, errors=errors)

    async def async_step_device(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        errors: Dict[str, str] = {}
        if user_input is not None:
            path = user_input[CONF_PATH]
            if not validate_path(path):
                errors["base"] = "invalid_path"

            if not errors:
                self.data[CONF_DEVICES].append(
                    {
                        "name": user_input[CONF_FRIENDLY_NAME],
                        "ip": user_input[CONF_IP_ADDRESS],
                        "path": user_input[CONF_PATH]
                    }
                )
                if user_input.get("add_another", False):
                    return await self.async_step_device()

                return self.async_create_entry(title="Google Home", data=self.data)

        client = GLocalAuthenticationTokens(
            username=self.data[CONF_USERNAME],
            password=self.data[CONF_PASSWORD]
        )
        devices = client.get_google_devices_json()
        device_names = {e.entity_id: e.deviceName for e in devices}

        new_device_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Required(CONF_FRIENDLY_NAME): cv.ensure_list(device_names),
                vol.Required(CONF_PATH): cv.string,
                vol.Optional("add_another"): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="device", data_schema=new_device_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        errors: Dict[str, str] = {}

        entity_registry = await async_get_registry(self.hass)
        entries = async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )
        all_devices = {e.entity_id: e.original_name for e in entries}
        devices_map = {e.entity_id: e for e in entries}

        if user_input is not None:
            updated_devices = deepcopy(self.config_entry.data[CONF_DEVICES])

            removed_entities = [
                entity_id
                for entity_id in devices_map.keys()
                if entity_id not in user_input[CONF_DEVICES]
            ]
            for entity_id in removed_entities:
                entity_registry.async_remove(entity_id)
                entry = devices_map[entity_id]
                entry_path = entry.unique_id
                updated_devices = [e for e in updated_devices if e["path"] != entry_path]

            if user_input[CONF_PATH]:
                if not validate_path(user_input[CONF_PATH]):
                    errors["base"] = "invalid_path"

                if not errors:
                    updated_devices.append(
                        {
                            "name": user_input[CONF_FRIENDLY_NAME],
                            "ip": user_input[CONF_IP_ADDRESS],
                            "path": user_input[CONF_PATH]
                        }
                    )

            if not errors:
                return self.async_create_entry(
                    title="",
                    data={CONF_DEVICES: updated_devices}
                )

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_DEVICES, default=list(all_devices.keys())): cv.multi_select(all_devices),
                vol.Optional(CONF_IP_ADDRESS): cv.string,
                vol.Optional(CONF_PATH): cv.string,
                vol.Optional(CONF_FRIENDLY_NAME): cv.string,
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
