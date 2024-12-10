from __future__ import annotations

import logging

from lamb.utils.transformers import transform_string_enum

from core.constants import UserRole

__all__ = [
    "tf_user_role",
]

logger = logging.getLogger(__name__)


def tf_user_role(value: str) -> UserRole:
    return transform_string_enum(value=value, enum_class=UserRole)
