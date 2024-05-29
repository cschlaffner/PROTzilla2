"""This module contains the logging configuration for the protzilla app."""
import logging


class ProtzillaLoggingHandler(logging.Handler):
    """
    Courtesy of https://stackoverflow.com/users/9150146/sergey-pleshakov,
                https://stackoverflow.com/a/56944256/1435167

    A logging handler that emits styled log messages to the console.
    Used by the protzilla app and as the Django logging handler.
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.level = level
        self.setLevel(level)
        self.propagate = False

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    formats = "[%(asctime)s] [%(levelname)8.8s] %(message)s"
    date_format = "%Y/%m/%d - %H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey + formats + reset,
        logging.INFO: grey + formats + reset,
        logging.WARNING: yellow + formats + reset,
        logging.ERROR: red + formats + reset,
        logging.CRITICAL: bold_red + formats + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=self.date_format)
        return formatter.format(record)

    def emit(self, record):
        msg = self.format(record)
        print(msg)

    def debug(self, msg):
        if self.level == 10:
            self.emit(logging.makeLogRecord({"msg": msg, "levelname": "DEBUG"}))

    def info(self, msg):
        if self.level <= 20:
            self.emit(logging.makeLogRecord({"msg": msg, "levelname": "INFO"}))

    def warning(self, msg):
        if self.level <= 30:
            self.emit(logging.makeLogRecord({"msg": msg, "levelname": "WARNING"}))

    def error(self, msg):
        if self.level <= 40:
            self.emit(logging.makeLogRecord({"msg": msg, "levelname": "ERROR"}))

    def critical(self, msg):
        if self.level <= 50:
            self.emit(logging.makeLogRecord({"msg": msg, "levelname": "CRITICAL"}))


# the logger used by DJANGO is configured in ui/main/settings.py::LOGGING

# this logger is/can be used by the protzilla app
# adjust `protzilla_logging_level` to adjust the verbosity of the protzilla logger
protzilla_logging_level = logging.INFO
logger = logging.getLogger("protzilla")
logger.setLevel(protzilla_logging_level)
logger.addHandler(ProtzillaLoggingHandler(protzilla_logging_level))
logger.propagate = False

# Map the error levels to the logging functions
MESSAGE_TO_LOGGING_FUNCTION = {
    logging.ERROR: logging.error,
    logging.WARNING: logging.warning,
    logging.INFO: logging.info,
}
