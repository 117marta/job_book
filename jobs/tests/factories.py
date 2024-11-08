import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyDecimal

from jobs.consts import JobKinds, JobStatuses
from jobs.models import Job
from trades.factories import TradeFactory
from users.tests.factories import UserFactory


class JobFactory(factory.django.DjangoModelFactory):
    """
    Create a Job Factory object for the tests with pre-defined values.
    """

    principal = factory.SubFactory(UserFactory)
    contractor = factory.SubFactory(UserFactory)
    kind = FuzzyChoice(JobKinds)
    trade = factory.SubFactory(TradeFactory)
    description = factory.Faker("text", max_nb_chars=64)
    km_from = FuzzyDecimal(low=100, high=120, precision=3)
    km_to = FuzzyDecimal(low=100, high=120, precision=3)
    deadline = FuzzyDate(
        start_date=datetime.date.today() + datetime.timedelta(days=1),
        end_date=datetime.date.today() + datetime.timedelta(days=7),
    )
    comments = factory.Faker("text", max_nb_chars=32)
    status = FuzzyChoice(JobStatuses)

    class Meta:
        model = Job
