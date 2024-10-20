from django.urls import path

from jobs import views

urlpatterns = [
    path("jobs-all/", views.jobs_all, name="jobs-all"),
]
