import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate

from users.models import ROLES, User


class UserFactory(factory.django.DjangoModelFactory):
    """
    Create a User Factory object for the tests with pre-defined values.
    """

    password = factory.Faker("password")
    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    is_active = False
    phone = factory.Faker("msisdn")
    birth_date = FuzzyDate(start_date=datetime.date(1900, 5, 5), end_date=datetime.date(2005, 5, 5))
    role = FuzzyChoice(dict(ROLES).keys())

    class Meta:
        model = User
