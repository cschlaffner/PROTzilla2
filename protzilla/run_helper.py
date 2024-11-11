from protzilla.constants.protzilla_logging import MESSAGE_TO_LOGGING_FUNCTION


def log_message(level: int = 40, msg: str = "", trace: str | list[str] = ""):
    """
    Logs a message to the console.

    :param level: The logging level of the message. See https://docs.python.org/3/library/logging.html#logging-levels
    :param msg: The message to log.
    :param trace: The trace to log.
    """
    log_function = MESSAGE_TO_LOGGING_FUNCTION.get(level)
    if log_function:
        if trace != "":
            trace = f"\nTrace: {trace}"
        log_function(f"{msg}{trace}")


def log_messages(messages: list[dict] = None):
    """
    Logs a list of messages to the console.

    :param messages: A list of messages to log, each message is a dict with the keys "level", "msg" and optional "trace".
    """
    if messages is None:
        messages = []
    for message in messages:
        log_message(
            message["level"],
            message["msg"],
            message["trace"] if "trace" in message else "",
        )
