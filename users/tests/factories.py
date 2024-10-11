import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate

from users.models import ROLES, User


class UserFactory(factory.django.DjangoModelFactory):
    password = factory.Faker("password")
    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("msisdn")
    birth_date = FuzzyDate(start_date=datetime.date(1900, 5, 5), end_date=datetime.date(2005, 5, 5))
    role = FuzzyChoice(dict(ROLES).keys())

    class Meta:
        model = User
