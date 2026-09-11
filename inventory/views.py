from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db import models, transaction
from django.db.models import Q, Sum, F, Count, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import (
    Product,
    Category,
    StockMovement,
    Supplier,
    PurchaseOrder,
    Customer,
    SalesOrder,
    SalesOrderItem,
)


from .forms import (
    ProductForm,
    CategoryForm,
    StockMovementForm,
    SupplierForm,
    PurchaseOrderForm,
    PurchaseOrderItemForm,
    CustomerForm,
    SalesOrderForm,
    SalesOrderItemFormSet,
)

from django.core.paginator import Paginator

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)




# =========================
# Dashboard
# =========================


@login_required
def dashboard(request):

    # -----------------------------------------
    # BASIC COUNTS
    # -----------------------------------------

    total_products = Product.objects.count()

    total_customers = Customer.objects.count()

    total_suppliers = Supplier.objects.count()

    low_stock_products = Product.objects.filter(quantity__lte=F("minimum_stock"))

    low_stock_count = low_stock_products.count()

    pending_sales = SalesOrder.objects.filter(status="PENDING").count()

    confirmed_sales = SalesOrder.objects.filter(status="CONFIRMED").count()

    # -----------------------------------------
    # TODAY'S SALES
    # -----------------------------------------

    today = timezone.localdate()

    todays_sales = (
        SalesOrder.objects.filter(status="CONFIRMED", order_date__date=today).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    # -----------------------------------------
    # RECENT SALES
    # -----------------------------------------

    recent_sales = SalesOrder.objects.select_related("customer").order_by(
        "-order_date"
    )[:5]

    # -----------------------------------------
    # RECENT STOCK MOVEMENTS
    # -----------------------------------------

    recent_movements = StockMovement.objects.select_related("product").order_by(
        "-created_at"
    )[:5]

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_suppliers": total_suppliers,
        "low_stock_count": low_stock_count,
        "low_stock_products": low_stock_products[:5],
        "pending_sales": pending_sales,
        "confirmed_sales": confirmed_sales,
        "todays_sales": todays_sales,
        "recent_sales": recent_sales,
        "recent_movements": recent_movements,
    }

    return render(request, "inventory/dashboard.html", context)


########################### ALL REPORTS ###############################

@login_required
def inventory_report(request):

    products = Product.objects.select_related("category").order_by("name")

    # Search
    search = request.GET.get("search", "")

    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))

    # Category filter
    category = request.GET.get("category", "")

    if category:
        products = products.filter(category_id=category)

    # Stock status filter
    stock_status = request.GET.get("stock_status", "")

    if stock_status == "low":

        products = products.filter(quantity__gt=0, quantity__lte=F("minimum_stock"))

    elif stock_status == "out":

        products = products.filter(quantity=0)

    elif stock_status == "normal":

        products = products.filter(quantity__gt=F("minimum_stock"))

    # Pagination
    paginator = Paginator(products, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all().order_by("name")

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "search": search,
        "selected_category": category,
        "stock_status": stock_status,
    }

    return render(request, "inventory/inventory_report.html", context)



@login_required
def stock_movement_report(request):

    movements = StockMovement.objects.select_related("product").order_by("-created_at")

    # Search
    search = request.GET.get("search", "")

    if search:
        movements = movements.filter(
            Q(product__name__icontains=search) | Q(product__sku__icontains=search)
        )

    # Movement type
    movement_type = request.GET.get("movement_type", "")

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # Date filters
    date_from = request.GET.get("date_from", "")

    date_to = request.GET.get("date_to", "")

    if date_from:
        movements = movements.filter(created_at__date__gte=date_from)

    if date_to:
        movements = movements.filter(created_at__date__lte=date_to)

    # Pagination
    paginator = Paginator(movements, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "movement_type": movement_type,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "inventory/stock_movement_report.html", context)


@login_required
def purchase_report(request):

    orders = (
        PurchaseOrder.objects.select_related("supplier")
        .prefetch_related("items")
        .order_by("-order_date", "-created_at")
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get("search", "")

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) | Q(supplier__name__icontains=search)
        )

    # -------------------------
    # Status filter
    # -------------------------

    status = request.GET.get("status", "")

    if status:
        orders = orders.filter(status=status)

    # -------------------------
    # Date filters
    # -------------------------

    date_from = request.GET.get("date_from", "")

    date_to = request.GET.get("date_to", "")

    if date_from:
        orders = orders.filter(order_date__gte=date_from)

    if date_to:
        orders = orders.filter(order_date__lte=date_to)

    # -------------------------
    # Statistics
    # -------------------------

    total_orders = orders.count()

    pending_orders = orders.filter(status="PENDING").count()

    received_orders = orders.filter(status="RECEIVED").count()

    cancelled_orders = orders.filter(status="CANCELLED").count()

    # -------------------------
    # Total purchase value
    # -------------------------

    total_purchase_value = 0

    for order in orders:

        for item in order.items.all():

            total_purchase_value += item.quantity * item.unit_price

    # -------------------------
    # Pagination
    # -------------------------

    paginator = Paginator(orders, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "received_orders": received_orders,
        "cancelled_orders": cancelled_orders,
        "total_purchase_value": total_purchase_value,
    }

    return render(request, "inventory/purchase_report.html", context)


def sales_report(request):

    orders = SalesOrder.objects.select_related(
        "customer"
    ).order_by(
        "-order_date"
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get(
        "search",
        ""
    )

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search)
            | Q(customer__name__icontains=search)
        )

    # -------------------------
    # Status filter
    # -------------------------

    status = request.GET.get(
        "status",
        ""
    )

    if status:
        orders = orders.filter(
            status=status
        )

    # -------------------------
    # Date filters
    # -------------------------

    date_from = request.GET.get(
        "date_from",
        ""
    )

    date_to = request.GET.get(
        "date_to",
        ""
    )

    if date_from:
        orders = orders.filter(
            order_date__date__gte=date_from
        )

    if date_to:
        orders = orders.filter(
            order_date__date__lte=date_to
        )

    # -------------------------
    # Statistics
    # -------------------------

    total_orders = orders.count()

    pending_orders = orders.filter(
        status="PENDING"
    ).count()

    confirmed_orders = orders.filter(
        status="CONFIRMED"
    ).count()

    cancelled_orders = orders.filter(
        status="CANCELLED"
    ).count()

    total_sales_value = orders.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # -------------------------
    # Pagination
    # -------------------------

    paginator = Paginator(
        orders,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "page_obj": page_obj,

        "search": search,

        "status": status,

        "date_from": date_from,

        "date_to": date_to,

        "total_orders": total_orders,

        "pending_orders": pending_orders,

        "confirmed_orders": confirmed_orders,

        "cancelled_orders": cancelled_orders,

        "total_sales_value": total_sales_value,
    }

    return render(
        request,
        "inventory/sales_report.html",
        context
    )


def low_stock_report(request):

    products = Product.objects.select_related(
        "category"
    ).order_by(
        "quantity"
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get(
        "search",
        ""
    )

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(sku__icontains=search)
        )

    # -------------------------
    # Stock status filter
    # -------------------------

    stock_status = request.GET.get(
        "stock_status",
        ""
    )

    if stock_status == "OUT":

        products = products.filter(
            quantity=0
        )

    elif stock_status == "LOW":

        products = products.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock")
        )

    elif stock_status == "NORMAL":

        products = products.filter(
            quantity__gt=F("minimum_stock")
        )

    else:

        # Default:
        # Show only low-stock and out-of-stock products

        products = products.filter(
            quantity__lte=F("minimum_stock")
        )

    # -------------------------
    # Statistics
    # -------------------------

    total_products = Product.objects.count()

    out_of_stock = Product.objects.filter(
        quantity=0
    ).count()

    low_stock = Product.objects.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock")
    ).count()

    normal_stock = Product.objects.filter(
        quantity__gt=F("minimum_stock")
    ).count()

    # -------------------------
    # Pagination
    # -------------------------

    paginator = Paginator(
        products,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "page_obj": page_obj,

        "search": search,

        "stock_status": stock_status,

        "total_products": total_products,

        "out_of_stock": out_of_stock,

        "low_stock": low_stock,

        "normal_stock": normal_stock,

    }

    return render(
        request,
        "inventory/low_stock_report.html",
        context
    )


import csv
@login_required
def low_stock_report_csv(request):

    products = Product.objects.select_related(
        "category"
    ).order_by(
        "quantity"
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get(
        "search",
        ""
    )

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(sku__icontains=search)
        )

    # -------------------------
    # Stock status filter
    # -------------------------

    stock_status = request.GET.get(
        "stock_status",
        ""
    )

    if stock_status == "OUT":

        products = products.filter(
            quantity=0
        )

    elif stock_status == "LOW":

        products = products.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock")
        )

    elif stock_status == "NORMAL":

        products = products.filter(
            quantity__gt=F("minimum_stock")
        )

    else:

        products = products.filter(
            quantity__lte=F("minimum_stock")
        )

    # -------------------------
    # Create CSV response
    # -------------------------

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="low_stock_report.csv"'
    )

    writer = csv.writer(response)

    # -------------------------
    # CSV Header
    # -------------------------

    writer.writerow([
        "Product",
        "SKU",
        "Category",
        "Current Stock",
        "Minimum Stock",
        "Status",
    ])

    # -------------------------
    # CSV Data
    # -------------------------

    for product in products:

        if product.quantity == 0:

            status = "Out of Stock"

        elif product.quantity <= product.minimum_stock:

            status = "Low Stock"

        else:

            status = "Normal"

        writer.writerow([
            product.name,
            product.sku,
            product.category.name,
            product.quantity,
            product.minimum_stock,
            status,
        ])

    return response
       

##### PDF ====================================== 
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)



def low_stock_report_pdf(request):

    products = Product.objects.select_related(
        "category"
    ).order_by(
        "quantity"
    )

    # -------------------------
    # Search
    # -------------------------

    search = request.GET.get(
        "search",
        ""
    )

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(sku__icontains=search)
        )

    # -------------------------
    # Stock status filter
    # -------------------------

    stock_status = request.GET.get(
        "stock_status",
        ""
    )

    if stock_status == "OUT":

        products = products.filter(
            quantity=0
        )

    elif stock_status == "LOW":

        products = products.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock")
        )

    elif stock_status == "NORMAL":

        products = products.filter(
            quantity__gt=F("minimum_stock")
        )

    else:

        products = products.filter(
            quantity__lte=F("minimum_stock")
        )

    # -------------------------
    # HTTP response
    # -------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="low_stock_report.pdf"'
    )

    # -------------------------
    # PDF document
    # -------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    elements = []

    # -------------------------
    # Title
    # -------------------------

    title = Paragraph(
        "Low Stock Report",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 10)
    )

    # -------------------------
    # Report information
    # -------------------------

    if search:

        elements.append(
            Paragraph(
                f"Search: {search}",
                styles["Normal"]
            )
        )

    if stock_status:

        elements.append(
            Paragraph(
                f"Filter: {stock_status}",
                styles["Normal"]
            )
        )

    elements.append(
        Spacer(1, 10)
    )

    # -------------------------
    # Table data
    # -------------------------

    data = [
        [
            "Product",
            "SKU",
            "Category",
            "Current",
            "Minimum",
            "Status",
        ]
    ]

    for product in products:

        if product.quantity == 0:

            status = "Out of Stock"

        elif product.quantity <= product.minimum_stock:

            status = "Low Stock"

        else:

            status = "Normal"

        data.append(
            [
                product.name,
                product.sku,
                product.category.name,
                str(product.quantity),
                str(product.minimum_stock),
                status,
            ]
        )

    # -------------------------
    # Create table
    # -------------------------

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            38 * mm,
            25 * mm,
            35 * mm,
            22 * mm,
            22 * mm,
            30 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#343a40"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "ALIGN",
                    (3, 1),
                    (4, -1),
                    "CENTER",
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(table)

    # -------------------------
    # Build PDF
    # -------------------------

    document.build(elements)

    return response

########################### END OF REPORTS ###############################


# =========================
# Products
# =========================

from django.core.paginator import Paginator

@login_required
def product_list(request):

    products = Product.objects.select_related("category").all()

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        products = products.filter(
            models.Q(name__icontains=search) | models.Q(sku__icontains=search)
        )

    # Category filter
    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(category_id=category_id)

    # Low-stock filter
    low_stock = request.GET.get("low_stock")

    if low_stock == "1":
        products = products.filter(quantity__lte=models.F("minimum_stock"))

    # Pagination
    paginator = Paginator(products, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "search": search,
        "selected_category": category_id,
        "low_stock": low_stock,
    }

    return render(request, "inventory/product_list.html", context)


# def product_create(request):
#     categories = Category.objects.all()

#     if request.method == "POST":
#         name = request.POST.get("name")
#         category_id = request.POST.get("category")
#         sku = request.POST.get("sku")
#         price = request.POST.get("price")
#         quantity = request.POST.get("quantity")
#         minimum_stock = request.POST.get("minimum_stock")
#         description = request.POST.get("description")

#         Product.objects.create(
#             name=name,
#             category_id=category_id,
#             sku=sku,
#             price=price,
#             quantity=quantity,
#             minimum_stock=minimum_stock,
#             description=description,
#         )

#         return redirect("product_list")

#     return render(
#         request,
#         "inventory/product_form.html",
#         {"categories": categories}
#     )


def product_create(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("product_list")

    else:

        form = ProductForm()

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "title": "Add Product",
        },
    )


# def product_update(request, id):
#     product = get_object_or_404(Product, id=id)
#     categories = Category.objects.all()

#     if request.method == "POST":
#         product.name = request.POST.get("name")
#         product.category_id = request.POST.get("category")
#         product.sku = request.POST.get("sku")
#         product.price = request.POST.get("price")
#         product.quantity = request.POST.get("quantity")
#         product.minimum_stock = request.POST.get("minimum_stock")
#         product.description = request.POST.get("description")

#         product.save()

#         return redirect("product_list")

#     spell = {
#         "product": product,
#         "categories": categories,
#     }

#     return render(request, "inventory/product_form.html", spell)


def product_update(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)

        if form.is_valid():

            form.save()

            return redirect("product_list")

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "product": product,
            "title": "Edit Product",
        },
    )


def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(
        request, "inventory/product_list.html", {"products": Product.objects.all()}
    )



# =========================
# Categories
# =========================

@login_required
def category_list(request):
    categories = Category.objects.all()

    return render(request, "inventory/category_list.html", {"categories": categories})


def category_create(request):

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("category_list")

    else:
        form = CategoryForm()

    return render(request, "inventory/category_form.html", {"form": form})


def category_update(request, id):

    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect("category_list")

    else:
        form = CategoryForm(instance=category)

    return render(request, "inventory/category_form.html", {"form": form})


def category_delete(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.delete()
        return redirect("category_list")

    return redirect("category_list")


# Create your views here.


def stock_in(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        form = StockMovementForm(request.POST)

        if form.is_valid():

            quantity = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]

            with transaction.atomic():

                previous_quantity = product.quantity
                new_quantity = previous_quantity + quantity

                product.quantity = new_quantity
                product.save()

                StockMovement.objects.create(
                    product=product,
                    movement_type="IN",
                    quantity=quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    reason=reason,
                )

            return redirect("product_list")

    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/stock_form.html",
        {
            "form": form,
            "product": product,
            "movement_type": "Stock In",
        },
    )


def stock_out(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        form = StockMovementForm(request.POST)

        if form.is_valid():

            quantity = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]

            if quantity > product.quantity:

                form.add_error("quantity", "Not enough stock available.")

            else:

                with transaction.atomic():

                    previous_quantity = product.quantity
                    new_quantity = previous_quantity - quantity

                    product.quantity = new_quantity
                    product.save()

                    StockMovement.objects.create(
                        product=product,
                        movement_type="OUT",
                        quantity=quantity,
                        previous_quantity=previous_quantity,
                        new_quantity=new_quantity,
                        reason=reason,
                    )

                return redirect("product_list")

    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/stock_form.html",
        {
            "form": form,
            "product": product,
            "movement_type": "Stock Out",
        },
    )


################### Suppliers : ##################
@login_required
def supplier_list(request):

    suppliers = Supplier.objects.all().order_by("-created_at")

    # print("SUPPLIER COUNT:", suppliers.count())
    # print("SUPPLIERS:", list(suppliers))

    search = request.GET.get("search", "")

    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search)
            | Q(contact_person__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )

    paginator = Paginator(suppliers, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "inventory/supplier_list.html", context)


def supplier_create(request):

    if request.method == "POST":

        form = SupplierForm(request.POST)

        if form.is_valid():

            supplier = form.save()

            messages.success(
                request, f"Supplier '{supplier.name}' created successfully."
            )

            return redirect("supplier_list")

    else:

        form = SupplierForm()

    return render(
        request,
        "inventory/supplier_form.html",
        {
            "form": form,
            "title": "Add Supplier",
        },
    )


def supplier_update(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    if request.method == "POST":

        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():

            supplier = form.save()

            messages.success(
                request, f"Supplier '{supplier.name}' updated successfully."
            )

            return redirect("supplier_list")

    else:

        form = SupplierForm(instance=supplier)

    return render(
        request,
        "inventory/supplier_form.html",
        {
            "form": form,
            "title": "Edit Supplier",
            "supplier": supplier,
        },
    )


def supplier_delete(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    if request.method == "POST":

        name = supplier.name

        supplier.delete()

        messages.success(request, f"Supplier '{name}' deleted successfully.")

    return redirect("supplier_list")


################ Purhase Details  ###################


from .forms import PurchaseOrderItemForm

@login_required
def purchase_order_list(request):

    purchase_orders = (
        PurchaseOrder.objects.select_related("supplier").all().order_by("-created_at")
    )

    return render(
        request,
        "inventory/purchase_order_list.html",
        {
            "purchase_orders": purchase_orders,
        },
    )


def purchase_order_create(request):

    if request.method == "POST":

        form = PurchaseOrderForm(request.POST)

        if form.is_valid():

            purchase_order = form.save()

            return redirect("purchase_order_detail", purchase_order.id)

    else:

        form = PurchaseOrderForm()

    return render(
        request,
        "inventory/purchase_order_form.html",
        {
            "form": form,
        },
    )


def purchase_order_detail(request, id):

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier"), id=id
    )

    items = purchase_order.items.select_related("product").all()

    total = sum(item.total_price for item in items)

    return render(
        request,
        "inventory/purchase_order_detail.html",
        {
            "purchase_order": purchase_order,
            "items": items,
            "total": total,
        },
    )


def purchase_order_item_create(request, id):

    purchase_order = get_object_or_404(PurchaseOrder, id=id)

    if purchase_order.status != "PENDING":

        return redirect("purchase_order_detail", purchase_order.id)

    if request.method == "POST":

        form = PurchaseOrderItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)

            item.purchase_order = purchase_order

            item.save()

            return redirect("purchase_order_detail", purchase_order.id)

    else:

        form = PurchaseOrderItemForm()

    return render(
        request,
        "inventory/purchase_order_item_form.html",
        {
            "form": form,
            "purchase_order": purchase_order,
        },
    )


def purchase_order_receive(request, id):

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.prefetch_related("items__product"), id=id
    )

    if purchase_order.status != "PENDING":
        return redirect("purchase_order_detail", purchase_order.id)

    if request.method == "POST":

        with transaction.atomic():

            for item in purchase_order.items.all():

                product = item.product

                previous_quantity = product.quantity
                new_quantity = previous_quantity + item.quantity

                product.quantity = new_quantity
                product.save(update_fields=["quantity"])

                StockMovement.objects.create(
                    product=product,
                    movement_type="IN",
                    quantity=item.quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    reason=(f"Purchase Order " f"{purchase_order.order_number}"),
                )

            purchase_order.status = "RECEIVED"

            purchase_order.save(update_fields=["status"])

        return redirect("purchase_order_detail", purchase_order.id)

    return render(
        request,
        "inventory/purchase_order_receive.html",
        {
            "purchase_order": purchase_order,
        },
    )


# def supplier_update(request, id):

#     supplier = get_object_or_404(Supplier, id=id)

#     if request.method == "POST":

#         form = SupplierForm(request.POST, instance=supplier)

#         if form.is_valid():
#             form.save()

#             return redirect("supplier_list")

#     else:
#         form = SupplierForm(instance=supplier)

#     return render(
#         request,
#         "inventory/supplier_form.html",
#         {
#             "form": form,
#             "supplier": supplier,
#             "title": "Edit Supplier",
#         },
#     )


# def supplier_delete(request, id):

#     supplier = get_object_or_404(Supplier, id=id)

#     if request.method == "POST":

#         supplier.delete()

#         return redirect("supplier_list")

#     return render(
#         request,
#         "inventory/supplier_confirm_delete.html",
#         {
#             "supplier": supplier,
#         },
#     )


# def supplier_list(request):

#     search = request.GET.get("search", "").strip()

#     suppliers = Supplier.objects.all()

#     if search:

#         suppliers = suppliers.filter(
#             models.Q(name__icontains=search)
#             | models.Q(contact_person__icontains=search)
#             | models.Q(phone__icontains=search)
#             | models.Q(email__icontains=search)
#         )

#     suppliers = suppliers.order_by("name")

#     return render(
#         request,
#         "inventory/supplier_list.html",
#         {
#             "suppliers": suppliers,
#             "search": search,
#         },
#     )


# def supplier_detail(request, id):

#     supplier = get_object_or_404(Supplier, id=id)

#     purchase_orders = supplier.purchase_orders.select_related("supplier").order_by(
#         "-created_at"
#     )

#     return render(
#         request,
#         "inventory/supplier_detail.html",
#         {
#             "supplier": supplier,
#             "purchase_orders": purchase_orders,
#         },
#     )



#########################  CUSTOMERS ############################

@login_required
def customer_list(request):

    search = request.GET.get("search", "").strip()

    customers = Customer.objects.all()

    if search:

        customers = customers.filter(
            models.Q(name__icontains=search)
            | models.Q(phone__icontains=search)
            | models.Q(email__icontains=search)
        )

    customers = customers.order_by("name")

    return render(
        request,
        "inventory/customer_list.html",
        {
            "customers": customers,
            "search": search,
        },
    )


def customer_create(request):

    if request.method == "POST":

        form = CustomerForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("customer_list")

    else:

        form = CustomerForm()

    return render(
        request,
        "inventory/customer_form.html",
        {
            "form": form,
            "title": "Add Customer",
        },
    )


def customer_update(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":

        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():

            form.save()

            return redirect("customer_list")

    else:

        form = CustomerForm(instance=customer)

    return render(
        request,
        "inventory/customer_form.html",
        {
            "form": form,
            "customer": customer,
            "title": "Edit Customer",
        },
    )


def customer_delete(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":

        customer.delete()

        return redirect("customer_list")

    return render(
        request,
        "inventory/customer_confirm_delete.html",
        {
            "customer": customer,
        },
    )


# Sales orders


def sales_order_list(request):

    search = request.GET.get("search", "").strip()

    orders = SalesOrder.objects.select_related("customer").order_by("-order_date")

    if search:

        orders = orders.filter(
            models.Q(order_number__icontains=search)
            | models.Q(customer__name__icontains=search)
        )

    return render(
        request,
        "inventory/sales_order_list.html",
        {
            "orders": orders,
            "search": search,
        },
    )


def sales_order_create(request):

    if request.method == "POST":

        order_form = SalesOrderForm(request.POST)

        if order_form.is_valid():

            sales_order = order_form.save(commit=False)

            item_formset = SalesOrderItemFormSet(request.POST, instance=sales_order)

            if item_formset.is_valid():

                items = item_formset.save(commit=False)

                if not items:
                    order_form.add_error(None, "Add at least one product.")

                else:

                    total_amount = 0

                    for item in items:

                        item.unit_price = item.product.price

                        item.subtotal = item.unit_price * item.quantity

                        total_amount += item.subtotal

                    sales_order.order_number = (
                        f"SO-{SalesOrder.objects.count() + 1:04d}"
                    )

                    sales_order.total_amount = total_amount

                    sales_order.status = "PENDING"

                    sales_order.save()

                    for item in items:
                        item.sales_order = sales_order
                        item.save()

                    return redirect("sales_order_list")

    else:

        order_form = SalesOrderForm()

        item_formset = SalesOrderItemFormSet()

    return render(
        request,
        "inventory/sales_order_form.html",
        {
            "order_form": order_form,
            "item_formset": item_formset,
        },
    )


def sales_order_detail(request, id):

    sales_order = get_object_or_404(
        SalesOrder.objects.select_related("customer"), id=id
    )

    items = sales_order.items.select_related("product").all()

    return render(
        request,
        "inventory/sales_order_detail.html",
        {
            "sales_order": sales_order,
            "items": items,
        },
    )


@transaction.atomic
def sales_order_confirm(request, id):

    if request.method != "POST":
        return redirect("sales_order_detail", id=id)

    sales_order = get_object_or_404(SalesOrder.objects.select_for_update(), id=id)

    # Don't allow an already confirmed/cancelled
    # order to be processed again.

    if sales_order.status != "PENDING":

        return redirect("sales_order_detail", id=id)

    items = (
        SalesOrderItem.objects.select_related("product")
        .select_for_update()
        .filter(sales_order=sales_order)
    )

    # Check stock first

    for item in items:

        if item.quantity > item.product.quantity:

            messages.error(
                request,
                (
                    f"Not enough stock for "
                    f"{item.product.name}. "
                    f"Available: "
                    f"{item.product.quantity}, "
                    f"Requested: {item.quantity}."
                ),
            )

            return redirect("sales_order_detail", id=id)

    # Stock is available.
    # Now deduct it.

    for item in items:

        product = item.product

        previous_quantity = product.quantity

        new_quantity = previous_quantity - item.quantity

        product.quantity = new_quantity

        product.save(update_fields=["quantity"])

        StockMovement.objects.create(
            product=product,
            movement_type="OUT",
            quantity=item.quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason="Sale",
        )

    sales_order.status = "CONFIRMED"

    sales_order.save(update_fields=["status"])

    messages.success(
        request, (f"Sale {sales_order.order_number} " f"confirmed successfully.")
    )

    return redirect("sales_order_detail", id=id)


@login_required
@transaction.atomic
def sales_order_cancel(request, id):

    if request.method != "POST":
        return redirect("sales_order_detail", id=id)

    sales_order = get_object_or_404(SalesOrder.objects.select_for_update(), id=id)

    # Only pending orders can be cancelled.

    if sales_order.status != "PENDING":

        messages.error(
            request,
            (
                f"Sale {sales_order.order_number} "
                f"cannot be cancelled because it is "
                f"already {sales_order.get_status_display()}."
            ),
        )

        return redirect("sales_order_detail", id=id)

    sales_order.status = "CANCELLED"

    sales_order.save(update_fields=["status"])

    messages.success(
        request, (f"Sale {sales_order.order_number} " f"cancelled successfully.")
    )

    return redirect("sales_order_detail", id=id)


def stock_history(request):

    movements = StockMovement.objects.select_related("product").order_by("-created_at")

    # -----------------------------
    # SEARCH
    # -----------------------------

    search = request.GET.get("search", "")

    if search:
        movements = movements.filter(product__name__icontains=search)

    # -----------------------------
    # MOVEMENT TYPE
    # -----------------------------

    movement_type = request.GET.get("movement_type", "")

    if movement_type in ["IN", "OUT"]:

        movements = movements.filter(movement_type=movement_type)

    # -----------------------------
    # DATE FILTER
    # -----------------------------

    date_from = request.GET.get("date_from", "")

    date_to = request.GET.get("date_to", "")

    if date_from:

        movements = movements.filter(created_at__date__gte=date_from)

    if date_to:

        movements = movements.filter(created_at__date__lte=date_to)

    # -----------------------------
    # PAGINATION
    # -----------------------------

    paginator = Paginator(movements, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    # -----------------------------
    # CONTEXT
    # -----------------------------

    context = {
        "page_obj": page_obj,
        "search": search,
        "movement_type": movement_type,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "inventory/stock_history.html", context)
