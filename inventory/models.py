from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_movements"
    )

    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)

    quantity = models.PositiveIntegerField()

    previous_quantity = models.PositiveIntegerField()

    new_quantity = models.PositiveIntegerField()

    reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"


class Supplier(models.Model):

    name = models.CharField(max_length=200)

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="purchase_orders"
    )

    order_number = models.CharField(max_length=50, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    order_date = models.DateField(auto_now_add=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number
    
    @property
    def total_amount(self):
        return sum(
            item.total_price
            for item in self.items.all()
        )


class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="purchase_order_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price



class Customer(models.Model):

    name = models.CharField(max_length=150)

    phone = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class SalesOrder(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(
        max_length=50,
        unique=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="sales_orders"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    order_date = models.DateTimeField(
        auto_now_add=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.order_number
    

class SalesOrderItem(models.Model):

    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_order_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return (
            f"{self.sales_order.order_number} - "
            f"{self.product.name}"
        )