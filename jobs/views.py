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
from jobs.forms import JobCreateForm, JobFileForm, JobViewForm
from jobs.models import Job, JobFile
from users.tasks import send_email_with_celery


@login_required
def jobs_all(request):
    """
    Display all jobs as a table.

    :template: jobs/jobs_all.html
    :param request: the request object
    :return: the request response - `jobs-all` page
    """
    page_number = request.GET.get("page")
    order_by = request.GET.get("order_by", "-created")
    jobs = Job.objects.all().order_by(order_by)
    paginator = Paginator(jobs, per_page=JOBS_PER_PAGE)
    page_object = paginator.get_page(page_number)
    return render(
        request=request,
        template_name="jobs/jobs_all.html",
        context={
            "jobs": jobs,
            "page_object": page_object,
            "paginator": paginator,
            "order_by": order_by,
        },
    )


@login_required
def job_create(request):
    """
    Create a new job and a job file in the database.

    :template: jobs/create.html
    :param request: the request object
    :return: redirects to the `jobs-all` page
    """
    form = JobCreateForm(data=request.POST or None, user=request.user)
    job_file_form = JobFileForm(data=request.POST or None, files=request.FILES or None)

    if request.method == "POST":
        if form.is_valid() and job_file_form.is_valid():
            principal = form.cleaned_data["principal"]
            contractor = form.cleaned_data["contractor"]
            trade = form.cleaned_data["trade"]
            form.save()

            if files := job_file_form.cleaned_data.get("file"):
                JobFile.objects.create(file=files, content_object=form.instance)

            send_email_with_celery.delay(
                user_pk=contractor.pk,
                subject=EMAIL_JOB_CREATE_SUBJECT,
                content=EMAIL_JOB_CREATE_CONTENT.format(principal.get_full_name(), trade.name),
            )

            messages.success(request, JOB_CREATE_SUCCESS_MESSAGE)
            return redirect("jobs-all")

    return render(
        request=request,
        template_name="jobs/create.html",
        context={"form": form, "job_file_form": job_file_form},
    )


@login_required
def job_view(request, job_pk):
    """
    Display the details of a specific job.

    :template: jobs/job.html
    :param request: the request object
    :param int job_pk: a job pk
    :return: redirects to the `jobs-all` page
    """
    job = get_object_or_404(Job, pk=job_pk)
    form = JobViewForm(data=request.POST or None, instance=job, user=request.user)
    attachments = job.get_job_files

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
                        subject=EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT.format(job_pk),
                        content=EMAIL_JOB_CHANGE_CONTRACTOR_CONTENT.format(
                            job_pk=job_pk, trade=job.trade, url=job_url
                        ),
                    )
            form.save()
            messages.success(request, JOB_SAVE_SUCCESS_MESSAGE)
            return redirect("jobs-all")

    return render(request, "jobs/job.html", {"job": job, "form": form, "attachments": attachments})


@login_required
def my_jobs(request, status=JobStatuses.WAITING):
    """
    Display user jobs.

    :template: jobs/my_jobs.html
    :param request: the request object
    :param str status: a status of the job
    :return: the request response - `jobs-my-jobs` page
    """
    user = request.user
    role = request.session.get("role", None)
    if not role:
        return render(request, "jobs/my_jobs.html")

    jobs = Job.objects.all().order_by("-pk")
    if role == JOB_ROLE_PRINCIPAL:
        jobs = jobs.filter(principal=user)
    else:
        jobs = jobs.filter(contractor=user)

    if status == "in_progress":
        role_filter = {role: user}
        jobs = jobs.filter(
            **role_filter,
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
    """
    Sets the user role (principal/contractor) in the session.

    :param request: the request object
    :param str role_url: a user role
    :return: redirects to the `jobs-my-jobs` page
    """
    request.session["role"] = role_url
    return redirect("jobs-my-jobs")
