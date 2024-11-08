from django.shortcuts import render


def home_page(request):
    """
    Display a main page.

    :template: home_page/home-page.html
    :param request: the request object
    :return: the request response - home page.
    """
    return render(
        request=request,
        template_name="home_page/home-page.html",
    )
