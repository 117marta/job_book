from django.conf import settings


def default_avatar(request):
    return {"default_avatar": settings.DEFAULT_AVATAR}
