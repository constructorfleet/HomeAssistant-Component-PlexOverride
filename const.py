import re

DOMAIN = "plex_override"

ATTR_CLIENT_IDENTIFIER = "client_identifier"
ATTR_CONNECTION_URI = "connection_uri"

CLIENT_IDENTIFIER_PATTERN = re.compile("^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")
