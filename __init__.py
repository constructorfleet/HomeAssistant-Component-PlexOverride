from typing import List

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import ATTR_CLIENT_IDENTIFIER, ATTR_CONNECTION_URI, CLIENT_IDENTIFIER_PATTERN, DOMAIN

SCHEMA_CLIENT_URI = vol.Schema({
    vol.Required(ATTR_CLIENT_IDENTIFIER): vol.All(vol.Coerce(str), vol.Match(CLIENT_IDENTIFIER_PATTERN)),
    vol.Required(ATTR_CONNECTION_URI): vol.All(vol.Coerce(str), cv.url)
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(vol.All(vol.Coerce(str), vol.Match(CLIENT_IDENTIFIER_PATTERN))): vol.All(vol.Coerce(str), cv.url)
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Set up the plex_override component."""

    from homeassistant.components.plex.media_player import PlexMediaPlayer
    from homeassistant.components.plex.const import COMMON_PLAYERS, NAME_FORMAT
    import plexapi.exceptions

    def update(self):
        """Refresh key device data."""
        if not self.session:
            self.force_idle()
        if not self.device:
            self._attr_available = False
            return

        self._attr_available = True

        try:
            if self.device.address.startswith("10.0"):
                self.device.protocolCapabilities = "playback"
                self.device._baseurl = f"http://{self.device.address}:32500"
            device_url = self.device.url("/")
        except plexapi.exceptions.BadRequest:
            device_url = "127.0.0.1"
        if "127.0.0.1" in device_url:
            self.device.proxyThroughServer()
        self._device_protocol_capabilities = self.device.protocolCapabilities

        for device in filter(None, [self.device, self.session_device]):
            self.device_make = self.device_make or device.device
            self.device_platform = self.device_platform or device.platform
            self.device_product = self.device_product or device.product
            self.device_title = self.device_title or device.title
            self.device_version = self.device_version or device.version

        name_parts = [self.device_product, self.device_title or self.device_platform]
        if (self.device_product in COMMON_PLAYERS) and self.device_make:
            # Add more context in name for likely duplicates
            name_parts.append(self.device_make)
        if self.username and self.username != self.plex_server.owner:
            # Prepend username for shared/managed clients
            name_parts.insert(0, self.username)
        self._attr_name = NAME_FORMAT.format(" - ".join(name_parts))

    PlexMediaPlayer.update = update

    return True
