from django.contrib import admin
from .models import (
    Category,
    Product,
    StockMovement,
    Supplier,
    PurchaseOrderItem,
    PurchaseOrder,
    Customer,
    SalesOrder,
    SalesOrderItem,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "quantity",
        "minimum_stock",
    )

    list_filter = ("category",)
    search_fields = ("name", "sku")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "movement_type",
        "quantity",
        "previous_quantity",
        "new_quantity",
        "reason",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "reason",
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "created_at",
    )

    search_fields = (
        "name",
        "contact_person",
        "phone",
        "email",
    )


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "supplier",
        "status",
        "order_date",
        "created_at",
    )

    list_filter = (
        "status",
        "order_date",
    )

    search_fields = (
        "order_number",
        "supplier__name",
    )


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "purchase_order",
        "product",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "purchase_order__order_number",
        "product__name",
        "product__sku",
    )



@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "customer",
        "status",
        "total_amount",
        "order_date",
    )

    list_filter = (
        "status",
        "order_date",
    )

    search_fields = (
        "order_number",
        "customer__name",
    )


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "sales_order",
        "product",
        "quantity",
        "unit_price",
        "subtotal",
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "email",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
    )    