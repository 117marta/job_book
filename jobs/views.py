from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render, reverse

from jobs.consts import (
    EMAIL_JOB_CHANGE_CONTRACTOR_CONTENT,
    EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT,
    EMAIL_JOB_CHANGE_STATUS_CONTENT,
    EMAIL_JOB_CHANGE_STATUS_SUBJECT,
    EMAIL_JOB_CREATE_CONTENT,
    EMAIL_JOB_CREATE_SUBJECT,
    JOB_CREATE_SUCCESS_MESSAGE,
    JOB_ROLE_PRINCIPAL,
    JOB_SAVE_SUCCESS_MESSAGE,
    JOBS_PER_PAGE,
    JobStatuses,
)
from jobs.forms import JobCreateForm, JobViewForm
from jobs.models import Job
from users.tasks import send_email_with_celery


@login_required(login_url="login")
def jobs_all(request):
    jobs = Job.objects.all().order_by("-created")
    paginator = Paginator(jobs, per_page=JOBS_PER_PAGE)

    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    adjusted_elided_pages = paginator.get_elided_page_range(
        number=page_object.number, on_each_side=2, on_ends=1
    )
    return render(
        request=request,
        template_name="jobs/jobs_all.html",
        context={
            "users": jobs,
            "page_object": page_object,
            "paginator": paginator,
            "adjusted_elided_pages": adjusted_elided_pages,
        },
    )


@login_required(login_url="login")
def job_create(request):
    form = JobCreateForm(data=request.POST or None, instance=request.user)

    if request.method == "POST":
        if form.is_valid():
            principal = form.cleaned_data["principal"]
            contractor = form.cleaned_data["contractor"]
            kind = form.cleaned_data["kind"]
            trade = form.cleaned_data["trade"]
            description = form.cleaned_data["description"]
            km_from = form.cleaned_data["km_from"]
            km_to = form.cleaned_data["km_to"]
            deadline = form.cleaned_data["deadline"]
            comments = form.cleaned_data["comments"]

            Job.objects.create(
                principal=principal,
                contractor=contractor,
                kind=kind,
                trade=trade,
                description=description,
                km_from=km_from,
                km_to=km_to,
                deadline=deadline,
                comments=comments,
            )

            send_email_with_celery.delay(
                user_pk=contractor.pk,
                template_name="users/email.html",
                subject=EMAIL_JOB_CREATE_SUBJECT,
                content=EMAIL_JOB_CREATE_CONTENT.format(principal.get_full_name(), trade.name),
            )

            messages.success(request, JOB_CREATE_SUCCESS_MESSAGE)
            return redirect("jobs-all")

    return render(request=request, template_name="jobs/create.html", context={"form": form})


@login_required(login_url="login")
def job_view(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk)
    form = JobViewForm(data=request.POST or None, instance=job, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            principal = form.cleaned_data["principal"]
            contractor = form.cleaned_data["contractor"]
            status = form.cleaned_data["status"]
            if form.has_changed():
                job_url = settings.BASE_URL + reverse("jobs-job", kwargs={"job_pk": job_pk})
                if "status" in form.changed_data:
                    send_email_with_celery.delay(
                        user_pk=principal.pk,
                        template_name="users/email.html",
                        subject=EMAIL_JOB_CHANGE_STATUS_SUBJECT.format(job_pk),
                        content=EMAIL_JOB_CHANGE_STATUS_CONTENT.format(
                            job_pk=job_pk,
                            status=JobStatuses(status).label.capitalize(),
                            url=job_url,
                        ),
                    )
                if "contractor" in form.changed_data:
                    send_email_with_celery.delay(
                        user_pk=contractor.pk,
                        template_name="users/email.html",
                        subject=EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT.format(job_pk),
                        content=EMAIL_JOB_CHANGE_CONTRACTOR_CONTENT.format(
                            job_pk=job_pk, trade=job.trade, url=job_url
                        ),
                    )
            form.save()
            messages.success(request, JOB_SAVE_SUCCESS_MESSAGE)
            return redirect("jobs-all")

    return render(request, "jobs/job.html", {"job": job, "form": form})


@login_required(login_url="login")
def my_jobs(request, status=JobStatuses.WAITING):
    user = request.user
    role = request.session.get("role", None)
    jobs = Job.objects.all().order_by("-pk")

    if role == JOB_ROLE_PRINCIPAL:
        jobs = jobs.filter(principal=user)
    else:
        jobs = jobs.filter(contractor=user)

    if status == "in_progress":
        jobs = jobs.filter(
            principal=user,
            status__in=[
                JobStatuses.MAKING_DOCUMENTS,
                JobStatuses.READY_TO_STAKE_OUT,
                JobStatuses.DATA_PASSED,
                JobStatuses.ONGOING,
            ],
        )
    else:
        jobs = jobs.filter(status=status)

    return render(request, "jobs/my_jobs.html", {"jobs": jobs, "role": role})


def set_role_session(request, role_url=JOB_ROLE_PRINCIPAL):
    request.session["role"] = role_url
    return redirect("jobs-my-jobs")
