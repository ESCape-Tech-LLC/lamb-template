from __future__ import annotations

import enum

from lamb.exc import ApiError

__all__ = ["InvalidRoleError"]


@enum.unique
class AppErrorCodes(enum.IntEnum):
    InvalidRole = 1001


class InvalidRoleError(ApiError):
    _status_code = 403
    _app_error_code = AppErrorCodes.InvalidRole
    _message = "Invalid user role for access this service"
