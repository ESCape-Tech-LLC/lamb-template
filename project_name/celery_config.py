import enum
import os

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from django.conf import settings
from kombu import Exchange, Queue

import lamb.log.constants
from lamb.log.formatters import CeleryJsonFormatter, CeleryMultilineFormatter

__all__ = ["celery_app", "CeleryQueues"]


# Django init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{project_name}}.settings")


# Queues
@enum.unique
class CeleryQueues(str, enum.Enum):
    default = "default"
    maintenance = "maintenance"
    email = "email"


# Create celery app
celery_app = Celery(
    main="{{project_name}}",
    broker=settings.LAMB_BROKER_URL,
    backend=settings.LAMB_BROKER_RESULT_URL,
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    accept_content=["json"],
    enable_utc=True,
    task_queues=tuple([Queue(q, exchange=Exchange(q), routing_key=q) for q in CeleryQueues.__members__]),
    task_default_queue=CeleryQueues.default,
    task_default_exchange=CeleryQueues.default,
    task_default_routing_key=CeleryQueues.default,
    autodiscover_tasks=lambda: settings.INSTALLED_APPS,
    worker_log_format=lamb.log.constants.LAMB_LOG_FORMAT_CELERY_MAIN_SIMPLE,
    worker_task_log_format=lamb.log.constants.LAMB_LOG_FORMAT_CELERY_TASK_SIMPLE,
    broker_transport_options=settings.LAMB_BROKER_TRANSPORT_OPTIONS,
    result_backend_transport_options=settings.LAMB_BROKER_RESULT_TRANSPORT_OPTIONS,
)


# Celery Beat tasks
celery_app.conf.beat_schedule = {}

celery_formatter_cls = CeleryJsonFormatter if settings.LAMB_LOG_JSON_ENABLE else CeleryMultilineFormatter


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    # print(f"setup_task_logger: {logger, args, kwargs}")
    for handler in logger.handlers:
        handler.setFormatter(celery_formatter_cls(lamb.log.constants.LAMB_LOG_FORMAT_CELERY_TASK_SIMPLE))


@after_setup_logger.connect
def setup_logger(logger, *args, **kwargs):
    # print(f"setup_logger: {logger, args, kwargs}")
    for handler in logger.handlers:
        handler.setFormatter(celery_formatter_cls(lamb.log.constants.LAMB_LOG_FORMAT_CELERY_MAIN_SIMPLE))
