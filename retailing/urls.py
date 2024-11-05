from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from retailing.apps import RetailingConfig
from retailing.views import SupplierListApiView, SupplierCreateApiView, SupplierUpdateApiView, SupplierDestroyApiView, \
    SupplierDetailApiView, CategoryViewSet, CountryViewSet, ProductViewSet, WarehouseViewSet, OrderListApiView, \
    OrderDetailApiView, OrderCreateApiView, OrderUpdateApiView, OrderDestroyApiView, PayableViewSet

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
router_product = SimpleRouter()
router_product.register("product", ProductViewSet, basename="product")
router_country = SimpleRouter()
router_country.register("country", CountryViewSet, basename="country")
router_warehouse = SimpleRouter()
router_warehouse.register("warehouse", WarehouseViewSet, basename="warehouse")
router_payable = SimpleRouter()
router_payable.register("payable", PayableViewSet, basename="payable")

urlpatterns = [
    path("supplier/", SupplierListApiView.as_view(), name="supplier_list"),
    path("supplier/create/", SupplierCreateApiView.as_view(), name="supplier_create"),
    path("supplier/<int:pk>/", SupplierDetailApiView.as_view(), name="supplier_retrieve"),
    path("supplier/update/<int:pk>/", SupplierUpdateApiView.as_view(), name="supplier_update"),
    path("supplier/delete/<int:pk>/", SupplierDestroyApiView.as_view(), name="supplier_delete"),
    path("order/", OrderListApiView.as_view(), name="order_list"),
    path("order/create/", OrderCreateApiView.as_view(), name="order_create"),
    path("order/<int:pk>/", OrderDetailApiView.as_view(), name="order_retrieve"),
    path("order/update/<int:pk>/", OrderUpdateApiView.as_view(), name="order_update"),
    path("order/delete/<int:pk>/", OrderDestroyApiView.as_view(), name="order_delete"),
]
urlpatterns += router_category.urls
urlpatterns += router_product.urls
urlpatterns += router_country.urls
urlpatterns += router_warehouse.urls
urlpatterns += router_payable.urls
