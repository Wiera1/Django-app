from django.urls import path

from myauth.views import login_view

app_name = "myauth"

urlpatterns = [
    path("login/", login_view, name="login"),
]