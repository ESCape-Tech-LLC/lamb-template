from __future__ import annotations

import enum
from typing import Any, TypeVar

import sqlalchemy as sa
from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible

import lamb.exc as exc
from lamb.json.mixins import ResponseEncodableMixin

__all__ = ["UserRole", "UserEventCode"]


# utils
class _EncodeMixin(ResponseEncodableMixin):
    def response_encode(self, request=None) -> dict:
        return self.value

    def handbook_encode(self) -> dict:
        return {
            "id": self.value,
            "title": self.title,
        }


class _EnumMixin(_EncodeMixin):
    title: str | None = None

    def __new__(cls, code, title, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.__post_init__(code, title, *args, **kwargs)
        return obj

    def __post_init__(self, code, title, *args, **kwargs):
        self.title = title

    def response_encode(self, request=None) -> dict:
        return self.value

    def handbook_encode(self) -> dict:
        result = {
            "id": self.value,
            "title": self.title,
        }
        return result


class PGEnumMixin(_EnumMixin):
    __pg_name__ = None

    def __new__(cls, code, title, *args, **kwargs):
        if cls.__pg_name__ is None:
            raise exc.ImproperlyConfiguredError(f"__pg_name__ meta required on: {cls}")
        return super().__new__(cls, code, title, *args, **kwargs)


ET = TypeVar("ET")


class IntStrEnum(_EncodeMixin, enum.Enum):
    # attributes
    code: str
    title: int

    # cache titles
    _ignore_ = ["_title_map"]
    _title_map: dict[str, Any] = {}

    def __new__(cls, code, title):
        #  invalidate cache if required
        if hasattr(cls, "_title_map"):
            delattr(cls, "_title_map")

        # check uniques
        if any(code == e.code for e in cls):
            raise exc.ImproperlyConfiguredError(f"{cls.__name__} have duplicate codes")
        if any(title == e.title for e in cls):
            raise exc.ImproperlyConfiguredError(f"{cls.__name__} have duplicate titles")

        # create object
        obj = object.__new__(cls)
        obj._value_ = code
        obj.code = code
        obj.title = title
        return obj

    @classmethod
    def _missing_(cls, value: object):
        # early return and normalize
        if isinstance(value, int) or not isinstance(value, str):
            # raise exc.InvalidParamValueError(f'{value} is not valid value for {cls.__name__}')
            raise ValueError(f"{value} is not valid value for {cls.__name__}")

        value = value.lower()

        # create cache on-demand
        if not hasattr(cls, "_title_map"):
            cls._title_map = {e.title.lower(): e for e in cls}

        result = cls._title_map.get(value, None)
        if result is None:
            # raise exc.InvalidParamValueError(f'{value} is not valid value for {cls.__name__}')
            raise ValueError(f"{value} is not a valid value for {cls.__name__}")
        else:
            return result

    def response_encode(self, request=None) -> dict:
        return self.title


class IntStrEnumType(sa.types.TypeDecorator, ScalarCoercible):
    # meta
    impl = sa.Integer

    @property
    def python_type(self):
        return self._enum_type

    _enum_type: type[ET]
    _impl_type: type[sa.types.Integer]

    def __init__(
        self,
        enum_type: type[ET],
        impl_type: type[sa.Integer] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._enum_type = enum_type
        self._impl_type = impl_type

    def load_dialect_impl(self, dialect):
        if self._impl_type is not None:
            return dialect.type_descriptor(self._impl_type)
        else:
            return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value: ET | None, dialect):
        if value is None:
            return None

        if isinstance(value, IntStrEnum):
            return value.value
        else:
            return value

    def process_result_value(self, value: Any | None, dialect):
        if value is None:
            return None
        try:
            return self._enum_type(value)
        except ValueError as e:
            raise exc.InvalidParamValueError(f"Unknown enum value: {value}") from e

    def _coerce(self, value: Any | None) -> ET | None:
        if value is not None and not isinstance(value, self._enum_type):
            try:
                return self._enum_type(value)
            except ValueError as e:
                raise exc.InvalidParamValueError(f"Unknown enum value: {value}") from e
        return value


# database enums
@enum.unique
class UserRole(PGEnumMixin, enum.Enum):
    __pg_name__ = "bp_t_user_role"

    # values
    ADMIN = ("ADMIN", "Администратор")
    OPERATOR = ("OPERATOR", "Оператор")


@enum.unique
class UserEventCode(IntStrEnum):
    # auth
    LOGIN = (1, "Авторизация в системе")
    LOGIN_FAILED = (2, "Ошибка авторизации")

    # profile
    PASSWORD_CHANGE = (101, "Смена пароля")
