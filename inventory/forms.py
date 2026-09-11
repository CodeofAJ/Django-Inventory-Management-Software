from django import forms
from django.forms import inlineformset_factory
from .models import (
    Product,
    Category,
    Supplier,
    StockMovement,
    PurchaseOrder,
    PurchaseOrderItem,
    Customer,
    SalesOrderItem,
    SalesOrder,
)


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", "description"]



class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "sku",
            "price",
            "quantity",
            "minimum_stock",
            "description",
        ]

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")

        return price



class StockMovementForm(forms.Form):

    quantity = forms.IntegerField(min_value=1, label="Quantity")

    reason = forms.CharField(max_length=255, required=False)




class SupplierForm(forms.ModelForm):

    class Meta:

        model = Supplier

        fields = [
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "placeholder": "Supplier name"
                }
            ),

            "contact_person": forms.TextInput(
                attrs={
                    "placeholder": "Contact person"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "placeholder": "Supplier address",
                    "rows": 4
                }
            ),
        }   

        

class PurchaseOrderForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrder

        fields = [
            "supplier",
            "order_number",
            "notes",
        ]


class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderItem

        fields = [
            "product",
            "quantity",
            "unit_price",
        ]


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "name",
            "phone",
            "email",
            "address",
        ]


class SalesOrderForm(forms.ModelForm):

    class Meta:
        model = SalesOrder
        fields = [
            "customer",
        ]
 


class SalesOrderItemForm(forms.ModelForm):

    class Meta:
        model = SalesOrderItem
        fields = [
            "product",
            "quantity",
        ]

    def clean_quantity(self):

        quantity = self.cleaned_data.get("quantity")

        if quantity is None:
            return quantity

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")

        return quantity
         
   

# PASTE IT HERE
SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder,
    SalesOrderItem,
    form=SalesOrderItemForm,
    extra=1,
    can_delete=True,
)



#####   bending  work !!!   IN chatgpt. my work starts from =
#
#
#    .................   "No error, Go to next step" ....................
