from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
import re

from .models import Cart, CartItem, Product, Order, OrderItem


def products(request):

    product_list = Product.objects.all()

    paginator = Paginator(product_list, 8)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(request, "product.html", {"products": products})


def product_details(request, slug):

    product = get_object_or_404(Product, slug=slug)

    return render(request, "product_details.html", {"product": product})


@login_required
def add_to_cart(request, slug):

    product = get_object_or_404(Product, slug=slug)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, "cart.html", {"cart": cart})


@login_required
def remove_from_cart(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    CartItem.objects.filter(cart=cart, product=product).delete()

    return redirect("cart")


@login_required
def increase_quantity(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    cart_item.quantity += 1
    cart_item.save()

    return JsonResponse(
        {
            "quantity": cart_item.quantity,
            "item_total": cart_item.total_price,
            "cart_total": cart.total_price,
        }
    )


@login_required
def decrease_quantity(request, slug):

    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, slug=slug)

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

        return JsonResponse(
            {
                "quantity": cart_item.quantity,
                "item_total": cart_item.total_price,
                "cart_total": cart.total_price,
                "removed": False,
            }
        )

    cart_item.delete()

    return JsonResponse(
        {
            "quantity": 0,
            "item_total": 0,
            "cart_total": cart.total_price,
            "removed": True,
        }
    )


@login_required
def checkout(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    buy_now = request.GET.get("buy_now")

    # BUY NOW
    if buy_now:

        product = get_object_or_404(Product, slug=buy_now)

        checkout_items = [
            {"product": product, "quantity": 1, "total_price": product.price}
        ]

        total_price = product.price

    # CART CHECKOUT
    else:

        checkout_items = cart.items.all()

        total_price = cart.total_price

    # PURCHASE
    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()

        upi_id = request.POST.get("upi_id", "").strip()
        cardholder_name = request.POST.get("cardholder_name", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        expiry = request.POST.get("expiry", "").strip()
        cvv = request.POST.get("cvv", "").strip()
        bank = request.POST.get("bank", "").strip()

        error = None

        # CUSTOMER DETAILS
        if not name or not phone or not address or not payment_method:

            error = "Please fill in all required fields."

        elif not re.fullmatch(r"[A-Za-z ]{2,50}", name):

            error = "Please enter a valid name using only letters and spaces."

        elif not re.fullmatch(r"[6-9][0-9]{9}", phone):

            error = "Please enter a valid 10-digit Indian mobile number."

        elif len(address) < 10 or len(address) > 300:

            error = "Please enter a valid address between 10 and 300 characters."

        # UPI
        elif payment_method == "upi":

            if not re.fullmatch(r"[A-Za-z0-9._-]+@[A-Za-z0-9.-]+", upi_id):

                error = "Please enter a valid UPI ID."

        # DEBIT CARD / CREDIT CARD
        elif payment_method in ["debit_card", "credit_card"]:

            if not re.fullmatch(r"[A-Za-z ]{2,50}", cardholder_name):

                error = "Please enter a valid cardholder name."

            elif not re.fullmatch(r"[0-9]{16}", card_number):

                error = "Card number must contain exactly 16 digits."

            elif not re.fullmatch(r"(0[1-9]|1[0-2])/[0-9]{2}", expiry):

                error = "Expiry date must be in MM/YY format."

            elif not re.fullmatch(r"[0-9]{3}", cvv):

                error = "CVV must contain exactly 3 digits."

        # NET BANKING
        elif payment_method == "netbanking":

            if not bank:

                error = "Please select your bank."

        # INVALID PAYMENT METHOD
        elif payment_method != "cod":

            error = "Please select a valid payment method."

        if error:

            return render(
                request,
                "checkout.html",
                {
                    "cart": cart,
                    "checkout_items": checkout_items,
                    "total_price": total_price,
                    "error": error,
                },
            )

        # PAYMENT DETAILS ARE VALIDATED BUT NOT SAVED.
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_price=total_price,
            status="successful",
        )

        for item in checkout_items:

            if buy_now:

                product = item["product"]
                quantity = item["quantity"]
                price = item["product"].price

            else:

                product = item.product
                quantity = item.quantity
                price = item.product.price

            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=price
            )

        # Empty cart only when checking out the cart.
        # Buy Now does not affect the cart.
        if not buy_now:

            cart.items.all().delete()

        return redirect("order_success", order_id=order.id)

    return render(
        request,
        "checkout.html",
        {"cart": cart, "checkout_items": checkout_items, "total_price": total_price},
    )


@login_required
def order_success(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, "order_success.html", {"order": order})
