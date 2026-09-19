<img width="1366" height="768" alt="ims" src="https://github.com/user-attachments/assets/505f338c-ddce-4d32-9a2c-3eb91fd2af50" />


# Inventory Management System

A web-based **Inventory Management System (IMS)** built with **Django** to help businesses efficiently manage products, inventory, suppliers, sales, stock movements, and reports from a centralized dashboard.

## 🚀 Features

* 📊 **Dashboard** — Overview of inventory and business statistics
* 📦 **Product Management** — Add, update, search, and manage products
* 🏷️ **Category Management** — Organize products by categories
* 🚚 **Supplier Management** — Manage supplier information
* 🛒 **Sales Management** — Create and manage sales orders
* 📈 **Stock Management** — Track stock levels and inventory changes
* 📋 **Stock History** — View detailed stock movement records
* ⚠️ **Low Stock & Out-of-Stock Reports** — Quickly identify products that need attention
* 📄 **PDF Reports** — Export inventory reports as PDF
* 🔐 **Authentication & Authorization** — Secure login and protected system pages
* 👥 **User & Role Management** — Control access based on user roles and permissions
* ⚙️ **Background Tasks** — Automated inventory checks using Celery and Redis
* 🔎 **Search & Filtering** — Easily find products and suppliers
* 📱 **Responsive Dashboard UI** — Clean and user-friendly interface

## 🛠️ Technologies Used

* **Backend:** Python, Django
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Task Queue:** Celery
* **Message Broker:** Redis
* **PDF Generation:** ReportLab
* **Version Control:** Git & GitHub

## 🎯 Project Objective

The goal of this project is to build a practical inventory management solution that demonstrates real-world **Django development**, including database design, authentication, CRUD operations, form validation, reporting, stock tracking, background task processing, and role-based access control.

## 📂 Main Modules

```text
Dashboard
│
├── Products
├── Categories
├── Suppliers
├── Sales
├── Stock Management
├── Stock History
├── Reports
├── Authentication
└── User & Role Management
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

## 🔄 Celery & Redis

The project uses **Celery with Redis** for background tasks.

Start Redis:

```bash
redis-server
```

Start the Celery worker:

```bash
celery -A config worker --loglevel=info
```

> Replace `config` with your Django project package name if it is different.

## 📌 Future Improvements

* Purchase Order Management
* Advanced analytics and charts
* Email notifications for low-stock products
* Barcode/QR code integration
* REST API
* Docker deployment
* Production deployment with Gunicorn and Nginx
* Cloud deployment on AWS

## 👨‍💻 Project Status

**Active Development**

This project is being developed as a practical Django application and continuously improved with new features, security enhancements, and better user experience.

## 📄 License

This project is intended for educational and portfolio purposes.
