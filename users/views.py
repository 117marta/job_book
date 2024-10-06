from django.shortcuts import redirect, render
from users.forms import RegistrationForm
from users.models import User


def registration(request):
    form = RegistrationForm(request.POST or None)

    if request.method == "POST":
        breakpoint()
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
            return redirect("home-page")
    return render(request=request, template_name="users/registration.html", context={"form": form})
