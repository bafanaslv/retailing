from rest_framework import serializers
from retailing.models import Supplier, Category, Country


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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"