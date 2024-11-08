from django.db.models import Sum, Q
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny

from retailing.models import Supplier, Category, Country, Product, Warehouse, Order, Payable
from retailing.paginations import CategoryPaginator, SupplierPaginator, CountryPaginator, ProductPaginator, \
    WarehousePaginator, OrderPaginator, PayablePaginator
from retailing.serialaizer import SupplierSerializer, CategorySerializer, CountrySerializer, SupplierSerializerReadOnly, \
    ProductSerializer, ProductSerializerReadOnly, WarehouseSerializer, OrderSerializer, OrderSerializerReadOnly, \
    PayableSerializer
from users.models import Users
from users.permissions import IsActiveAndNotSuperuser


class CountryViewSet(viewsets.ModelViewSet):
    """Представление для стран. Страны загружаются командой fill_counties из файла counties.json
    скачанного из интернет ресурса."""

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
    """Создание поставщика. Пользователь может создает поставщика и становится сотрудником у поставщика. Другого
    поставщика он создать не может, но может других пользоватерелей зарегистрировать в своей компании."""

    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    def perform_create(self, serializer):
        """Создаем поставщика и заполним у пользователя номер поставщика."""
        if self.request.user.supplier_id is not None:
            supplier_object = Supplier.objects.get(pk=self.request.user.supplier_id)
            raise ValidationError(
                f"Этот сотрудник уже зарегистрировал поставщика {supplier_object.name}!"
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
    """Право на изменения только у сотрудника компании поставщика."""
    serializer_class = SupplierSerializer

    def get_queryset(self):
        return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_update(self, serializer):
        supplier = serializer.save()
        supplier.save()
    permission_classes = (IsActiveAndNotSuperuser,)


class SupplierDestroyApiView(DestroyAPIView):
    """Право на удаление только у сотрудника компании поставщика."""

    def get_queryset(self):
        return Supplier.objects.filter(pk=self.request.user.supplier_id)

    def perform_destroy(self, serializer):
        """Сначала отвязываем от пользователей id компании, затем удалаем саму компанию если это не нарушает
        целостность БД (отслеживается on_delete=models.PROTECT)."""
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
    """Представление для товаров. Продукт может создавать только сотрудник завода производителя (вендора)."""

    def get_queryset(self):
        if self.action == "destroy" and Order.objects.filter(product=self.kwargs["pk"]) is not None:
            raise ValidationError(
                f"Невозможно удалить продукт - он находится в обороте !"
            )

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
        if self.action == "create" and self.request.user.supplier_type != "vendor":
            raise ValidationError(
                f"Продукт может создавать только представитель вендора !"
            )
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

    serializer_class = WarehouseSerializer
#    pagination_class = WarehousePaginator

    permission_classes = (IsActiveAndNotSuperuser,)


class OrderListApiView(ListAPIView):
    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user.supplier)

    serializer_class = OrderSerializerReadOnly
    # pagination_class = OrderPaginator
    permission_classes = (IsActiveAndNotSuperuser,)


class OrderCreateApiView(CreateAPIView):
    """Реализованы операции addition - пополнение склада вендором и buying - покупка другими участниками торговой сети"""

    serializer_class = OrderSerializer
    permission_classes = (IsActiveAndNotSuperuser,)

    def perform_create(self, serializer):
        operation = serializer.validated_data["operation"]
        supplier = serializer.validated_data["supplier"]

        if operation == "addition" and self.request.user.supplier_type != "vendor":
            raise ValidationError(
                f"Пополнить склад готовой продукций может только вендор !"
            )
        if operation == "addition" and self.request.user.supplier_type == "vendor" and supplier.pk != self.request.user.supplier_id:
            raise ValidationError(
                f"Пополнить склад готовой продукции может только сотрудник вендора !"
            )

        if operation == "buying" and  supplier.pk == self.request.user.supplier_id:
            raise ValidationError(
                f"Нельзя купить товар у самого себя !"
            )

        if operation == "buying" and self.request.user.supplier_type == "vendor":
            raise ValidationError(
                f"Вендор может пополнить склад готовой продукции но не может купить !"
            )

        if operation == "buying" and self.request.user.supplier_type == "distributor" and supplier.type != "vendor":
            raise ValidationError(
                f"Дистрибьютор может купить товар только у завода производителя !"
            )

        if operation == "buying" and self.request.user.supplier_type == "retailer" and supplier.type not in ["vendor", "distributor"]:
            raise ValidationError(
                f"Ритейлер может купить товар только у завода производителя (вендора) или дистрибьютера !"
            )

        if operation == "buying":
            # проверяем есть ли у поставщика требуемое количество товара
            warehouse_quantity = Warehouse.objects.filter(owner=supplier.pk, product=serializer.validated_data["product"]).aggregate(Sum("quantity"))
            if warehouse_quantity["quantity__sum"] is None:
                raise ValidationError(
                    f"У поставщика отсутствует требуемый товар !"
                )
            if warehouse_quantity["quantity__sum"] < serializer.validated_data["quantity"]:
                raise ValidationError(
                    f"У поставщика недостаточно требуемого товара !"
                )

        order = serializer.save()
        order.user = self.request.user
        order.owner = self.request.user.supplier
        order.amount = order.price*order.quantity
        order.save()
        if operation in ["addition", "buying"]:
            # перемещаем купленный товар на остаток покупателя
            warehouse_owner = list(Warehouse.objects.filter(owner=order.owner.id, product=order.product.id))
            if len(warehouse_owner) == 1:
                warehouse_owner[0].quantity += order.quantity
                warehouse_owner[0].save()
            else:
                Warehouse.objects.create(
                    owner=order.owner,
                    product=order.product,
                    quantity=order.quantity
                )
            print(self.request.user.username)
            if self.request.user.supplier_type != "vendor":
                # уменьшаем у поставщика остаток товара если это покупка
                warehouse_supplier = list(Warehouse.objects.filter(owner=order.supplier, product=order.product))
                warehouse_supplier[0].quantity -= order.quantity
                warehouse_supplier[0].save()

            if self.request.user.supplier_type != "vendor" and order.quantity != order.payment_amount:
                print(333333333333333333333)
                # Если стоимость товара отличается от оплаченной суммы то разницу записываем в долг поставщику
                # или покупателю. Если положительная сумма должник покупатель, отрицательная - поставщик.
                payable = list(Payable.objects.filter(owner=order.owner, supplier=order.supplier))
                if len(payable) == 1:
                    payable[0].amount += order.amount - order.payment_amount
                    payable[0].save()
                else:
                    Payable.objects.create(
                        owner=order.owner,
                        supplier=order.supplier,
                        amount=order.amount - order.payment_amount
                    )


class OrderDetailApiView(RetrieveAPIView):
    def get_queryset(self):
        return Order.objects.filter(pk=self.kwargs["pk"], user=self.request.user)

    serializer_class = OrderSerializerReadOnly
    permission_classes = (IsActiveAndNotSuperuser,)


class OrderUpdateApiView(UpdateAPIView):
    def get_queryset(self):
        raise ValidationError(
            "Невозможно изменить операцию, разрешены только создание и просмотр !"
        )


class OrderDestroyApiView(DestroyAPIView):
    def get_queryset(self):
        raise ValidationError(
            "Невозможно удалить операцию, разрешены только создание и просмотр !"
        )


class PayableViewSet(viewsets.ModelViewSet):
    """Представление для должников. Модель (таблица) заполняется (изменяется) автоматически по мере
     выполнения операуий покупки товаров у постащиков. Задолженность может возникнуть как у покупателя, таки и
     у поставщика. Разрешен только просмотр астивным пользователям сети своих долгов (owner = supplier или
     supplier = supplier). Удаление или изменение задолженнности из API невозможно. Списание задолженности возможно
     только с админ-панели."""

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            # из модели задолженностей выводятся только несписанные задолженности.
            return Payable.objects.filter(Q(owner=self.request.user.supplier) | Q(supplier=self.request.user.supplier), is_paid=False)
        else:
            raise ValidationError(
                "Невозможно создать, изменить и удалить задолженность, разрешен только просмотр !"
            )

    serializer_class = PayableSerializer
#    pagination_class = PayablePaginator
    permission_classes = (IsActiveAndNotSuperuser,)


