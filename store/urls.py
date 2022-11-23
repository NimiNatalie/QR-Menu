from django.urls import path
from django.conf.urls import include
from django.urls import re_path as url


from . import views

urlpatterns = [
    path("", views.restaurant, name="restaurant"),
    path("dashboard/", views.dasboard, name="dashboard"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("confirm_payment/", views.confirmPayment, name="confirm_payment"),
    path("process_order_mpesa/", views.mpesaPaymnet, name="process_mpesa"),
    path("login/", views._login, name="login"),
    path("auth/", views._loginEndPoint, name="auth"),
    path("logout/", views._logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("upd_personal_info/", views.updPersonalInfo, name="updPersonalInfo"),
    path("upd_email/", views.updEmail, name="updEmail"),
    path("register/", views.register, name="register"),
    path("save_user/", views._registerEndPoint, name="save_user"),
]