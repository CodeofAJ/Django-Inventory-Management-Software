from celery import shared_task
from django.db.models import F

from .models import Product


@shared_task
def check_low_stock_products():
    low_stock_products = Product.objects.filter(
        quantity__lte=F("minimum_stock")
    )

    print("========== LOW STOCK CHECK ==========")

    if not low_stock_products.exists():
        print("No low-stock products found.")
        return "No low-stock products found."

    for product in low_stock_products:
        print(
            f"LOW STOCK: {product.name} | "
            f"Current Stock: {product.quantity} | "
            f"Minimum Stock: {product.minimum_stock}"
        )

    print("=====================================")

    return f"Found {low_stock_products.count()} low-stock product(s)."