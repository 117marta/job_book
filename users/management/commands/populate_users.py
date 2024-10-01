from faker import Faker
from random import choice

from django.core.management.base import BaseCommand

from trades.models import (
    ABBREVIATION_BRIDGE,
    ABBREVIATION_CONSTRUCTION,
    ABBREVIATION_CONTACT_SYSTEM,
    ABBREVIATION_DRAINAGE,
    ABBREVIATION_OTHER,
    ABBREVIATION_POWER_ENGINEERING,
    ABBREVIATION_RAILWAY,
    ABBREVIATION_RAILWAY_TRAFFIC,
    ABBREVIATION_ROAD,
    ABBREVIATION_TELECOMMUNICATION,
    Trade,
)
from users.models import (
    CONTRACT_DIRECTOR,
    CONTRACT_MANAGER,
    CLERK_OF_THE_WORKS,
    SITE_MANAGER,
    SITE_ENGINEER,
    SUBCONTRACTOR,
    SURVEYOR,
    User,
)

fake = Faker("pl_PL")

ALL_TRADES = [
    ABBREVIATION_BRIDGE,
    ABBREVIATION_CONSTRUCTION,
    ABBREVIATION_CONTACT_SYSTEM,
    ABBREVIATION_DRAINAGE,
    ABBREVIATION_OTHER,
    ABBREVIATION_POWER_ENGINEERING,
    ABBREVIATION_RAILWAY,
    ABBREVIATION_RAILWAY_TRAFFIC,
    ABBREVIATION_ROAD,
    ABBREVIATION_TELECOMMUNICATION,
]


class Command(BaseCommand):
    help = "Populates the database with fake users."
    PASSWORD = "."
    MINIMUM_AGE = 20
    MAXIMUM_AGE = 60
    NUMBER_OF_SUBCONTRACTORS = 13
    NUMBER_OF_SURVEYORS = 7

    def _populate_users(self, role, birth_date=None, trade=None, trades=None):
        if birth_date:
            birth_date = fake.date_of_birth(
                minimum_age=self.MINIMUM_AGE, maximum_age=self.MAXIMUM_AGE
            )
        user = User.objects.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password=self.PASSWORD,
            role=role,
            phone=fake.phone_number(),
            birth_date=birth_date,
        )
        if trade:
            user.trade.add(trade)
        if trades:
            user.trade.add(*trades)

    def handle(self, *args, **options):
        bridge = Trade.objects.get(abbreviation=ABBREVIATION_BRIDGE)
        construction = Trade.objects.get(abbreviation=ABBREVIATION_CONSTRUCTION)
        contact_system = Trade.objects.get(abbreviation=ABBREVIATION_CONTACT_SYSTEM)
        railway = Trade.objects.get(abbreviation=ABBREVIATION_RAILWAY)
        road = Trade.objects.get(abbreviation=ABBREVIATION_ROAD)

        self._populate_users(role=CONTRACT_DIRECTOR, birth_date=True, trade=railway)
        self._populate_users(role=CONTRACT_MANAGER, birth_date=True, trades=(railway, road))
        self._populate_users(
            role=SITE_MANAGER, birth_date=True, trades=(railway, road, construction)
        )

        # Create site managers and site engineers
        for trade in ALL_TRADES:
            self._populate_users(
                role=CLERK_OF_THE_WORKS,
                birth_date=True,
                trade=Trade.objects.get(abbreviation=trade),
            )
            self._populate_users(
                role=SITE_ENGINEER, birth_date=True, trade=Trade.objects.get(abbreviation=trade)
            )
        self._populate_users(role=CLERK_OF_THE_WORKS, birth_date=True, trade=railway)
        self._populate_users(role=CLERK_OF_THE_WORKS, birth_date=True, trade=bridge)
        self._populate_users(role=CLERK_OF_THE_WORKS, birth_date=True, trade=contact_system)
        self._populate_users(role=SITE_ENGINEER, birth_date=True, trade=railway)
        self._populate_users(role=SITE_ENGINEER, birth_date=True, trade=bridge)
        self._populate_users(role=SITE_ENGINEER, birth_date=True, trade=contact_system)

        # Create surveyors
        for _ in range(self.NUMBER_OF_SURVEYORS):
            self._populate_users(role=SURVEYOR)

        # Create subcontractors
        ALL_TRADES.remove(ABBREVIATION_OTHER)
        for _ in range(self.NUMBER_OF_SUBCONTRACTORS):
            choice_trade = choice(ALL_TRADES)
            self._populate_users(
                role=SUBCONTRACTOR, trade=Trade.objects.get(abbreviation=choice_trade)
            )

        self.stdout.write(self.style.SUCCESS("Users have been completed successfully!"))
