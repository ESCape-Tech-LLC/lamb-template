from django.urls import re_path

# Project
from api.views import HandbooksView, PingView

app_name = "api"

handler404 = "lamb.utils.default_views.page_not_found"
handler400 = "lamb.utils.default_views.bad_request"
handler500 = "lamb.utils.default_views.server_error"

urlpatterns = [
    # main
    re_path(r"^configs/?$", HandbooksView, name="configs"),
    # healthcheck
    re_path(r"^ping/?$", PingView, name="ping"),
]
