from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

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


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"


    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     product = get_object_or_404(Product, pk=pk)
    #     context = {
    #         "product": product
    #     }
    #     return render(request, "shopapp/products-details.html", context=context)


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount"
    # form_class = GroupForm
    success_url = reverse_lazy("shopapp:products_list")

class ProductUpdateView(UpdateView):
    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("shopapp:products_list")

    def get_success(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context ["products"] = Product.objects.all()
    #     return context

# def products_list(request: HttpRequest):
#     context = {
#         "products": Product.objects.all(),
#     }
#     return render(request, 'shopapp/products-list.html', context=context)

# def orders_list(request: HttpRequest):
#     context = {
#         'orders': .all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self. get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)

class OrderDetailView(DetailView):
    queryset = (
        Order.objects.
        select_related('user').
        prefetch_related('products')
    )


class OrdersListView(ListView):
    template_name = 'shopapp/order_list.html'
    model = Product
    context_object_name = "products"