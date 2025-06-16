from django.urls import path

from .views import (
    ShopIndexView,
    GroupListView,
    ProductDetailsView,
    products_list,
    orders_list)

app_name = 'shopapp'

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path("groups/", GroupListView.as_view(), name="groups_list"),
    path("products/", products_list, name="products_list"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path('orders_list/', orders_list, name='orders_list'),
]