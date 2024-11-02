from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from retailing.models import Supplier, Category, Country, Product, Warehouse, Order
from retailing.paginations import CategoryPaginator, SupplierPaginator, CountryPaginator, ProductPaginator, \
    WarehousePaginator, OrderPaginator
from retailing.serialaizer import SupplierSerializer, CategorySerializer, CountrySerializer, SupplierSerializerReadOnly, \
    ProductSerializer, ProductSerializerReadOnly, WarehouseSerializer, OrderSerializer
from users.models import Users
from users.permissions import IsSuperuser, IsActive, IsActiveAndNotSuperuser


class CountryViewSet(viewsets.ModelViewSet):
    """Представление для стран."""

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
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializerReadOnly
    # pagination_class = SupplierPaginator
    permission_classes = (AllowAny,)


class SupplierDetailApiView(RetrieveAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializerReadOnly
    permission_classes = (AllowAny,)


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
        self.request.user.supplier_type = supplier.type
        self.request.user.save()
    permission_classes = (IsActiveAndNotSuperuser,)


class SupplierUpdateApiView(UpdateAPIView):

    serializer_class = SupplierSerializer

    def get_queryset(self):
        return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_update(self, serializer):
        supplier = serializer.save()
        supplier.save()
    permission_classes = (IsActiveAndNotSuperuser,)


class SupplierDestroyApiView(DestroyAPIView):

    def get_queryset(self):
        return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_destroy(self, serializer):
        """Сначала отввязываем от пользователей id компании, затем удалаем саму компанию."""
        sup_id = self.request.user.supplier_id
        user_list = list(Users.objects.filter(supplier_id=sup_id))
        for user in user_list:
            user.supplier_id = None
            user.save()
        self.request.user.supplier_id = None
        Supplier.objects.filter(pk=sup_id).delete()

    permission_classes = (IsActiveAndNotSuperuser,)


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление для категорий товаров."""

    def get_queryset(self):
        if self.action == "destroy" and Product.objects.filter(category=self.kwargs["pk"]) is not None:
            raise ValidationError(
                "Невозможно удалить категорию - есть зарегистрированные продукты !"
            )
        return Category.objects.all().order_by("id")

    serializer_class = CategorySerializer
    # pagination_class = CategoryPaginator

    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ("name",)
    search_fields = ("name",)

    permission_classes = (AllowAny,)


class ProductViewSet(viewsets.ModelViewSet):
    """Представление для товаров."""

    def get_queryset(self):
        if self.action in ["update", "retrieve", "destroy"]:
            return Product.objects.filter(pk=self.kwargs["pk"])
        else:
            return Product.objects.all()

    def get_serializer_class(self):
        if self.action in ["update", "create"]:
            return ProductSerializer
        else:
            return ProductSerializerReadOnly

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsActiveAndNotSuperuser,)
        return super().get_permissions()

    # pagination_class = ProductPaginator

    def perform_create(self, serializer):
        product = serializer.save()
        product.user = self.request.user
        product.supplier = self.request.user.supplier
        product.save()

    def retrieve(self, request, *args, **kwargs):
        """Увеличиваем количество промотров продукта."""
        obj = self.get_object()
        obj.view_counter = obj.view_counter + 1
        obj.save(update_fields=("view_counter", ))
        return super().retrieve(request, *args, **kwargs)

    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ("name",)
    search_fields = ("name", "category")


class WarehouseViewSet(viewsets.ModelViewSet):
    """Представление для складов товаров. Модель (таблица) заполняется (изменяется) автоматически по мере
     выполнения операуий покупки товаров у постащиков. Разрешен только просмотр астивными пользователями сети своих
     товаров (owner = supplier_id)."""

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Warehouse.objects.filter(owner=self.request.user.supplier_id)
        else:
            raise ValidationError(
                "Невозможно создать, изменить и удалить товар на складе, разрешен только просмотр !"
            )

    def perform_create(self, serializer):
        raise ValidationError(
            "Невозможно создать, изменить и удалить товар на складе, разрешен только просмотр !"
        )

    serializer_class = WarehouseSerializer
#    pagination_class = WarehousePaginator

    permission_classes = (IsActiveAndNotSuperuser,)


class OrderListApiView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # pagination_class = OrderPaginator
    permission_classes = (IsActiveAndNotSuperuser,)


class OrderCreateApiView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    permission_classes = (IsActiveAndNotSuperuser,)


class OrderDetailApiView(ListAPIView):
    pass


class OrderUpdateApiView(ListAPIView):
    pass


class OrderDestroyApiView(ListAPIView):
    pass




