from rest_framework import serializers
from retailing.models import Supplier, Category, Country, Product


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            "id",
            "name",
            "type",
            "email",
            "country",
            "user",
            "city",
            "street",
            "house_number",
        )


class SupplierSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name",
            "model",
            "category",
            "release_date",
        )

