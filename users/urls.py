from django.urls import path

from users import views

urlpatterns = [
    path("registration/", views.registration, name="registration"),
    path("login/", views.log_in, name="login"),
    path("logout/", views.log_out, name="logout"),
    path("panel/", views.panel, name="panel"),
    path("users-all/", views.users_all, name="users-all"),
]
