from typing import List

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from const import ATTR_CLIENT_IDENTIFIER, ATTR_CONNECTION_URI, CLIENT_IDENTIFIER_PATTERN, DOMAIN

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

    conf = config.get(DOMAIN)

    from plexapi.myplex import MyPlexDevice
    original_list_attrs = MyPlexDevice.listAttrs

    def override_list_attrs(self, data, attr, rtag=None, **kwargs) -> List[str]:
        """ Return a list of values from matching attribute. """
        if attr != 'uri' or kwargs['etag'] != 'Connection':
            return original_list_attrs(self, data, attr, rtag, **kwargs)

        client_identifier = data.attrib.get('clientIdentifier')
        if not client_identifier or client_identifier not in conf:
            return original_list_attrs(self, data, attr, rtag, **kwargs)

        return [
            conf.get(client_identifier)
        ]

    MyPlexDevice.listAttrs = override_list_attrs

    return True
