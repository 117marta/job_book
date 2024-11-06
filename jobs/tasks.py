from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from jobs.consts import (
    EMAIL_JOB_UPCOMING_DEADLINE_CONTENT,
    EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT,
    JobStatuses,
)
from jobs.models import Job
from users.tasks import send_email_with_celery


@shared_task
def jobs_upcoming_deadline_contractor():
    upcoming_deadline = (now() + relativedelta(days=1)).date()
    jobs = Job.objects.filter(deadline=upcoming_deadline).exclude(
        status__in=[JobStatuses.CLOSED, JobStatuses.FINISHED]
    )
    for job in jobs:
        send_email_with_celery(
            user_pk=job.contractor.pk,
            subject=EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT.format(job.pk),
            content=EMAIL_JOB_UPCOMING_DEADLINE_CONTENT.format(job.pk),
        )
