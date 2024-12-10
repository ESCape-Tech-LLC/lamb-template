from __future__ import annotations

import logging
import secrets
import uuid
from typing import Any, Self

from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    ForeignKey,
    Identity,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, SMALLINT
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    object_session,
    relationship,
)

from django.contrib.auth.hashers import check_password, make_password

import lamb.exc as exc
from lamb.db import DeclarativeBase
from lamb.db.logging import sql_logging_enable
from lamb.db.mixins import TimeMarksMixinTZ
from lamb.json.mixins import ResponseEncodableMixin
from lamb.types.annotations.postgresql import (
    bool_t,
    int_b,
    jsonb,
    str_ci,
    str_v,
    timestamp_tz,
    uuid_pk,
)
from lamb.utils import TZ_MSK, tz_now

from core.constants import (
    IntStrEnumType,
    PGEnumMixin,
    UserEventCode,
    UserRole,
)

logger = logging.getLogger(__name__)

sql_logging_enable()


# utils
class PG_ENUM(ENUM):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and issubclass(args[0], PGEnumMixin):
            _enum = args[0]
            kwargs["values_callable"] = lambda obj: [e.value for e in obj]
            kwargs["name"] = _enum.__pg_name__
        super().__init__(*args, **kwargs)


# admin
class Base(ResponseEncodableMixin, TimeMarksMixinTZ, DeclarativeBase):
    __abstract__ = True


class AbstractUser(Base):
    __tablename__ = "role_user_base"

    # columns
    user_id: Mapped[uuid_pk]
    role: Mapped[UserRole] = mapped_column(PG_ENUM(UserRole))
    password_hash: Mapped[str_v]
    is_active: Mapped[bool_t]

    # methods
    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str):
        def setter(_raw_password):
            self.set_password(_raw_password)
            try:
                session = object_session(self)
                session.commit()
            except (SQLAlchemyError, DBAPIError):
                pass

        return check_password(raw_password, self.password_hash, setter)

    def change_password(self, password_old: str, password_new: str):
        """Updates password for user"""
        if self.password_hash is not None and not self.check_password(password_old):
            raise exc.AuthCredentialsInvalidError("Invalid old password value")
        self.set_password(password_new)

    # mapper
    __mapper_args__ = {"polymorphic_on": role}


class AccessToken(ResponseEncodableMixin, TimeMarksMixinTZ, DeclarativeBase):
    __tablename__ = "role_access_token"

    # columns
    access_token: Mapped[str_ci] = mapped_column(primary_key=True)
    refresh_token: Mapped[str_ci] = mapped_column(unique=True)
    time_expire: Mapped[timestamp_tz]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(AbstractUser.user_id, onupdate="CASCADE", ondelete="CASCADE"))

    # relations
    user: Mapped[AbstractUser] = relationship()

    # methods
    @classmethod
    def generate(cls, user: AbstractUser) -> Self:
        # move ttl to configs
        ttl = 60 * 60 * 24

        result = AccessToken()
        result.user = user

        result.time_expire = tz_now() + relativedelta(seconds=ttl)
        result.access_token = secrets.token_urlsafe(64)
        result.refresh_token = secrets.token_urlsafe(64)

        return result

    @classmethod
    def response_attributes(cls) -> list[Any]:
        return [
            cls.time_created,
            cls.time_updated,
            cls.time_expire,
            cls.access_token,
            cls.refresh_token,
            cls.user_id,
        ]


class Admin(AbstractUser):
    __tablename__ = "role_admin"
    __mapper_args__ = {"polymorphic_identity": UserRole.ADMIN}

    # columns
    admin_id: Mapped[uuid_pk] = mapped_column(ForeignKey(AbstractUser.user_id, onupdate="CASCADE", ondelete="CASCADE"))


class UserEvent(Base):
    __tablename__ = "role_user_event"
    # columns
    event_id: Mapped[int_b] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(AbstractUser.user_id, onupdate="CASCADE", ondelete="CASCADE"))
    event_code: Mapped[UserEventCode] = mapped_column(IntStrEnumType(enum_type=UserEventCode, impl_type=SMALLINT))
    context: Mapped[jsonb] = mapped_column(default={}, server_default=text("'{}'::JSONB"))

    # relations
    user: Mapped[AbstractUser] = relationship(lazy="selectin", foreign_keys=[user_id])

    # methods
    def response_encode(self, request=None) -> dict:
        result = super().response_encode(request)

        result.pop("user_id")
        result.pop("context")
        result.pop("event_code")

        if self.user is None:
            initiator = None
        elif isinstance(self.user, Operator):
            initiator = self.user.login
        else:
            initiator = self.user.email

        result["visual_info"] = {
            "tm": self.time_created,
            "tms": self.time_created.astimezone(TZ_MSK).strftime("%d.%m.%Y %H:%M (МСК)"),
            "event_code": self.event_code.value,
            "event_title": self.event_code.title,
            "subject": self.context.get("subject"),
            "comment": self.context.get("comment"),
            "initiator": initiator,
        }

        return result


class Operator(AbstractUser):
    __tablename__ = "role_operator"
    __mapper_args__ = {"polymorphic_identity": UserRole.OPERATOR}

    # columns
    operator_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey(AbstractUser.user_id, onupdate="CASCADE", ondelete="CASCADE")
    )
