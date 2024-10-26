from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from retailing.models import Supplier, Category, Country
from retailing.paginations import CategoryPaginator, SupplierPaginator, CountryPaginator
from retailing.serialaizer import SupplierSerializer, CategorySerializer, CountrySerializer
from users.permissions import IsSuperuser, IsActive


class CountryViewSet(viewsets.ModelViewSet):
    """Представление для категорий товаров."""

    queryset = Country.objects.all().order_by("id")
    serializer_class = CountrySerializer
#    pagination_class = CountryPaginator

    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ("name",)
    search_fields = ("name",)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (AllowAny,)
        # else:
        #     self.permission_classes = (False,)
        return super().get_permissions()


class SupplierListApiView(ListAPIView):
    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Supplier.objects.all().order_by("id")
        else:
            return Supplier.objects.filter(user=self.request.user)

    serializer_class = SupplierSerializer
    # pagination_class = SupplierPaginator


class SupplierDetailApiView(RetrieveAPIView):
    pass


class SupplierCreateApiView(CreateAPIView):
    pass


class SupplierUpdateApiView(UpdateAPIView):
    pass


class SupplierDestroyApiView(DestroyAPIView):
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление для категорий товаров."""

    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    # pagination_class = CategoryPaginator

    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ("name",)
    search_fields = ("name",)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (IsSuperuser, IsActive,)
        return super().get_permissions()


