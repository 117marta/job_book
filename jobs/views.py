from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from jobs.consts import JOB_CREATE_SUCCESS_MESSAGE, JOBS_PER_PAGE
from jobs.forms import JobCreateForm
from jobs.models import Job


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
            messages.success(request, JOB_CREATE_SUCCESS_MESSAGE)
            return redirect("jobs-all")

    return render(request=request, template_name="jobs/create.html", context={"form": form})
