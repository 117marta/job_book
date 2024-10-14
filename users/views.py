from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from users.const import (
    ADMIN_NECESSITY_MESSAGE,
    EMAIL_ACCEPTANCE_CONTENT,
    EMAIL_ACCEPTANCE_SUBJECT,
    EMAIL_REGISTRATION_CONTENT,
    EMAIL_REGISTRATION_SUBJECT,
    FORM_ERROR_MESSAGE,
    LOGIN_FAIL_MESSAGE,
    LOGIN_NECESSITY_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    REGISTRATION_SUCCESS_MESSAGE,
    USERS_ACCEPTED,
    USERS_DELETED,
    USERS_OBJECTS_PER_PAGE,
)
from users.forms import AcceptOrDeleteForm, LoginForm, RegistrationForm
from users.helpers import convert_to_html_content, plain_message
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

            user.email_user(
                subject=EMAIL_REGISTRATION_SUBJECT,
                message=plain_message(),
                html_message=convert_to_html_content(
                    template_name="users/email.html",
                    context={
                        "user_name": user.get_full_name(),
                        "content": EMAIL_REGISTRATION_CONTENT,
                    },
                ),
            )

            messages.success(request, REGISTRATION_SUCCESS_MESSAGE)
            return redirect("home-page")
        else:
            messages.error(request, FORM_ERROR_MESSAGE)
    return render(request=request, template_name="users/registration.html", context={"form": form})


def log_in(request):
    form = LoginForm(request.POST or None)
    next_url = request.GET.get("next")

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, LOGIN_SUCCESS_MESSAGE)
                if next_url:
                    return redirect(next_url)
                else:
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


@login_required(login_url="login")
def accept_or_delete_inactive_users(request):
    if not request.user.is_admin:
        messages.error(request, ADMIN_NECESSITY_MESSAGE)
        return redirect("home-page")

    form = AcceptOrDeleteForm(request.POST or None)
    inactive_users = User.objects.filter(is_active=False)

    if request.method == "POST":
        if form.is_valid():
            users_list = request.POST.getlist("action_checkbox")
            if "action_accept" in request.POST:
                form.accept_users(users_list)
                for user in User.objects.filter(pk__in=users_list):
                    user.email_user(
                        subject=EMAIL_ACCEPTANCE_SUBJECT,
                        message=plain_message(),
                        html_message=convert_to_html_content(
                            template_name="users/email.html",
                            context={
                                "user_name": user.get_full_name(),
                                "content": EMAIL_ACCEPTANCE_CONTENT,
                            },
                        ),
                    )
                messages.success(request, USERS_ACCEPTED.format(len(users_list)))
            else:
                form.delete_users(users_list)
                messages.error(request, USERS_DELETED.format(len(users_list)))

    return render(
        request=request,
        template_name="users/accept_or_delete.html",
        context={"form": form, "inactive_users": inactive_users},
    )
