from django.urls import path
from . import views

urlpatterns = [
    path("", views.products, name="products"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<slug:slug>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/increase/<slug:slug>/", views.increase_quantity, name="increase_quantity"),
    path("cart/decrease/<slug:slug>/", views.decrease_quantity, name="decrease_quantity"),
    path("<slug:slug>/", views.product_details, name="product_details"),    
]
