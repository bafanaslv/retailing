from django.db import models
from datetime import date

from config import settings
from users.models import Users

NULLABLE = {"blank": True, "null": True}


class Country(models.Model):
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
        return f"Страна: {self.name} код: {self.code}"


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Наименование",
        help_text="Введите наименование категории",
    )
    description = models.TextField(
        verbose_name="Опиcание", help_text="Введите описание категории"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="нименование поставщика", unique=True)
    email = models.EmailField(unique=True, verbose_name="E-mail")
    country = models.ForeignKey(
        Country,
        related_name="supplier_country",
        on_delete=models.PROTECT,
        verbose_name="страна",
    )
    city = models.CharField(max_length=100, verbose_name="город")
    street = models.CharField(max_length=100, verbose_name="улица")
    house_number = models.CharField(max_length=10, verbose_name="номер дома")
    date_create = models.DateField(verbose_name="дата создания", default=date.today)


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Наименование"
    )
    description = models.TextField(
        verbose_name="Опиcание", **NULLABLE
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="categories",
        verbose_name="Категория"
    )
    image = models.ImageField(
        upload_to="catalog/media",
        verbose_name="Изображение", **NULLABLE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    owner = models.ForeignKey(
        Users,
        verbose_name='Владелец',
        on_delete=models.CASCADE,
        related_name="owner"
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name='Поставщик',
        on_delete=models.CASCADE,
        related_name="supplier"
    )
    is_published = models.BooleanField(default=False, verbose_name='Опубликован')
    view_counter = models.PositiveIntegerField(
        default=0,
        verbose_name="Счетчик проcмотров"
    )
