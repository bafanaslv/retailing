from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Users


class UsersTestCase(APITestCase):
    """Тестирование CRUD пользователей."""

    def setUp(self):
        """Готовим двух пользователей для тестирования, суперюзера и пользователя сотрудника вендора (неактивного)"""

        self.user = Users.objects.create(
            email="ivc@gmail.com",
            password="123qwe",
            is_superuser=True,
        )
        self.user_vendor = Users.objects.create(
            username="Лукин В.М.",
            email="foxship@zdship.ru",
            password="123qwe",
            phone="+7 9655965915",
            tg_chat_id="743470705",
            is_personal_data="True",
            is_active="False",
        )
        self.client.force_authenticate(user=self.user)

    def test_user_create(self):
        """Создаем еще одного пользователя и проверяем общее количество."""

        url = reverse("users:register")
        data = {
            "username": "Бояджи С.В.",
            "email": "sveta@zdship.ru",
            "password": "123qwe",
            "phone": "+7 9655965222",
            "is_personal_data": "True",
            "is_active": "False",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Users.objects.all().count(), 3)

    def test_user_list(self):
        """Выводим общий список всех пользователей."""

        url = reverse("users:users_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_retrieve(self):
        """Выводим конкретного пользователя."""

        url = reverse("users:users_retrieve", args=(self.user.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("tg_chat_id"), self.user.tg_chat_id)

    def test_user_update(self):
        """Активируем второго пользователя и проверяем результат."""

        url = reverse("users:users_update", args=(self.user_vendor.pk,))
        data = {
            "is_active": "True",
        }
        response = self.client.patch(url, data)
        print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("is_active"), "True")

    def test_user_delete(self):
        """Удаляем пользователя и проверяем общее количество оставшихся."""
        url = reverse("users:users_delete", args=(self.user.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Users.objects.all().count(), 1)
