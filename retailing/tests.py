# Тесты созданы только для моделей поставщик (Supplier) и операции (Order).
# Тесты для моделей страна (Country), категория товара (Caterogry) и товар (Product) не создавались ввиду
# крайней их простоты и примитивности. Также не создавались тести на модели склад (Warehouse) и задолженности (Payable),
# поскольку в них хранится производная и динамическая информация при выполнении функций API над моделью операции (Order).
# API для них создавались только для просмотра.

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from retailing.models import Supplier, Order, Product, Category, Country, Warehouse, Payable
from users.models import Users


class SupplierTestCase(APITestCase):
    """Тестирование CRUD авторов."""

    def setUp(self):
        self.user = Users.objects.create(
            username="Лукин В.М.",
            email="foxship@yandex.ru",
            password="123qwe",
            phone="+7 9655965915",
            is_personal_data="True",
            is_active="True",
        )
        self.country = Country.objects.create(code="US", name="США")
        self.client.force_authenticate(user=self.user)

    def test_supplier_create(self):
        url = reverse("retailing:supplier_create")
        data = {
            "id": 1,
            "name": "Sony Corporation",
            "type": "vendor",
            "email": "info@sony.us",
            "country": self.country.pk,
            "city": "New York",
            "street": "Manhattan",
            "house_number": 4
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.all().count(), 1)
        self.assertEqual(self.user.supplier_id, 3)
        self.assertEqual(Supplier.objects.get(pk=3).user_id, self.user.pk)

    def test_supplier_list(self):
        url = reverse("retailing:supplier_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_retrieve(self):
        url_create = reverse("retailing:supplier_create")
        data = {
            "id": 1,
            "name": "Sony Corporation",
            "type": "vendor",
            "email": "info@sony.us",
            "country": self.country.pk,
            "city": "New York",
            "street": "Manhattan",
            "house_number": 4
        }
        self.client.post(url_create, data)

        url = reverse("retailing:supplier_retrieve", args=(self.user.supplier_id,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Sony Corporation")

    def test_supplier_update(self):
        url_create = reverse("retailing:supplier_create")
        data = {
            "id": 1,
            "name": "Sony Corporation",
            "type": "vendor",
            "email": "info@sony.us",
            "country": self.country.pk,
            "city": "New York",
            "street": "Manhattan",
            "house_number": 4
        }
        self.client.post(url_create, data)

        url = reverse("retailing:supplier_update", args=(self.user.supplier_id,))
        data = {
            "type": "distributor",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("type"), "distributor")

    def test_supplier_delete(self):
        url_create = reverse("retailing:supplier_create")
        data = {
            "id": 1,
            "name": "Sony Corporation",
            "type": "vendor",
            "email": "info@sony.us",
            "country": self.country.pk,
            "city": "New York",
            "street": "Manhattan",
            "house_number": 4
        }
        self.client.post(url_create, data)

        url = reverse("retailing:supplier_delete", args=(self.user.supplier_id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.all().count(), 0)


class OrderTestCaseAddition(APITestCase):
    """Тестирование CRUD авторов."""

    def setUp(self):
        self.user = Users.objects.create(
            username="Лукин В.М.",
            email="foxship@yandex.ru",
            password="123qwe",
            phone="+7 9655965111",
            is_personal_data="True",
            is_active="True",
        )
        self.country = Country.objects.create(code="US", name="США")
        self.category = Category.objects.create(name="Телевизоры")
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name="Sony Corporation",
            type="vendor",
            email="info@sony.us",
            country_id=self.country.pk,
            city="New York",
            street="Manhattan",
            house_number=4,
            user_id=self.user.pk
        )
        self.user.supplier_id = self.supplier.pk
        self.user.supplier_type = self.supplier.type
        self.product = Product.objects.create(
            name="Sony",
            model="Bravia",
            category_id=self.category.pk,
            user_id=self.user.pk,
            supplier_id=self.supplier.pk,
            release_date="2024-10-01"
        )

    def test_order_create_vendor(self):
        url = reverse("retailing:order_create")
        data = {
            "owner": self.user.supplier_id,
            "supplier": self.supplier.pk,
            "product": self.product.pk,
            "operation": "addition",
            "user": self.user.pk,
            "quantity": 5,
            "price": 45000.00,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Warehouse.objects.all().count(), 1)
        self.assertEqual(Payable.objects.all().count(), 0)

        url = reverse("retailing:order_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("retailing:order_retrieve", args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(pk=1).owner_id, self.user.supplier_id)


class OrderTestCaseBuying(APITestCase):
    """Тестирование CRUD авторов."""
    def setUp(self):
        self.user = Users.objects.create(
            username="Бояджи С.В.",
            email="sveta@yandex.ru",
            password="123qwe",
            phone="+7 9655965222",
            is_personal_data="True",
            is_active="True",
        )
        self.country = Country.objects.create(code="US", name="США")
        self.category = Category.objects.create(name="Телевизоры")
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name="Sumsung Corporation",
            type="distributor",
            email="info@sumsung.us",
            country_id=self.country.pk,
            city="New York",
            street="Manhattan",
            house_number=4,
            user_id=self.user.pk
        )
        self.product = Product.objects.create(
            name="Sony",
            model="Bravia",
            category_id=self.category.pk,
            user_id=self.user.pk,
            supplier_id=self.supplier.pk,
            release_date="2024-10-01"
        )

    def test_order_create_distributor(self):
        self.user.supplier_id = self.supplier.pk
        self.user.supplier_type = self.supplier.type

        url = reverse("retailing:order_create")
        data = {
            "owner": self.user.supplier_id,
            "supplier": 1,
            "product": self.product.pk,
            "operation": "buying",
            "user": self.user.pk,
            "quantity": 3,
            "price": 45000.00,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Warehouse.objects.all().count(), 1)
        self.assertEqual(Payable.objects.all().count(), 1)
