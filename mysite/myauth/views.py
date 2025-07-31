from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseForbidden

from .forms import ProfileForm
from .models import Profile

class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        resource = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return resource

def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")

@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

def get_cookie_view(request:HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")

@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value {value!r}")

class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


@login_required
def about_me(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        else:
            form = ProfileForm(isinstance=profile)

        return render(request, 'myauth/about_me.html', {'profile': profile, 'form': form})


@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, 'myauth/users_list.html', {'users': users})


@login_required
def user_profile(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    profile = user_obj.profile

    can_edit = request.user.is_stuff or request.user == user_obj

    if request.method == 'POST':
        if not can_edit:
            return HttpResponseForbidden("You don't have permission to edit this profile")
        form = ProfileForm(request.POST, request.FIKES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('myauth:user-profile', user_id=user_id)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_obj': user_obj,
        'can_edit': can_edit,
        'form': form,
    }
    return render(request, 'myauth/user_profile.html', context)