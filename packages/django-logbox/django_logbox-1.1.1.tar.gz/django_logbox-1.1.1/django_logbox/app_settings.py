from http import HTTPStatus

from django.conf import settings

DEFAULT_LOGBOX_SETTINGS = {
    # HTTP methods to log. Default to all
    "LOGGING_HTTP_METHODS": ["GET", "POST", "PUT", "PATCH", "DELETE"],
    # exclude server IPs from logging. Default to not exclude any
    "LOGGING_SERVER_IPS_TO_EXCLUDE": [],
    # exclude client IPs from logging. Default to not exclude any
    "LOGGING_CLIENT_IPS_TO_EXCLUDE": [],
    # Status codes to log. Default to all
    "LOGGING_STATUS_CODES": [http_code.value for http_code in HTTPStatus],
    # Path regex to exclude from logging. Default to not exclude any
    "LOGGING_PATHS_TO_EXCLUDE": [],
    # The number of logs to insert in bulk. The default is 1, which means insert logs instantly.
    "LOGGING_DAEMON_QUEUE_SIZE": 1,
    # The number of seconds between log insertion attempts. The default is 0.
    "LOGGING_DAEMON_INTERVAL": 0,
}

USER_LOGBOX_SETTINGS = getattr(settings, "LOGBOX_SETTINGS", {})
settings.LOGBOX_SETTINGS = {**DEFAULT_LOGBOX_SETTINGS, **USER_LOGBOX_SETTINGS}
