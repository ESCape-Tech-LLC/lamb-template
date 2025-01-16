import logging

from lamb.management.base import LambCommand
# Lamb Framework
from lamb.utils import import_by_name

logger = logging.getLogger(__name__)


class Command(LambCommand):
    help = "run task"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "-task_name",
            type=str,
            dest="task_name",
            help="task_name",
        )

    def handle(self, *args, **options):
        task_name = options.get("task_name")

        task = import_by_name(f"api.tasks.{task_name}")

        task.si().apply_async({"expires": 60 * 60})
        logger.info(f"Did send to broker {task_name} task")
