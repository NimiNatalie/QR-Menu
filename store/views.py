from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from .models import *
import json
import uuid
from .utils import *
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users, admin_only, unauthenticated_user
from django.core.paginator import Paginator
import requests
from django.contrib import messages








@login_required(login_url='login')
def restaurant(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems, "order": order, "group": group}
    return render(request, "restaurant/restaurant.html", context)


def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "restaurant/cart.html", context)


def checkout(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "restaurant/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add" or action == "buyNow":
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    orderItem.save()

    total = order.get_cart_items
    totalValue = float(orderItem.get_total)
    quantity = orderItem.quantity

    orderTotalValue = float(order.get_cart_total)

    if orderItem.quantity <= 0:
        orderItem.delete()
        totalValue = 0
        quantity = 0

    data = {
        "cartTotal": total,
        "productQuantity": quantity,
        "orderItemTotalValue": totalValue,
        "orderTotalValue": orderTotalValue,
    }

    return JsonResponse(
        data=data,
        safe=False,
    )


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        uname = data["form"]["username"]
        email = data["form"]["email"]
        password = data["form"]["password"]

        errors = []
        if User.objects.filter(username=uname).exists():
            errors.append("Username already exists.")
        if User.objects.filter(email=email).exists():
            errors.append("Email is already in use.")

        errCount = len(errors)

        if errCount > 0:
            return JsonResponse({"errors": errors}, safe=False,status=403)

        customer, order = guestOrder(request, data)

        if customer.user is not None:
            login(request, customer.user)
        else:
            print("is none")

    total = float(data["form"]["total"])

    if total != float(order.get_cart_total):
        err = {"err": "Your order total value does not match."}
        return JsonResponse({"errors": [err]}, safe=False, status=403)

    order.save()

    return JsonResponse({"id": order.id}, safe=False)


def confirmPayment(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        transaction_id = str(uuid.uuid4())
        order.transaction_id = transaction_id
        order.paypalTransactionId = data["paypalTxId"]
        order.complete = True

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data["shippingInfo"]["address"]["address_line_1"],
                city=data["shippingInfo"]["address"]["admin_area_2"],
                state=data["shippingInfo"]["address"]["admin_area_1"],
                zipcode=data["shippingInfo"]["address"]["postal_code"],
                countrycode=data["shippingInfo"]["address"]["country_code"],
            )
        order.save()

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)

def mpesaPaymnet(request):
    user = request.user
    amount = 1000
    phone_number = 254798556797
    try:
        mpesa = requests.post("http://127.0.0.1:8000/mpesa/submit/", data={"phone_number": phone_number,"amount": amount}) 
        messages.success(request, "Check Your Phone and Input your Mpesa PIN to make payment.")
        response = HttpResponseRedirect('checkout')
        response.delete_cookie("cart")
    except:
        messages.error("Something went wrong")
    
    context = {}
 
    return redirect('checkout')


def _logout(request):
    logout(request)
    return redirect("restaurant")

@unauthenticated_user
def _login(request):  # /login
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    if request.user.is_authenticated:
        return redirect("restaurant")
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "restaurant/login.html", context)


def _loginEndPoint(request):  # /auth
    data = json.loads(request.body)
    username = data["userFormData"]["username"]
    password = data["userFormData"]["password"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(status=209)
    else:
        return JsonResponse(
            {"errors": ["Your login credentials are incorrect."]}, status=403
        )

@unauthenticated_user
def register(request):  # /register
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    if request.user.is_authenticated:
        return redirect("restaurant")

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "restaurant/register.html", context)

def _registerEndPoint(request):  # /save_user
    data = json.loads(request.body)
    username = data["userFormData"]["username"]
    email = data["userFormData"]["email"]
    password = data["userFormData"]["password"]
    group = 'customer'
    

    errors = []
    if User.objects.filter(username=username).exists():
        errors.append("Username already exists.")
    if User.objects.filter(email=email).exists():
        errors.append("Email is already in use.")

    errCount = len(errors)

    if errCount > 0:
        return JsonResponse({"errors": errors}, status=403)

def profile(request):  # /profile
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    user = request.user

    context = {"items": items, "order": order, "cartItems": cartItems, "user": user}
    return render(request, "restaurant/profile.html", context)


def updPersonalInfo(request):
    data = json.loads(request.body)
    if request.user.is_authenticated:
        fName = data["fName"]
        lName = data["lName"]
        user = User.objects.get(username=request.user.username)
        user.first_name = fName
        user.last_name = lName
        user.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


def updEmail(request):
    data = json.loads(request.body)
    if request.user.is_authenticated:
        email = data["email"]
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
        user.email = email
        customer.email = email
        user.save()
        customer.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)
    
    
    
# Dashboard
@allowed_users(allowed_roles=['chef'])
def dasboard(request):
    orders = Order.objects.filter(date_ordered__gte=timezone.now().replace(hour=0, minute=0, second=0), date_ordered__lte=timezone.now().replace(hour=23, minute=59, second=59)).order_by('-date_ordered')
    customers = Customer.objects.all()

    total_orders = orders.count()
    total_customers = customers.count()
    orders_completed = orders.filter(complete='True').count()
    orders_pending = orders.filter(complete='False').count()
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)




    context = {'customers': customers, 'orders': orders, 'total_orders': total_orders,
               ' total_customers': total_customers, 'orders_completed': orders_completed,
               'orders_pending': orders_pending,'page_obj': page_obj,}
    return render(request, 'restaurant/dashboard.html', context)