DOMAIN = "googlehome"

AVAILABLE_GET_PATHS = [
    "/supported_timezones",
    "/supported_locales",
    "/offer",
    "/eureka_info",
    "/assistant/alarms",
    "/bluetooth/scan_results",
    "/bluetooth/status",
    "/bluetooth/get_bonded",
    "/configured_networks",
    "/scan_results",
    "/NOTICE.html.gz",
    "/icon.png"
]

ATTR_BSSID = "bssid"
ATTR_BUILD_VERSION = "build_version"
ATTR_CAST_BUILD_VERSION = "cast_build_version"
ATTR_HOTSPOT_BSSID = "hotspot_bssid"
ATTR_IP_ADDRESS = "ip_address"
ATTR_LOCALE = "locale"
ATTR_LOCATION_COUNTRY_CODE = "location_country_code"
ATTR_LOCATION_LATITUDE = "location_latitude"
ATTR_LOCATION_LONGITUDE = "location_longitude"
ATTR_MAC = "mac_address"
ATTR_SSID = "ssid"
ATTR_TIME_FORMAT = "time_format"
ATTR_TIMEZONE = "timezone"
ATTR_UPTIME = "uptime"
ATTR_VERSION = "version"

CONF_NEXT_ALARM = "next_alarm"

AVAILABLE_CONF_PATHS = {
    CONF_NEXT_ALARM: {
        "icon": "mdi:alarm",
        "path": "/assistant/alarms"
    },
}
