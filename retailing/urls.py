from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from retailing.apps import RetailingConfig
from retailing.views import SupplierListApiView, SupplierCreateApiView, SupplierUpdateApiView, SupplierDestroyApiView, \
    SupplierDetailApiView, CategoryViewSet, CountryViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API управления торговой сетью электроники.",
        terms_of_service="http://localhost:8000/retailing/",
        contact=openapi.Contact(email="foxship@yandex.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

app_name = RetailingConfig.name

router_category = SimpleRouter()
router_category.register("category", CategoryViewSet, basename="category")
router_country = SimpleRouter()
router_country.register("country", CountryViewSet, basename="country")

urlpatterns = [
    path("supplier/", SupplierListApiView.as_view(), name="supplier_list"),
    path("supplier/create/", SupplierCreateApiView.as_view(), name="supplier_create"),
    path(
        "supplier/<int:pk>/", SupplierDetailApiView.as_view(), name="supplier_retrieve"
    ),
    path(
        "supplier/update/<int:pk>/",
        SupplierUpdateApiView.as_view(),
        name="supplier_update",
    ),
    path(
        "supplier/delete/<int:pk>/",
        SupplierDestroyApiView.as_view(),
        name="supplier_delete",
    ),
]
urlpatterns += router_category.urls
urlpatterns += router_country.urls
