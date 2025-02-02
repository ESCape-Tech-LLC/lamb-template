import logging

from {{project_name}}.celery_config import CeleryQueues, celery_app

__all__ = ["some_task"]


logger = logging.getLogger(__name__)


@celery_app.task(queue=CeleryQueues.default, bind=True, ignore_result=True)
def some_task(_: celery_app.Task):
    logger.debug("Some task")
