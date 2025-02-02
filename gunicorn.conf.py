import os
from datetime import datetime

from gunicorn.instrument.statsd import Statsd as StatsdLogger

from lamb.utils import dpath_value
from lamb.utils.transformers import transform_boolean

LAMB_LOG_JSON_ENABLE = dpath_value(os.environ, "LAMB_LOG_JSON_ENABLE", str, transform=transform_boolean, default=False)


class CustomLogger(StatsdLogger):
    def now(self):
        return datetime.now().isoformat(sep="T", timespec="microseconds")


# logs access info
logger_class = CustomLogger
if LAMB_LOG_JSON_ENABLE:
    logging_formatter = "lamb.log.formatters.RequestJsonFormatter"
else:
    logging_formatter = "lamb.log.formatters.MultilineFormatter"

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "INFO",
        "handlers": [],
    },
    "loggers": {
        "gunicorn.error": {
            "level": "WARNING",
            "handlers": ["error_console"],
            "propagate": True,
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": True,
            "qualname": "gunicorn.access",
        },
    },
    "formatters": {
        "generic": {
            "class": logging_formatter,
            "format": "[%(asctime)s, xray=None, user_id=None: %(levelname)9s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr",
        },
    },
}

# number of requests in queue waiting for workers
backlog = 2048

# bind
bind = ["127.0.0.1:8000", "[::1]:8000"]

# max requests until worker rotate
max_requests = 4096
max_requests_jitter = 128

# processing/harakiri timeout
timeout = 30
