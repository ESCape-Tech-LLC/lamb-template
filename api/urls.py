from django.urls import re_path

from api.views import HandbooksView, PingView

app_name = "api"

urlpatterns = [
    # main
    re_path(r"^configs/?$", HandbooksView, name="configs"),
    # healthcheck
    re_path(r"^ping/?$", PingView, name="ping"),
]
