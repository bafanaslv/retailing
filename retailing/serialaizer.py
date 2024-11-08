from rest_framework import serializers

from retailing.models import (Category, Country, Order, Payable, Product,
                              Supplier, Warehouse)


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
            "id",
            "name",
            "model",
            "category",
            "release_date",
        )


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            "owner",
            "supplier",
            "quantity",
        )


class OrderSerializerReadOnly(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "supplier",
            "product",
            "operation",
            "quantity",
            "price",
        )


class PayableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payable
        fields = "__all__"
