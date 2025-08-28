from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap
from shopapp.sitemap import ShopSitemap

from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    ShopIndexView,
    # GroupListView,
    ProductDetailsView,
    ProductsListView,
    OrderDetailView,
    OrdersListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    OrdersExportView,
    ProductViewSet,
    OrdersViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrdersExportView,
)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrdersViewSet)


sitemaps = {
    'shop': ShopSitemap,
}


urlpatterns = [
    # path('', cache_page(60*3)(ShopIndexView.as_view()), name='index'),
    path('', ShopIndexView.as_view(), name='index'),
    path("api/", include(routers.urls)),
    # path("groups/", GroupListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="products_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/<slug:slug>/', ProductDetailsView.as_view(), name='product_detale'),
    path('orders_list/', OrdersListView.as_view(), name='orders_list'),
    path('orders_list/<int:pk>/', OrderDetailView.as_view(), name='orders_details'),
    # path("orders-export/", OrdersExportView.as_view(), name="orders_export"),
    path("sitemap.xml",
         sitemap,
         {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemaps"),
    path('products/latest/feed/', LatestProductsFeed(), name='products_latest_feed'),
    path("users/<int:user_id>/orders", UserOrdersListView.as_view(), name="user_orders"),
    path("users/<int:user_id>/orders/export", UserOrdersExportView.as_view(), name="user_orders"),
]