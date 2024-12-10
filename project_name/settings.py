from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from functools import partial
from pathlib import Path

import furl

import lamb.service.redis.config as redisCfg

# Lamb Framework
from lamb.json import JsonEncoder
from lamb.log.constants import LAMB_LOG_FORMAT_PREFIXNO, LAMB_LOG_FORMAT_SIMPLE
from lamb.log.utils import inject_logging_factory
from lamb.service.aws.s3 import S3BucketConfig
from lamb.utils import dpath_value, masked_url
from lamb.utils.core import masked_dict
from lamb.utils.transformers import tf_list_int, tf_list_string, transform_boolean, transform_string_enum
from lamb.utils.validators import (
    validate_length,
)

# warning
logging.captureWarnings(True)
warnings.filterwarnings("once", category=DeprecationWarning, module="lamb")
warnings.filterwarnings("once", category=DeprecationWarning, module="django")
warnings.filterwarnings("once", category=DeprecationWarning, module="api")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Lamb: main configs
LAMB_APP_SERVERNAME = dpath_value(os.environ, "LAMB_APP_SERVERNAME", str)
LAMB_APP_ALLOWED_HOSTS = dpath_value(
    os.environ,
    "LAMB_APP_ALLOWED_HOSTS",
    str,
    transform=tf_list_string,
    default=[LAMB_APP_SERVERNAME],
)
LAMB_APP_DEBUG = dpath_value(os.environ, "LAMB_APP_DEBUG", str, transform=transform_boolean, default=False)
LAMB_APP_PORT = dpath_value(os.environ, "LAMB_APP_PORT", int, default=80)
LAMB_APP_SCHEME = dpath_value(os.environ, "LAMB_APP_SCHEME", str, default="http")
LAMB_APP_NAME = dpath_value(os.environ, "LAMB_APP_NAME", str, transform=validate_length, default=None)
LAMB_APP_GOD_MODE = dpath_value(os.environ, "LAMB_APP_GOD_MODE", str, transform=transform_boolean, default=False)

LAMB_LOG_JSON_ENABLE = dpath_value(os.environ, "LAMB_LOG_JSON_ENABLE", str, transform=transform_boolean, default=False)

LAMB_RESPONSE_APPLY_TO_APPS = ["api"]
LAMB_RESPONSE_DATETIME_TRANSFORMER = "lamb.utils.transformers.transform_datetime_milliseconds_int"
LAMB_RESPONSE_DATE_FORMAT = "%Y.%m.%d"

LAMB_DPATH_DICT_ENGINE = "reduce"

LAMB_LOGGING_HEADER_XRAY = "HTTP_X_LAMB_LOGGING_XRAY"
LAMB_EVENT_LOGGING_HEADER_TRACKID = "HTTP_X_LAMB_LOGGING_TRACKID"

LAMB_DEVICE_INFO_COLLECT_IP = True
LAMB_DEVICE_INFO_COLLECT_GEO = False

LAMB_VERBOSE_SQL_LOG = dpath_value(os.environ, "LAMB_VERBOSE_SQL_LOG", str, transform=transform_boolean, default=False)
LAMB_VERBOSE_SQL_LOG_THRESHOLD = dpath_value(os.environ, "LAMB_VERBOSE_SQL_LOG_THRESHOLD", float, default=None)

LAMB_EXECUTION_TIME_STORE = dpath_value(
    os.environ,
    "LAMB_EXECUTION_TIME_STORE",
    str,
    transform=transform_boolean,
    default=False,
)
LAMB_EXECUTION_TIME_COLLECT_MARKERS = dpath_value(
    os.environ,
    "LAMB_EXECUTION_TIME_COLLECT_MARKERS",
    str,
    transform=transform_boolean,
    default=False,
)
LAMB_EXECUTION_TIME_TIMESCALE = dpath_value(
    os.environ,
    "LAMB_EXECUTION_TIME_TIMESCALE",
    str,
    transform=transform_boolean,
    default=False,
)
LAMB_ADD_CORS_ENABLED = dpath_value(
    os.environ,
    "LAMB_ADD_CORS_ENABLED",
    str,
    transform=transform_boolean,
    default=False,
)

# SPO: db connections
LAMB_DB_CONFIG = {
    "default": dict(
        driver="pysqlite",
        async_driver="aiosqlite",
        host=":memory:",
        db_name=None,
        port=None,
        username=None,
        password=None,
        # engine_options=_engine_options,
        # aengine_options=_engine_options,
        # connect_options=partial(_connect_options, target_session_attrs="read-write"),
        # aconnect_options=partial(_connect_options, target_session_attrs="read-write"),
    ),
}

LAMB_DB_CONTEXT_POOLED_METRICS = True

# SPO: S3 connections
LAMB_S3_CONFIG = {
    "default": S3BucketConfig(
        bucket_name="dev-bucket",
        access_key="123456",
        secret_key="13=23456",
        endpoint_url="http://minio:9000/dev-bucket",
        bucket_url="http://minio:9000/dev-bucket",
        check_buckets_list=False,
    )
}

# SPO: Redis connections
LAMB_REDIS_HOST = dpath_value(os.environ, "LAMB_REDIS_HOST", str, transform=tf_list_string, default=["localhost"])
LAMB_REDIS_PORT = dpath_value(os.environ, "LAMB_REDIS_PORT", str, transform=tf_list_int, default=[6379])
LAMB_REDIS_PASS = dpath_value(os.environ, "LAMB_REDIS_PASS", str, transform=validate_length, default=None)
LAMB_REDIS_USERNAME = dpath_value(os.environ, "LAMB_REDIS_USERNAME", str, transform=validate_length, default=None)
LAMB_REDIS_MODE = dpath_value(
    os.environ,
    "LAMB_REDIS_MODE",
    str,
    transform=partial(transform_string_enum, enum_class=redisCfg.Mode),
    default="GENERIC",
)
LAMB_REDIS_SENTINEL_PASS = dpath_value(
    os.environ, "LAMB_REDIS_SENTINEL_PASS", str, transform=validate_length, default=None
)
LAMB_REDIS_SENTINEL_SERVICE_NAME = dpath_value(
    os.environ, "LAMB_REDIS_SENTINEL_SERVICE_NAME", str, transform=validate_length, default=None
)

_redis_main_configs = {
    "host": LAMB_REDIS_HOST,
    "port": LAMB_REDIS_PORT,
    "mode": LAMB_REDIS_MODE,
    "username": LAMB_REDIS_USERNAME,
    "password": LAMB_REDIS_PASS,
    "sentinel_password": LAMB_REDIS_SENTINEL_PASS,
    "sentinel_service_name": LAMB_REDIS_SENTINEL_PASS,
}
LAMB_REDIS_CONFIG = {
    "cache": redisCfg.Config(**_redis_main_configs, default_db=0),
    "throttling": redisCfg.Config(**_redis_main_configs, default_db=1),
    "broker": redisCfg.Config(**_redis_main_configs, default_db=2),
    "result": redisCfg.Config(**_redis_main_configs, default_db=3),
}
LAMB_BROKER_URL = LAMB_REDIS_CONFIG["broker"].broker_url
LAMB_BROKER_RESULT_URL = LAMB_REDIS_CONFIG["result"].broker_url
LAMB_BROKER_TRANSPORT_OPTIONS = LAMB_REDIS_CONFIG["broker"].broker_transport_options
LAMB_BROKER_RESULT_TRANSPORT_OPTIONS = LAMB_REDIS_CONFIG["result"].broker_transport_options


# Lamb: dynamic configs
LAMB_GEOIP2_DB_CITY = BASE_DIR.joinpath("data", "geoip", "GeoLite2-City.mmdb")
LAMB_GEOIP2_DB_COUNTRY = BASE_DIR.joinpath("data", "geoip", "GeoLite2-Country.mmdb")
LAMB_GEOIP2_DB_ASN = BASE_DIR.joinpath("data", "geoip", "GeoLite2-ASN.mmdb")

LAMB_RUN_FOLDER = BASE_DIR.joinpath("run")
LAMB_TMP_FOLDER = BASE_DIR.joinpath("tmp")
LAMB_LOG_FOLDER = BASE_DIR.joinpath("log")
LAMB_CRT_FOLDER = BASE_DIR.joinpath("crt")
LAMB_SYSTEM_STATIC_FOLDER = BASE_DIR.joinpath("system-static")
LAMB_STATIC_FOLDER = BASE_DIR.joinpath("static")
LAMB_TEMPLATE_FOLDER = BASE_DIR.joinpath("templates")

_full_host = furl.furl()
_full_host.scheme = LAMB_APP_SCHEME
_full_host.host = LAMB_APP_SERVERNAME
_full_host.port = LAMB_APP_PORT
LAMB_ORIGIN_URL = _full_host.origin
LAMB_STATIC_URL = _full_host.set(path="static").url
LAMB_SYSTEM_STATIC_URL = _full_host.set(path="system-static").url

with open(os.path.join(BASE_DIR, "VERSION"), "r") as f:
    LAMB_APP_VERSION = f.read()
    LAMB_APP_VERSION = "".join(LAMB_APP_VERSION.split())  # bump2version sometime adds \n symbol

# logging
_log_fmt_cls = (
    "lamb.log.formatters.RequestJsonFormatter" if LAMB_LOG_JSON_ENABLE else "lamb.log.formatters.MultilineFormatter"
)
_log_fmt = LAMB_LOG_FORMAT_SIMPLE if sys.platform == "darwin" else LAMB_LOG_FORMAT_PREFIXNO

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "generic": {
            "format": _log_fmt,
            "class": _log_fmt_cls,
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "generic",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
            "level": "WARNING",
        },
        "api": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "core": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "lamb": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "py.warnings": {
            "handlers": ["console"],
            "propagate": True,
            "level": "WARNING",
        },
    },
}
inject_logging_factory()

# django - main configs
SECRET_KEY = dpath_value(os.environ, "CHATUP_API_SECRET_KEY", str)

DEBUG = LAMB_APP_DEBUG

ALLOWED_HOSTS = LAMB_APP_ALLOWED_HOSTS

PORT = LAMB_APP_PORT

SCHEME = LAMB_APP_SCHEME

HOST = LAMB_APP_SERVERNAME

INSTALLED_APPS = ["lamb.LambAppConfig", "api"]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "lamb.middleware.grequest.LambGRequestMiddleware",
    "lamb.middleware.cors.LambCorsMiddleware",
    "lamb.middleware.xray.LambXRayMiddleware",
    "lamb.middleware.device_info.LambDeviceInfoMiddleware",
    "lamb.middleware.db.LambSQLAlchemyMiddleware",
    "lamb.middleware.execution_time.LambExecutionTimeMiddleware",
    "lamb.middleware.rest.LambRestApiJsonMiddleware",
]

ROOT_URLCONF = "{{project_name}}.urls"

WSGI_APPLICATION = "{{project_name}}.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-US"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25MB max POST/PATCH body size

FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

# collect main details and log
_msg = {
    "DATABASES": {
        k: masked_dict(v, "password", "engine_options", "aengine_options", "connect_options", "aconnect_options")
        for k, v in LAMB_DB_CONFIG.items()
    },
    "REDIS": dict(
        CACHE=masked_url(LAMB_REDIS_CONFIG["cache"].url),
        BROKER=masked_url(LAMB_REDIS_CONFIG["broker"].url),
        RESULT=masked_url(LAMB_REDIS_CONFIG["result"].url),
        THROTTLING=masked_url(LAMB_REDIS_CONFIG["throttling"].url),
    ),
    "LAMB": dict(
        LAMB_APP_NAME=LAMB_APP_NAME,
        LAMB_APP_SERVERNAME=LAMB_APP_SERVERNAME,
        LAMB_APP_ALLOWED_HOSTS=LAMB_APP_ALLOWED_HOSTS,
        LAMB_APP_DEBUG=LAMB_APP_DEBUG,
        LAMB_APP_PORT=LAMB_APP_PORT,
        LAMB_APP_SCHEME=LAMB_APP_SCHEME,
        LAMB_APP_GOD_MODE=LAMB_APP_GOD_MODE,
        LAMB_LOG_JSON_ENABLE=LAMB_LOG_JSON_ENABLE,
        LAMB_EXECUTION_TIME_STORE=LAMB_EXECUTION_TIME_STORE,
        LAMB_ADD_CORS_ENABLED=LAMB_ADD_CORS_ENABLED,
    ),
    "S3": {k: masked_dict(v.response_encode(), "access_key", "secret_key") for k, v in LAMB_S3_CONFIG.items()},
}
logger = logging.getLogger("django")
_indent = 2 if sys.platform == "darwin" and not LAMB_LOG_JSON_ENABLE else None
logger.warning(f"configs: {json.dumps(_msg, indent=_indent, ensure_ascii=False, cls=JsonEncoder)}")
