from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from jobs.consts import JobStatuses
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
from users.helpers import send_email
from users.models import User


def registration(request):
    """
    Allow to register a new user.

    :template: users/registration.html
    :param request: the request object
    :return: redirects to the `home-page` page
    """
    form = RegistrationForm(data=request.POST or None, files=request.FILES or None)

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
            avatar = form.cleaned_data.get("avatar")
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone,
                birth_date=birth_date,
                avatar=avatar,
            )
            user.trades.set(trades)

            send_email(
                recipients=[user.email],
                subject=EMAIL_REGISTRATION_SUBJECT,
                content=EMAIL_REGISTRATION_CONTENT,
            )

            messages.success(request, REGISTRATION_SUCCESS_MESSAGE)
            return redirect("home-page")
        else:
            messages.error(request, FORM_ERROR_MESSAGE)
    return render(request=request, template_name="users/registration.html", context={"form": form})


def log_in(request):
    """
    Log in a user.

    :template: users/login.html
    :param request: the request object
    :return: redirects to the `home-page` page
    """
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


@login_required
def log_out(request):
    """
    Log out a user.

    :param request: the request object
    :return: redirects to the home page.
    """
    logout(request)
    messages.success(request, LOGOUT_SUCCESS_MESSAGE)
    return redirect("home-page")


def panel(request):
    """
    Display a user details and his job statistics.

    :template: users/panel.html
    :param request: the request object
    :return: the request response - `panel` page
    """
    user = request.user
    if user and user.is_authenticated:
        roles_dict = {
            "principal": user.jobs_principal.all(),
            "contractor": user.jobs_contractor.all(),
        }
        jobs_statistics = {}
        for role, query in roles_dict.items():
            result = {
                "all": query.count(),
                "statuses": {
                    status.label: query.filter(status=status).count() for status in JobStatuses
                },
            }
            jobs_statistics[role] = result

        return render(
            request=request,
            template_name="users/panel.html",
            context={
                "user": user,
                "jobs_statistics": jobs_statistics,
            },
        )
    else:
        messages.info(request, LOGIN_NECESSITY_MESSAGE)
        return redirect("home-page")


@login_required
def users_all(request):
    """
    Display all users as a table.

    :template: users/users_all.html
    :param request: the request object
    :return: the request response - `users-all` page
    """
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


@login_required
def accept_or_delete_inactive_users(request):
    """
    Display all inactive users for acceptance or deletion.

    :template: users/accept_or_delete.html
    :param request: the request object
    :return: the request response - `accept-or-delete` page
    """
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
                    send_email(
                        recipients=[user.email],
                        subject=EMAIL_ACCEPTANCE_SUBJECT,
                        content=EMAIL_ACCEPTANCE_CONTENT,
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
