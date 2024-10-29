from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "supplier",
            "supplier_type",
            "is_personal_data",
        )


class UserSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("id", "username", "email")


class UserSerializerForSuperuser(serializers.ModelSerializer):
    """Этот сериалайзер используется только активации нового пользователя суперпользователем если пользователь
    дал согласие на обработку персональных данных. Остальные поля суперпользователеь не имеет права менять."""

    class Meta:
        model = Users
        fields = ("is_active",)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token
