from django.urls import path

from jobs import views

urlpatterns = [
    path("jobs-all/", views.jobs_all, name="jobs-all"),
    path("create/", views.job_create, name="jobs-create"),
    path("job/<int:job_pk>", views.job_view, name="jobs-job"),
]
