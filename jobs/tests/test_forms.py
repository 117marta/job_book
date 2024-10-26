import datetime

from django.test import TestCase
from parameterized import parameterized

from jobs.consts import DEADLINE_FORM_ERROR, JobKinds
from jobs.forms import JobCreateForm
from trades.factories import TradeFactory
from users.models import SITE_MANAGER, SURVEYOR
from users.tests.factories import UserFactory


class TestJobCreateForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.principal = UserFactory.create(is_active=True, role=SITE_MANAGER)
        cls.surveyor = UserFactory.create(is_active=True, role=SURVEYOR)
        cls.trade = TradeFactory.create()
        cls.data = {
            "principal": cls.principal.pk,
            "contractor": cls.surveyor.pk,
            "kind": JobKinds.STAKING,
            "trade": cls.trade.pk,
            "description": "Test description",
            "km_from": "12.345",
            "km_to": "12.400",
            "deadline": datetime.date.today() + datetime.timedelta(days=3),
            "comments": "Test comments",
        }

    def test_create_a_job_correct_data(self):
        """
        Test should pass, because the correct data is sent.
        """
        # Act
        form = JobCreateForm(data=self.data)

        # Assert
        self.assertTrue(form.is_valid())

    def test_create_a_job_empty_data(self):
        """
        Test should fail, because empty data is sent.
        """
        # Arrange
        expected_errors = {
            "principal": ["This field is required."],
            "contractor": ["This field is required."],
            "kind": ["This field is required."],
            "trade": ["This field is required."],
            "description": ["This field is required."],
            "km_from": ["This field is required."],
            "deadline": ["This field is required."],
        }
        # Act
        form = JobCreateForm(data={})

        # Assert
        self.assertFalse(form.is_valid())
        self.assertEqual(expected_errors, form.errors)

    @parameterized.expand(
        [
            ("past", False),
            ("today", True),
            ("future", True),
        ]
    )
    def test_create_a_job_deadline(self, fake_date, is_valid):
        """
        Check if the test will pass depending on the fake deadline.
        """
        # Arrange
        expected_errors = {"deadline": [DEADLINE_FORM_ERROR]}
        match fake_date:
            case "past":
                deadline = datetime.date.today() - datetime.timedelta(days=10)
            case "today":
                deadline = datetime.date.today()
            case _:
                deadline = datetime.date.today() + datetime.timedelta(days=2)

        # Act
        form = JobCreateForm(data=self.data)
        self.data["deadline"] = deadline

        # Assert
        if is_valid:
            self.assertTrue(form.is_valid())
        else:
            self.assertFalse(form.is_valid())
            self.assertEqual(expected_errors, form.errors)
