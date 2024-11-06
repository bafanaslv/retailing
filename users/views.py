# Описание представления пользователи и сотрудники. Пользователи могут зарегистрироваться в системе и будут иметь
# доступ к компаниям (контактам) и продукции которые производят или которыми торгуют компании.
# Пользователь может зарегистрировать свою компанию (вендора, дистрибьютера или ритейлера) и становится сотрудником
# этой компании, но не имеет никаких дополнительных прав пока суперпользователь или сотрудник той же компаниии
# не подтвердит и не сделает пользователя аетивным (is_active = true). Суперпользователь может сам, по электронной
# заявке зарегистрировать сотрудника выдать ему права на управление компанией (is_active = true).
# Таким же образом активный сотрудник комании может сделает пользователя активным если он зарегистровался
# в той же компании.

# Примечание: суперпользователь создается командой csu и имеет права только на управление пользователями.

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework_simplejwt.views import TokenObtainPairView

from retailing.models import Supplier, Product
from users.models import Users
from users.permissions import IsActive, IsSuperuser, IsActiveAndNotSuperuser
from users.serializer import UserSerializer, UserTokenObtainPairSerializer, UserSerializerReadOnly, \
    UserSerializerForSuperuser


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializerReadOnly
    queryset = Users.objects.all()
    permission_classes = [IsSuperuser,]


class UserRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserSerializerReadOnly

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Users.objects.all()
        else:
            user = Users.objects.get(pk=self.kwargs["pk"])
            if user.supplier != self.request.user.supplier:
                raise ValidationError(
                "У вас недостаточно прав для просмотра учетных данных пользователя !"
            )
            return Users.objects.filter(pk=self.kwargs["pk"])
    permission_classes = [IsActive,]


class UserUpdateAPIView(UpdateAPIView):
    """Изменение аттрибутов пользователя, кроме принадлежности работодателю (supplier_id > 0), если он уже зарегистирован
    в торговой сети за определенной компанией. Можно отвязать (supplier_id = None), если это не нарушает целостность БД
    а затем заново привязать к другой компании."""

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Users.objects.all()
        else:
            # проверяем действительно ли пользователь зарегистрировался в той же компании
            user = Users.objects.get(pk=self.kwargs["pk"])
            if user.supplier != self.request.user.supplier:
                raise ValidationError(
                    "У вас недостаточно прав для изменения учетных данных пользователя !"
                )
            return Users.objects.filter(pk=self.kwargs["pk"])

    def get_serializer_class(self):
        if IsActiveAndNotSuperuser().has_permission(self.request, self):
            user = Users.objects.get(pk=self.kwargs["pk"])
            if user == self.request.user:
                # необходимо дать разрешение менять собственные данные
                return UserSerializer
            else:
                return UserSerializerForSuperuser
        else:
            return UserSerializer

    def perform_update(self, serializer):
        user_obj = Users.objects.get(pk=self.kwargs["pk"])
        user = serializer.save()
        if IsSuperuser().has_permission(self.request, self):
            if user.is_personal_data:
                user_obj.is_active = user.is_active
            else:
                raise ValidationError(
                    "Пользователь не дал разрешение на обработку персональных данных !"
                )
        else:
            if user.supplier is not None and user_obj.supplier is not None and user_obj.supplier_id != user.supplier_id:
                raise ValidationError(
                    "Невозможно изменить место работы у пользователя зарегистрированного в сети за другой компанией !"
                )

            if user.supplier is not None:
                supplier_object = Supplier.objects.get(pk=user.supplier_id)
                user.supplier_type = supplier_object.type
            else:
                user.supplier_type = None
            user.set_password(self.request.data.get("password"))
        user.save()
    permission_classes = [IsActive,]


class UserDestroyAPIView(DestroyAPIView):

    def get_queryset(self):
        user_obj = Users.objects.get(pk=self.kwargs["pk"])
        if user_obj.supplier is not None:
            raise ValidationError(
                "Невозможно удалить пользователя который зарегистрирован в сети за компанией !"
            )
        elif Product.objects.get(user=self.kwargs["pk"]) is not None:
            raise ValidationError(
                "Невозможно удалить пользователя который зарегистрирован в сети (модель проукты) за компанией !"
            )
        elif Supplier.objects.get(user=self.kwargs["pk"]) is not None:
            raise ValidationError(
                "Невозможно удалить пользователя который зарегистрирован в сети (модель поставщики) за компанией !"
            )
        return Users.objects.all()
    permission_classes = [IsSuperuser,]


class UserCreateAPIView(CreateAPIView):
    """В сети может зарегистироваться любой пользователь, но до проверки и утверждения данных суперпользователем
    он не является активным (is_active = False) и не имеет никаких прав кроме просмотра разрешенных данных.
    Сделать активным пользователя можно только если он дал разрешение на обработку персональных данных."""

    serializer_class = UserSerializer
    queryset = Users.objects.all()
    permission_classes = []

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        user.set_password(self.request.data.get("password"))
        if user.supplier is not None:
            supplier_object = Supplier.objects.get(pk=user.supplier_id)
            user.supplier_type = supplier_object.type
        if IsSuperuser().has_permission(self.request, self):
            user.is_active = True
        user.save()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
