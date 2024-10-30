# Описание представления не требует детелизации. Здесь все стандартно.

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework_simplejwt.views import TokenObtainPairView

from retailing.models import Supplier, Product
from users.models import Users
from users.permissions import IsActive, IsSuperuser
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
            if len(dict(Users.objects.filter(pk=self.kwargs["pk"]))) == 0:
                raise ValidationError(
                    "Страница с таким id отсутствует !"
                )
            else:
                if self.kwargs["pk"] != self.request.user.id:
                    raise ValidationError(
                        "У вас недостаточно прав для просмотра учетных данных пользователя !"
                    )
            return Users.objects.filter(pk=self.request.user.id)
    permission_classes = [IsActive,]


class UserUpdateAPIView(UpdateAPIView):
    """Изменение аттрибутов пользователя, кроме принадлежности работодателю (supplier_id > 0), если он уже зарегистирован
    в торговой сети за определенной компанией. Можно отвязать (supplier_id = None), если это не нарушает целостность БД
    а затем заново привязать к другой компании."""

    def get_queryset(self):
        if IsSuperuser().has_permission(self.request, self):
            return Users.objects.all()
        else:
            if self.kwargs["pk"] != self.request.user.id:
                raise ValidationError(
                    "У вас недостаточно прав для изменения учетных данных пользователя !"
                )
            return Users.objects.filter(pk=self.request.user.id)

    def get_serializer_class(self):
        if IsSuperuser().has_permission(self.request, self):
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
                    "Невозможно изменить место работы у пользователя зарегистрированного в сети !"
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
                "Невозможно удалить пользователя который зарегистрирован в сети !"
            )
        elif Product.objects.get(user=self.kwargs["pk"]) is not None:
            raise ValidationError(
                "Невозможно удалить пользователя который зарегистрирован в сети (модель проукты) !"
            )
        elif Supplier.objects.get(user=self.kwargs["pk"]) is not None:
            raise ValidationError(
                "Невозможно удалить пользователя который зарегистрирован в сети (модель поставщики) !"
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
        user.save()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
