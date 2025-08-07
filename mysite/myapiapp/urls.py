from django.urls import path

from .views import hello_world_view, GroupsListView, OrderListView

app_name = "myapiapp"

urlpatterns = [
    path("hello/", hello_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
    path("order/", OrderListView.as_view(), name="order"),
]