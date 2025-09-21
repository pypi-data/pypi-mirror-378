import logging
import uuid
from contextvars import ContextVar

# Context variable to hold the request ID
# This is used to store the request ID in the context of the request
# The value of the request ID is set in the RequestIdMiddleware
# Magically, this is maintained across multiple requests without it getting mixed up.
request_id_var = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """
    A logging filter that injects the request_id from the context variable into the log record.
    """
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def setup_logging():
    """
    Configures the logging for the application.
    It sets up a handler, a formatter, and adds the RequestIdFilter.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Add the filter to all handlers
    for h in logger.handlers:
        if not any(isinstance(f, RequestIdFilter) for f in h.filters):
            h.addFilter(RequestIdFilter())

    return logger

__all__ = ["setup_logging", "request_id_var", "RequestIdFilter"]
