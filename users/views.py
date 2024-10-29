# Описание представления не требует детелизации. Здесь все стандартно.

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework_simplejwt.views import TokenObtainPairView

from retailing.models import Supplier, Product
from users.models import Users
from users.permissions import IsActive, IsSuperuser
from users.serializer import UserSerializer, UserTokenObtainPairSerializer, UserSerializerReadOnly


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
            if self.kwargs["pk"] != self.request.user.id:
                raise ValidationError(
                    "У вас недостаточно прав для просмотра учетных данных сотрудника !"
                )
            return Users.objects.filter(pk=self.request.user.id)
    permission_classes = [IsActive,]


class UserUpdateAPIView(UpdateAPIView):
    """Изменение аттрибутов пользователя, кроме принадлежности работодателю (supplier_id > 0), если он уже зарегистирован
    в торговой сети за определенной компанией. Можно отвязать (supplier_id = None), если это не нарушает целостность БД
    а затем заново привязать к другой компании."""

    serializer_class = UserSerializer
    queryset = Users.objects.all()

    def perform_update(self, serializer):
        user_obj = Users.objects.get(pk=self.kwargs["pk"])
        user = serializer.save()
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
    permission_classes = [IsSuperuser,]


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
    """При создании нового пользователя можно сразу указать где он работает (user.supplier) и автоматически присвоить
     тип компании (user.supplier_type)."""

    serializer_class = UserSerializer
    queryset = Users.objects.all()
    permission_classes = [IsSuperuser,]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(self.request.data.get("password"))
        if user.supplier is not None:
            supplier_object = Supplier.objects.get(pk=user.supplier_id)
            user.supplier_type = supplier_object.type
        user.save()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
