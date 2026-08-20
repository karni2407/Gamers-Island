from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

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