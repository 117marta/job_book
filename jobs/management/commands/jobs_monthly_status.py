import csv
import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db.models import CharField, Count, Exists, F, Func, OuterRef, Q, Value

from jobs.models import Job, JobFile

FIELD_NAMES = ["id", "date_formatted", "status", "kind", "has_attachments"]
today = datetime.date.today()
last_month = today - relativedelta(months=1)
file_name = f"{last_month.year}_{last_month.month}_jobs_monthly_status"


class Command(BaseCommand):
    help = "Exports jobs statistics for a previous month."

    @staticmethod
    def export_csv(data):
        with open(file=file_name, mode="w") as file:
            writer = csv.writer(file, dialect="excel")
            writer.writerow(FIELD_NAMES)
            writer.writerows(data)

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
