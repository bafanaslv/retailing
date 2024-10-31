from django.contrib import admin
from django.urls import include, path

from retailing.urls import schema_view

urlpatterns = [
    path("", include("retailing.urls", namespace="supplier")),
    path("", include("retailing.urls", namespace="order")),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
