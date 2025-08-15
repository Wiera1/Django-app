"""
В этом модуле лежат различные наборы представлений.

Разные view для интернет-магазина: по товарам, заказам и т.д.
"""
import logging
from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializers, OrderSerializers


log = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):...


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "description",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializers,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        },
    )
    def retrieve(self, *args, **kwargs):
        return super.retrieve(*args, **kwargs)


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filter_fields = ['promocode', 'created_at', 'user']
    ordering_fields = ['created_at', 'promocode']
    search_fields = ['promocode', 'delivery_address']



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
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


# class GroupListView(View):
#     def get(self, request: HttpRequest) -> HttpResponse:
#         context = {
#             "form": GroupForm(),
#             "groups": Group.objects.prefetch_related('permissions').all(),
#         }
#         return render(request, 'shopapp/groups-list.html', context=context)


    # def post(self, request: HttpRequest):
    #     form = GroupForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #
    #     return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = ("name", "price", "description", "discount", "preview")
    permission_required = reverse_lazy("shopapp:products_list")

    # def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        # return self.request.user.is_superuser


    # template_name = "shopapp/product_form.html"
    # success_url = reverse_lazy("shopapp:products_list")
    #
    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    # fields = ("name", "price", "description", "discount", "preview")
    template_name_suffix = "_update_form"
    form_class = ProductForm
    # success_url = reverse_lazy("shopapp:products_list")

    # def test_func(self):
    #     product = self.get_object()
    #     user = self.request.user
    #     if user.is_superuser:
    #         return True
    #     return user.has_perm("shopapp.change_product") and product.created_by == user

    def get_success_url(self):
        return reverse(
            "shopapp:products_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
        .all()
    )

    # template_name = 'shopapp/order_list.html'
    # model = Order #Product
    # context_object_name = "orders" # "products"


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.
        select_related('user').
        prefetch_related('products')
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name", name)
        return JsonResponse({"products": products_data})


class InformationExtraction(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "address": getattr(product, 'address', None),
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})


class OrdersExportView(UserPassesTestMixin, LoginRequiredMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        orders = Order.objects.prefetch_related("products").all()
        data = []

        for order in orders:
            data.append({
                "id": order.pk,
                "address": order.delivery_address,
                "promo_code": order.promocode,
                "user_id": order.user,
                "product_ids": list(order.products.values_list("pk", flat=True)),
            })

        return JsonResponse({"orders": data})