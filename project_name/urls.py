from django.urls import include, re_path

urlpatterns = [
    re_path("", include("api.urls", namespace="api")),
]
