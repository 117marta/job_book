from django.conf import settings
from django.shortcuts import render


def home_page(request):
    default_avatar = settings.DEFAULT_AVATAR
    return render(
        request=request,
        template_name="home_page/home-page.html",
        context={"default_avatar": default_avatar},
    )
