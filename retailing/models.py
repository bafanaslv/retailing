from django.db import models
from datetime import date

from config import settings

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
        return f"Наименование: {self.name}, тип: {self.type}, страна: {self.country}"


class Category(models.Model):
    """Товары электроники как и другие типы товаров могут делиться на разные категории
    (компьютеры, телефоны, телевизоры, бытовая техника и так далее)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="наименование",
    )

    def __str__(self):
        return f"Категория товара: {self.name}"

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
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="product_supplier",
        verbose_name='завод производитель',
        ** NULLABLE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="сотрудник",
        related_name="product_user",
        **NULLABLE
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

    def __str__(self):
        return f"Наименование: {self.name}, модель: {self.name}, производитель: {self.supplier}"


class Warehouse(models.Model):
    """Склад (остатки) продукции."""

    owner = models.ForeignKey(
        Supplier,
        verbose_name='собстенник',
        on_delete=models.PROTECT,
        related_name="owner_warehouse"
    )
    product = models.ForeignKey(
        Product, verbose_name='товар',
        on_delete=models.PROTECT,
        related_name="owner_product"
    )
    quantity = models.PositiveIntegerField(verbose_name='количество')

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"Владелец: {self.owner.name}, продукт: {self.product.name}, количество: {self.quantity}"


class Payable(models.Model):
    """Задолженность. Могут быть оба вида заолженности, дебиторская (недопоставлен товар) и кредиторская
     (не заплачены деньги за весь товар или часть товара)."""

    owner = models.ForeignKey(
        Supplier,
        verbose_name='собственник',
        on_delete=models.PROTECT,
        related_name="owner_payable",
        ** NULLABLE
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name='поставщик',
        on_delete=models.PROTECT,
        related_name="supplier_payable"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="сумма задолженности")
    created_at = models.DateField(verbose_name="дата возникновения", default=date.today)
    is_paid = models.BooleanField(verbose_name="погашена", default=False)
    paid_date = models.DateField(verbose_name="дата погашения", **NULLABLE)

    class Meta:
        verbose_name = "Задолженность"
        verbose_name_plural = "Задолженности"

    def __str__(self):
        return f"Должник: {self.owner}, поставщик: {self.supplier}, сумма задолежности: {self.amount}"


class Order(models.Model):
    """Операции с продукцией. Операция addition может быть только у завода после отправки произведенной продукции
    на склад. У остальных участников пополнение склада происходит после попкупки (buying). """

    OPERATION = [
        ("addition", "пополнение склада"),
        ("buying", "покупка"),
        ("return", "возврат"),
        ("write_off", "списание"),
    ]

    owner = models.ForeignKey(
        Supplier,
        verbose_name='собственник',
        on_delete=models.PROTECT,
        related_name="order_owner",
        **NULLABLE
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name='поставщик',
        on_delete=models.PROTECT,
        related_name="order_supplier",
        **NULLABLE
    )
    product = models.ForeignKey(
        Product, verbose_name='товар',
        on_delete=models.PROTECT,
        related_name="order_product"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="сотрудник",
        related_name="order_user",
        **NULLABLE
    )
    operation = models.CharField(max_length=10, verbose_name='действие', choices=OPERATION)
    quantity = models.PositiveIntegerField(verbose_name="количество")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="цена")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="сумма продукции", **NULLABLE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="сумма оплаты", **NULLABLE)
    created_at = models.DateField(verbose_name="дата операции", default=date.today)

    class Meta:
        verbose_name = "Задолженность"
        verbose_name_plural = "Задолженности"

    def __str__(self):
        return f"Должник: {self.owner}, поставщик: {self.supplier}, сумма задолежности: {self.amount}"

