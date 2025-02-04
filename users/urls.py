from django.urls import path

from users import api_views, views

urlpatterns = [
    path("registration/", views.registration, name="registration"),
    path("login/", views.log_in, name="login"),
    path("logout/", views.log_out, name="logout"),
    path("panel/", views.panel, name="panel"),
    path("users-all/", views.users_all, name="users-all"),
    path("accept-or-delete/", views.accept_or_delete_inactive_users, name="accept-or-delete"),
    path("api/get-users/", api_views.get_users, name="api-get-users"),
]
