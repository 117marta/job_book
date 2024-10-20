import datetime
from decimal import Decimal
from random import choice

from django.core.management.base import BaseCommand
from faker import Faker

from jobs.consts import JobKinds, JobStatuses
from jobs.models import Job
from trades.models import Trade
from users.models import GENERAL_CONTRACTOR, SUBCONTRACTOR, SURVEYOR, User

fake = Faker("pl_PL")


class Command(BaseCommand):
    help = "Populates the database with jobs."

    def handle(self, *args, **options):
        surveyors_pk = User.objects.filter(role=SURVEYOR).values_list("pk", flat=True)
        subcontractors_pk = User.objects.filter(role=SUBCONTRACTOR).values_list("pk", flat=True)
        principals_pk = User.objects.filter(role__in=GENERAL_CONTRACTOR).values_list(
            "pk", flat=True
        )

        for _ in range(20):
            principal = User.objects.get(pk=choice(principals_pk))
            contractor = User.objects.get(pk=choice(surveyors_pk))
            trade = Trade.objects.get(pk=choice(range(1, 11)))
            kind = fake.random_element(elements=JobKinds)
            description = fake.text(max_nb_chars=512)
            km_from = fake.pydecimal(left_digits=3, right_digits=3, positive=True)
            km_to = km_from + Decimal(0.1)
            deadline = fake.date_between(
                datetime.date.today() + datetime.timedelta(days=1),
                datetime.date.today() + datetime.timedelta(days=7),
            )
            comments = fake.text(max_nb_chars=128)
            status = fake.random_element(JobStatuses)

            Job.objects.create(
                principal=principal,
                contractor=contractor,
                trade=trade,
                kind=kind,
                description=description,
                km_from=km_from,
                km_to=km_to,
                deadline=deadline,
                comments=comments,
                status=status,
            )

        self.stdout.write(self.style.SUCCESS("Jobs have been completed successfully!"))
