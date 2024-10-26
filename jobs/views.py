from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from jobs.consts import JOBS_PER_PAGE
from jobs.models import Job


@login_required(login_url="login")
def jobs_all(request):
    jobs = Job.objects.all().order_by("created")
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
