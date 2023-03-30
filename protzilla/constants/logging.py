import logging

from django.contrib import messages

MESSAGE_TO_LOGGING_FUNCTION = {
    messages.ERROR: logging.error,
    messages.WARNING: logging.warning,
    messages.INFO: logging.info,
}
