from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import GroupForm
from .models import Product, Order


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)


    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form .is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(View):
    def get(self, request: HttpRequest, pk:int) -> HttpResponse:
        product = get_object_or_404(Product, pk=pk)
        context = {
            "product": product
        }
        return render(request, "shopapp/prosducts-details.html", context=context)


def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)

def orders_list(request: HttpRequest):
    context = {
        'orders': Order.objects.select_related('user').prefetch_related('products').all(),
    }
    return render(request, 'shopapp/orders-list.html', context=context)
