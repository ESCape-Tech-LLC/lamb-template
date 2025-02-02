from django.urls import include, re_path

handler404 = "lamb.utils.default_views.page_not_found"
handler400 = "lamb.utils.default_views.bad_request"
handler500 = "lamb.utils.default_views.server_error"

urlpatterns = [
    re_path(r"api/", include("api.urls", namespace="api")),
]
