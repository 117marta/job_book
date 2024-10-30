from django.urls import path, re_path

from jobs import views

urlpatterns = [
    path("jobs-all/", views.jobs_all, name="jobs-all"),
    path("create/", views.job_create, name="jobs-create"),
    path("job/<int:job_pk>/", views.job_view, name="jobs-job"),
    path("my-jobs/", views.my_jobs, name="jobs-my-job"),
    re_path(
        r"^my-jobs/(?P<status>waiting|accepted|refused|making_documents|ready_to_stake_out|data_passed|ongoing|finished|closed|in_progress)/$",
        views.my_jobs,
        name="jobs-my-jobs",
    ),
]
