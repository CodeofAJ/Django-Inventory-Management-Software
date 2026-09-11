from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Products URLS / Router
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:id>/edit/", views.product_update, name="product_update"),
    path("products/<int:id>/delete/", views.product_delete, name="product_delete"),
    path("products/<int:id>/stock-in/", views.stock_in, name="stock_in"),
    path("products/<int:id>/stock-out/", views.stock_out, name="stock_out"),
    path("products/<int:id>/stock-history/", views.stock_history, name="stock_history"),
    # Category
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:id>/edit/", views.category_update, name="category_update"),
    path("categories/<int:id>/delete/", views.category_delete, name="category_delete"),
    # suppliers
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:id>/edit/", views.supplier_update, name="supplier_update"),
    path("suppliers/<int:id>/delete/", views.supplier_delete, name="supplier_delete"),
    # Purchase Order
    path("purchase-orders/", views.purchase_order_list, name="purchase_order_list"),
    path(
        "purchase-orders/add/",
        views.purchase_order_create,
        name="purchase_order_create",
    ),
    path(
        "purchase-orders/<int:id>/",
        views.purchase_order_detail,
        name="purchase_order_detail",
    ),
    path(
        "purchase-orders/<int:id>/add-item/",
        views.purchase_order_item_create,
        name="purchase_order_item_create",
    ),
    path(
        "purchase-orders/<int:id>/receive/",
        views.purchase_order_receive,
        name="purchase_order_receive",
    ),
    # Customers
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_create, name="customer_create"),
    path("customers/<int:id>/edit/", views.customer_update, name="customer_update"),
    path("customers/<int:id>/delete/", views.customer_delete, name="customer_delete"),
    # Sales
    path("sales-orders/", views.sales_order_list, name="sales_order_list"),
    path("sales-orders/add/", views.sales_order_create, name="sales_order_create"),
    path("sales-orders/<int:id>/", views.sales_order_detail, name="sales_order_detail"),
    path(
        "sales-orders/<int:id>/confirm/",
        views.sales_order_confirm,
        name="sales_order_confirm",
    ),
    path(
        "sales-orders/<int:id>/cancel/",
        views.sales_order_cancel,
        name="sales_order_cancel",
    ),
    # Stocks ===================
    path("stock-history/", views.stock_history, name="stock_history"),
    # REPORTS ======================
    path("reports/inventory/", views.inventory_report, name="inventory_report"),
    path(
        "reports/stock-movements/",
        views.stock_movement_report,
        name="stock_movement_report",
    ),
    path("reports/purchases/", views.purchase_report, name="purchase_report"),
    path("reports/sales/", views.sales_report, name="sales_report"),
    path("reports/low-stock/", views.low_stock_report, name="low_stock_report"),
    path(
        "reports/low-stock/export/",
        views.low_stock_report_csv,
        name="low_stock_report_csv",
    ),
    path(
        "reports/low-stock/pdf/",
        views.low_stock_report_pdf,
        name="low_stock_report_pdf",
    ),
    # LOGIN AND LOGOUT
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="inventory/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
