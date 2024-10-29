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
            "supplier_type"
        )


class UserSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("id", "username", "email")


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token
