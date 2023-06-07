import logging

from django.contrib import messages

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)8.8s] %(message)s",
    datefmt="%Y/%M/%D %I:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

MESSAGE_TO_LOGGING_FUNCTION = {
    messages.ERROR: logging.error,
    messages.WARNING: logging.warning,
    messages.INFO: logging.info,
}
