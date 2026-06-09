import json
import logging
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """
        JSON logs are easier for log tools, cloud services, and monitoring systems
        to search, filter, and parse.

    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def get_logger(name):
    """
        Create or return a logger configured to write JSON logs to stdout.

        The same logger can be reused across the application without adding
        duplicate handlers each time this function is called.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
