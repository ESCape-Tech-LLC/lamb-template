from __future__ import annotations

from django.conf import settings

from lamb.rest.decorators import rest_allowed_http_methods
from lamb.rest.rest_view import RestView
from lamb.utils import LambRequest

from core.constants import UserRole


@rest_allowed_http_methods(["GET"])
class HandbooksView(RestView):
    def get(self, _: LambRequest):
        enums = {"user_roles": UserRole}

        result = {}
        for key, _enum in enums.items():
            result[key] = [m.handbook_encode() for m in _enum if m.handbook_encode() is not None]

        result["main"] = {
            "some_other_config": 10,
        }
        return result


@rest_allowed_http_methods(["GET"])
class PingView(RestView):
    def get(self, _: LambRequest):
        return {"response": "pong", "version": settings.LAMB_APP_VERSION}
