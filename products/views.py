from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse

from .models import Cart, CartItem, Product
from .models import Product


def products(request):

    product_list = Product.objects.all()

    paginator = Paginator(product_list, 8)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(request, "product.html", {
        "products": products
    })


def product_details(request, slug):

    product = get_object_or_404(Product, slug=slug)

    return render(request, "product_details.html", {
        "product": product
    })


@login_required
def add_to_cart(request, slug):

    product = get_object_or_404(Product, slug=slug)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, "cart.html", {
        "cart": cart
    })


@login_required
def remove_from_cart(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    CartItem.objects.filter(
        cart=cart,
        product=product
    ).delete()

    return redirect("cart")


@login_required
def increase_quantity(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product=product
    )

    cart_item.quantity += 1
    cart_item.save()

    return JsonResponse({
        "quantity": cart_item.quantity,
        "item_total": cart_item.total_price,
        "cart_total": cart.total_price
    })


@login_required
def decrease_quantity(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product=product
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

        return JsonResponse({
            "quantity": cart_item.quantity,
            "item_total": cart_item.total_price,
            "cart_total": cart.total_price,
            "removed": False
        })

    cart_item.delete()

    return JsonResponse({
        "quantity": 0,
        "item_total": 0,
        "cart_total": cart.total_price,
        "removed": True
    })