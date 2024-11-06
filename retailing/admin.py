from django.contrib import admin

from retailing.models import Supplier, Payable


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "email",
        "user",
        "country",
        "city",
        "street",
        "house_number",
        "created_at"
    )
    list_filter = ('city',)


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = ("owner", "supplier", "amount", "created_at", "is_paid", "paid_date")
