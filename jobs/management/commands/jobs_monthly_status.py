import csv
import datetime
import os

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db.models import CharField, Count, Exists, F, Func, OuterRef, Q, Value

from job_book.settings import MEDIA_ROOT
from jobs.consts import EMAIL_JOB_MONTHLY_STATUS_CONTENT, EMAIL_JOB_MONTHLY_STATUS_SUBJECT
from jobs.models import Job, JobFile
from users.helpers import send_email
from users.models import CONTRACT_DIRECTOR, CONTRACT_MANAGER, User

FIELD_NAMES = ["id", "date_formatted", "status", "kind", "has_attachments"]
today = datetime.date.today()
last_month = today - relativedelta(months=1)
file_name = f"{last_month.year}_{last_month.month}_jobs_monthly_status.csv"
directory = "reports"


class Command(BaseCommand):
    help = "Exports jobs statistics for a previous month."

    @staticmethod
    def export_csv(data):
        """Save the monthly statistics as a CSV file and send it by an e-mail."""
        try:
            os.makedirs(os.path.join(MEDIA_ROOT, directory))
        except OSError:
            pass
        csv_file = os.path.join(MEDIA_ROOT, directory, file_name)

        with open(file=csv_file, mode="w") as file:
            writer = csv.writer(file, dialect="excel")
            writer.writerow(FIELD_NAMES)
            writer.writerows(data)

        users_email_list = list(
            User.objects.filter(role__in=[CONTRACT_DIRECTOR, CONTRACT_MANAGER]).values_list(
                "email", flat=True
            )
        )
        send_email(
            recipients=users_email_list,
            subject=EMAIL_JOB_MONTHLY_STATUS_SUBJECT,
            content=EMAIL_JOB_MONTHLY_STATUS_CONTENT.format(
                year=last_month.year, month=last_month.strftime("%B")
            ),
            attachments=[csv_file],
        )

    def handle(self, *args, **options):
        data = (
            Job.objects.annotate(
                has_attachments=Exists(
                    JobFile.objects.filter(content_type__model="job", object_id=OuterRef("pk"))
                ),
                date_formatted=Func(
                    F("created"), Value("DD.MM.YYYY"), function="to_char", output_field=CharField()
                ),
            )
            .filter(
                created__year=last_month.year,
                created__month=last_month.month,
            )
            .order_by("pk")
            .values_list(*FIELD_NAMES)
        )

        output = list(data)
        output.append(["Number of jobs:", data.aggregate(Count("pk"))["pk__count"]])

        data_statuses = data.aggregate(
            waiting=Count("status", filter=Q(status="waiting")),
            accepted=Count("status", filter=Q(status="accepted")),
            refused=Count("status", filter=Q(status="refused")),
            making_documents=Count("status", filter=Q(status="making_documents")),
            ready_to_stake_out=Count("status", filter=Q(status="ready_to_stake_out")),
            data_passed=Count("status", filter=Q(status="data_passed")),
            ongoing=Count("status", filter=Q(status="ongoing")),
            finished=Count("status", filter=Q(status="finished")),
            closed=Count("status", filter=Q(status="closed")),
        )
        output.append(list(data_statuses.keys()))
        output.append(list(data_statuses.values()))

        data_kinds = data.aggregate(
            staking=Count("kind", filter=Q(kind="staking")),
            inventory=Count("kind", filter=Q(kind="inventory")),
            other=Count("kind", filter=Q(kind="other")),
        )
        output.append([*data_kinds])
        output.append([*data_kinds.values()])

        self.export_csv(output)
