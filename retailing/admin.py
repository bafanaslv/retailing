from datetime import date

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
    search_fields = ("name",)
    search_help_text = "Поиск по названию"


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = ("owner", "supplier", "amount", "created_at", "is_paid", "paid_date")

    actions = ["clear_payable"]

    def clear_payable(self, request, queryset):
        """Админ-действие для погашения задолженности на 0 для выбранных объектов.
        - queryset: набор объектов, к которым применяется действие.
        """
        queryset.update(amount=0, is_paid=True, paid_date=date.today)

    clear_payable.short_description = "Погасить задолженность перед поставщиком"
