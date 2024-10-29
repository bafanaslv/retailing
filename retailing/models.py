import datetime

from django.db import models
from datetime import date

from config import settings
# from users.models import Users

NULLABLE = {"blank": True, "null": True}


class Country(models.Model):
    """Страна где зарегистрован поставщик товара."""
    code = models.CharField(
        max_length=2, unique=True, verbose_name="код страны"
    )
    name = models.CharField(
        max_length=60, unique=True, verbose_name="название страны"
    )

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def str(self):
        return f"Страна: {self.id} {self.name}"


class Supplier(models.Model):
    """Участниками торговой сети делятся на три группы (типа): вендоры или производители товаров, дистрибьютеры -
    крупные оптовые торговцы закупающие товар у вендоров и ритейлеры (мелкие фирмы или индивидуальные предприниматели).
    На самом деле схема сложнее. Атрибут user заполняется при регистрации поставщика. В это же момент у пользователя
    заполняется поле supplier_id указывающее, что пользователь является сотрудником компании. На компанию в дальнейшем
    можно зарегистрировать других пользователей."""

    TYPE = [
        ("vendor", "производитель"),
        ("distributor", "дистрибьютер"),
        ("retailer", "ритейлер"),
    ]

    name = models.CharField(max_length=100, verbose_name="нименование поставщика", unique=True)
    type = models.CharField(max_length=11, choices=TYPE, verbose_name="тип участника сети")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="сотрудник",
        related_name="supplier_user",
        ** NULLABLE,
    )
    country = models.ForeignKey(
        Country,
        related_name="supplier_country",
        on_delete=models.PROTECT,
        verbose_name="страна",
    )
    city = models.CharField(max_length=100, verbose_name="город")
    street = models.CharField(max_length=100, verbose_name="улица")
    house_number = models.CharField(max_length=10, verbose_name="номер дома")
    created_at = models.DateTimeField(verbose_name="время создания", auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.type} {self.country}"


class Category(models.Model):
    """Товары электроники как и другие типы товаров могут делиться на разные категории
    (компьютеры, телефоны, телевизоры, бытовая техника и так далее)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="наименование",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    """Справочник продукции. Доступ только для сотрудников заводов изготовителей."""

    name = models.CharField(
        max_length=100,
        verbose_name="наименование"
    )
    model = models.TextField(
        verbose_name="модель", **NULLABLE
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="product_category",
        verbose_name="категория"
    )
    vendor = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="product_vendor",
        verbose_name='завод производитель'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="сотрудник",
        related_name="product_user",
    )
    release_date = models.DateField(verbose_name="дата выхода продукта на рынок")
    view_counter = models.PositiveIntegerField(
        default=0,
        verbose_name="счетчик проcмотров"
    )
    image = models.ImageField(
        upload_to="catalog/media",
        verbose_name="изображение", **NULLABLE
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class Payable(models.Model):
    """Кредиторская задолженность"""

    owner = models.ForeignKey(
        Supplier,
        verbose_name='владелец',
        on_delete=models.PROTECT,
        related_name="owner_payable"
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name='поставщик',
        on_delete=models.PROTECT,
        related_name="supplier_payable", **NULLABLE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="задолженность")
    is_paid = models.BooleanField(verbose_name="погашена", default=False)
    created_at = models.DateTimeField(verbose_name="время создания", auto_now_add=True)
    update_at = models.DateTimeField(verbose_name="время создания", **NULLABLE)
    paid_date = models.DateField(verbose_name="дата погашения", **NULLABLE)
