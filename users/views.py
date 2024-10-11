from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render

from users.const import (
    FORM_ERROR_MESSAGE,
    LOGIN_FAIL_MESSAGE,
    LOGIN_NECESSITY_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    REGISTER_SUCCESS_MESSAGE,
    USERS_OBJECTS_PER_PAGE,
)
from users.forms import LoginForm, RegistrationForm
from users.models import User


def registration(request):
    form = RegistrationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password2")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            phone = form.cleaned_data.get("phone")
            role = form.cleaned_data.get("role")
            birth_date = form.cleaned_data.get("birth_date")
            trades = form.cleaned_data.get("trades")
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone,
                birth_date=birth_date,
            )
            user.trades.set(trades)
            messages.success(request, REGISTER_SUCCESS_MESSAGE)
            return redirect("home-page")
        else:
            messages.error(request, FORM_ERROR_MESSAGE)
    return render(request=request, template_name="users/registration.html", context={"form": form})


def log_in(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, LOGIN_SUCCESS_MESSAGE)
                return redirect("home-page")
            else:
                messages.error(request, LOGIN_FAIL_MESSAGE)

    return render(request, "users/login.html", {"form": form})


@login_required(login_url="login")
def log_out(request):
    logout(request)
    messages.success(request, LOGOUT_SUCCESS_MESSAGE)
    return redirect("home-page")


def panel(request):
    user = request.user
    if user and user.is_authenticated:
        return render(request=request, template_name="users/panel.html", context={"user": user})
    else:
        messages.info(request, LOGIN_NECESSITY_MESSAGE)
        return redirect("home-page")


@login_required(login_url="login")
def users_all(request):
    users = User.objects.all().order_by("last_name", "first_name")
    paginator = Paginator(users, per_page=USERS_OBJECTS_PER_PAGE)

    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    adjusted_elided_pages = paginator.get_elided_page_range(
        number=page_object.number, on_each_side=2, on_ends=1
    )
    return render(
        request=request,
        template_name="users/users_all.html",
        context={
            "users": users,
            "page_object": page_object,
            "paginator": paginator,
            "adjusted_elided_pages": adjusted_elided_pages,
        },
    )
