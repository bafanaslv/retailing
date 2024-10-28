from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from retailing.models import Supplier, Category, Country
from retailing.paginations import CategoryPaginator, SupplierPaginator, CountryPaginator
from retailing.serialaizer import SupplierSerializer, CategorySerializer, CountrySerializer, SupplierSerializerReadOnly
from users.models import Users
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
        else:
            self.permission_classes = (~AllowAny,)
        return super().get_permissions()


class SupplierListApiView(ListAPIView):
    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Supplier.objects.all().order_by("id")
        else:
            return Supplier.objects.filter(user=self.request.user)

    serializer_class = SupplierSerializerReadOnly
    # pagination_class = SupplierPaginator


class SupplierDetailApiView(RetrieveAPIView):

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Supplier.objects.all()
        else:
            return Supplier.objects.filter(user=self.request.user)

    serializer_class = SupplierSerializerReadOnly
    permission_classes = (IsAuthenticated,)


class SupplierCreateApiView(CreateAPIView):
    """Создание поставщика. Пользователь может создать только одного поставщика. Суперюзер не имеет такого права."""

    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    def perform_create(self, serializer):
        """Создаем поставщика и заполним у пользователя номер поставщика."""
        if self.request.user.supplier_id is not None:
            supplier_object = Supplier.objects.get(pk=self.request.user.supplier_id)
            raise ValidationError(
                f"Этот сотрудник уже зарегистрировал компанию {supplier_object.name}!"
            )

        supplier = serializer.save()
        supplier.user = self.request.user
        supplier = serializer.save()
        supplier.save()
        self.request.user.supplier_id = supplier.id
        self.request.user.save()
    permission_classes = (IsActive, ~IsSuperuser,)


class SupplierUpdateApiView(UpdateAPIView):

    serializer_class = SupplierSerializer

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            raise ValidationError(
                f"У вас недостаточно прав для выполнения данного действия!"
            )
        else:
            return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_update(self, serializer):
        supplier = serializer.save()
        supplier.save()
    permission_classes = (IsActive,)


class SupplierDestroyApiView(DestroyAPIView):

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            raise ValidationError(
                f"У вас недостаточно прав для выполнения данного действия!"
            )
        else:
            return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_destroy(self, serializer):
        """Сначала отввязываем от пользователя id компании, затем удалаем саму компанию."""
        sup_id = self.request.user.supplier_id
        self.request.user.supplier_id = None
        self.request.user.save()
        Supplier.objects.filter(pk=sup_id).delete()

    permission_classes = (IsActive,)


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

