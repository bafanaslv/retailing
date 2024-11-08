# В проекте предусмотрены два типа пользователей. Библиотекарь, обладающий всеми правами и читатель, который может
# проматривать авторов, списки и аннотации книг и разного рода информацию по полученным им книгам.
# Библиотекарь входит в группу librarian, через которого получает все права в приложении.

from django.contrib.auth.models import AbstractUser
from django.db import models

from retailing.models import Supplier

NULLABLE = {"blank": True, "null": True}


class Users(AbstractUser):
    """Пользователи сети. Поля supplier и supplier|_type добавлены для таго, чтобы каждый раз перед выполнением
    какой либо операции не знать где работает пользователь сети и к какому типу относится компания где он работает.
    """

    username = models.CharField(max_length=50, verbose_name="имя пользователя")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.CharField(max_length=15, verbose_name="телефон")
    is_personal_data = models.BooleanField(
        default=True, verbose_name="согласие на обработку персональных данных"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", **NULLABLE
    )
    tg_chat_id = models.CharField(
        max_length=50, verbose_name="Telergram chat_id", **NULLABLE
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="поставщик",
        on_delete=models.PROTECT,
        related_name="supplier_user",
        **NULLABLE,
    )
    supplier_type = models.CharField(
        max_length=11, verbose_name="тип участника сети", **NULLABLE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email}"
