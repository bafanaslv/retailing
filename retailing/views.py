from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from retailing.models import Supplier, Category
from retailing.paginations import CategoryPaginator, SupplierPaginator
from retailing.serialaizer import SupplierSerializer, CategorySerializer
from users.permissions import IsSuperuser, IsActive


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
