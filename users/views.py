from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from users.const import (
    FORM_ERROR_MESSAGE,
    LOGIN_FAIL_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    REGISTER_SUCCESS_MESSAGE,
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
            trade = form.cleaned_data.get("trade")
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone,
                birth_date=birth_date,
            )
            user.trade.set(trade)
            messages.success(request, REGISTER_SUCCESS_MESSAGE)
            return redirect("home-page")
        else:
            messages.error(request, FORM_ERROR_MESSAGE)
    return render(request=request, template_name="users/registration.html", context={"form": form})


def logging(request):
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
