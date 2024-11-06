from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from jobs.consts import EMAIL_JOB_UPCOMING_DEADLINE_CONTENT, EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT
from jobs.models import Job
from users.tasks import send_email_with_celery


@shared_task
def jobs_upcoming_contractor():
    upcoming_deadline = now() + relativedelta(days=1)
    jobs = Job.objects.filter(deadline__gte=upcoming_deadline)
    for job in jobs:
        send_email_with_celery(
            user_pk=job.contractor.pk,
            template_name="users/email.html",
            subject=EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT.format(job.pk),
            content=EMAIL_JOB_UPCOMING_DEADLINE_CONTENT.format(job.pk),
        )
