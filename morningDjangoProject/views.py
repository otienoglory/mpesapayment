from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product

# Start mpesa related import

from django_daraja.mpesa import utils
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime

# End mpesa related import

# Start of Mpesa instances and variables
cl = MpesaClient()
stk_push_callback_url = "https://api.darajambili.com/express-payment"
b2c_callback = "https://api.darajambili.com/B2C/RESULT"


# End of Mpesa instances and variables

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect("register")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def add_product(request):
    if request.method == "POST":
        p_name = request.POST.get("jina")
        p_quantity = request.POST.get("kiasi")
        p_price = request.POST.get("bei")
        product = Product(prod_name=p_name, prod_quantity=p_quantity, prod_price=p_price)

        product.save()
        messages.success(request, 'Product saved successfully!')
        return redirect('add-product')
    return render(request, 'add-product.html')


@login_required()
def view_products(request):
    products = Product.objects.all()

    return render(request, 'products.html', {'products': products})


@login_required
def delete_product(request, id):
    # select the product you need to delete_product
    product = Product.objects.get(id=id)
    # Finally delete the product
    product.delete()
    # Redirect back to products page with a success message
    messages.success(request, 'Product deleted successfully')
    return redirect('products')


@login_required
def update_product(request, id):
    # select the products to be updated
    product = Product.objects.get(id=id)

    # check if the form has any submitted records to receive then
    if request.method == "POST":
        updated_name = request.POST.get('jina')
        updated_quantity = request.POST.get('kiasi')
        updated_price = request.POST.get('bei')

        # update the selected product above with a received data
        product.prod_name = updated_name
        product.prod_quantity = updated_quantity
        product.prod_price = updated_price

        # Return the updated data back to the database
        product.save()

        # Redirect back to the products page with a success message
        messages.success(request, 'product updated successfully')
        return redirect('products')
    return render(request, 'update-products.html', {'product': product})


def auth_success(request):
    token = cl.access_token()
    return JsonResponse(token, safe=False)


@login_required
def payment(request, id):
    # select the product being paid
    product = Product.objects.get(id=id)
    # check if the form has any submitted has post method
    if request.method == "POST":
        phone_number = request.POST.get('nambari')
        amount = request.POST.get('bei')
        amount = int(amount)
        # Proceed with the payment by launching mpesa STK
        account_ref = 'GA001'
        transaction_description = 'Payment for a product'
        stk = cl.stk_push(phone_number, amount, account_ref, transaction_description, stk_push_callback_url)
        return JsonResponse(stk.response_description, safe=False)
    return render(request, 'payment.html', {'product': product})
