from django.urls import path
from .views import shop_index

app_namr = 'shopapp'

urlpatterns = [
    path('', shop_index, name='index'),
]