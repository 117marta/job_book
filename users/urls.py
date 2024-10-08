from django.urls import path

from users import views

urlpatterns = [
    path("registration/", views.registration, name="registration"),
]
