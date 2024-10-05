from django.shortcuts import render


def home_page(request):
    return render(request=request, template_name="home_page/home-page.html")
