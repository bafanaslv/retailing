# Описание представления не требует детелизации. Здесь все стандартно.

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from stripe.climate import Supplier
from users.models import Users
from users.permissions import IsActive, IsSuperuser
from users.serializer import UserSerializer, UserTokenObtainPairSerializer


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = Users.objects.all()
    permission_classes = [IsSuperuser,]


class UserRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if IsActive().has_permission(self.request, self):
            return Users.objects.all()
        else:
            lending_object_list = list(Users.objects.filter(pk=self.kwargs["pk"]))
            if len(lending_object_list) == 1:
                if self.kwargs["pk"] != self.request.user.id:
                    raise ValidationError(
                        "У вас недостаточно прав на просмотра учетных данных сотрудника !"
                    )
                return Users.objects.filter(pk=self.request.user.id)
            else:
                raise ValidationError(
                    "Такой сотрудник не зарегистрирован в торговой сети !"
                )
    permission_classes = [IsSuperuser, IsActive,]


class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        lending_object_list = list(Users.objects.filter(pk=self.kwargs["pk"]))
        if len(lending_object_list) == 1:
            if self.kwargs["pk"] != self.request.user.id:
                raise ValidationError(
                    "У вас недостаточно прав на изменение учетных данных сотрудника !"
                )
            return Users.objects.filter(pk=self.request.user.id)
        else:
            raise ValidationError("Такой сотрудник не зарегистрирован в торговой сети !")

    permission_classes = [IsSuperuser, IsActive,]

    def perform_update(self, serializer):
        user = serializer.save()
        user.set_password(self.request.data.get("password"))
        user.save()


class UserDestroyAPIView(DestroyAPIView):
    def get_queryset(self):
        lending_object_list = list(Supplier.objects.filter(user=self.request.user.id))
        if len(lending_object_list) > 0:
            raise ValidationError(
                "Невозможно удалить сотрудника, который является сотрудником торговой сети !"
            )
        else:
            lending_object_list = list(Users.objects.filter(pk=self.kwargs["pk"]))
            if len(lending_object_list) == 0:
                raise ValidationError(
                    "Такой сотрудник не зарегистрирован в торговой сети !"
                )
            return Users.objects.all()

    permission_classes = [IsSuperuser, IsActive,]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = Users.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(self.request.data.get("password"))
        user.save()


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
