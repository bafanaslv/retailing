from rest_framework import serializers
from retailing.models import Supplier, Category


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            "id",
            "username",
            "email",
            "phone",
            "is_personal_data",
            "tg_chat_id",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"