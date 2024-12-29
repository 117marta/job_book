import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from parameterized import parameterized

from jobs.consts import DEADLINE_FORM_ERROR, JobKinds, JobStatuses
from jobs.forms import JobCreateForm, JobFileForm, JobViewForm
from jobs.tests.factories import JobFactory
from trades.factories import TradeFactory
from users.models import SITE_ENGINEER, SITE_MANAGER, SURVEYOR
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
        cls.file = SimpleUploadedFile(
            name="test_file.pdf",
            content=b"Test content",
            content_type="application/pdf",
        )

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

    @parameterized.expand(["zero", "one", "two"])
    def test_create_a_job_with_a_file(self, quantity):
        """
        Check if the test will pass depending on the number of uploaded files.
        """
        # Arrange
        if quantity == "zero":
            data = {}
        elif quantity == "one":
            data = {"files": self.file}
        else:
            data = {"files": [self.file, self.file]}

        # Act
        form = JobFileForm(data=data)

        # Assert
        self.assertTrue(form.is_valid())


class TestJobViewForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.principal = UserFactory.create(is_active=True, role=SITE_ENGINEER)
        cls.contractor = UserFactory.create(is_active=True, role=SURVEYOR)
        cls.new_contractor = UserFactory.create(is_active=True, role=SURVEYOR)
        cls.job = JobFactory.create(
            principal=cls.principal,
            contractor=cls.contractor,
            kind=JobKinds.INVENTORY,
            status=JobStatuses.WAITING,
        )

    @parameterized.expand(
        [
            "all",
            "contractor",
            "status",
            "comments",
        ]
    )
    def test_update_a_job_data(self, changed_data):
        """
        Check if the test will pass depending on the data changed.
        """
        # Arrange
        form = JobViewForm(instance=self.job)
        data = form.initial.copy()
        new_status = JobStatuses.READY_TO_STAKE_OUT
        new_comments = "New test comment"
        finished_status = JobStatuses.FINISHED
        finished_comments = "The job is finished."

        match changed_data:
            case "contractor":
                data["contractor"] = self.new_contractor.pk
            case "status":
                data["status"] = new_status
            case "comments":
                data["comments"] = new_comments
            case "all":
                data = {
                    "contractor": self.contractor.pk,
                    "status": finished_status,
                    "comments": finished_comments,
                }

        # Act
        form = JobViewForm(instance=self.job, data=data, user=self.principal)
        form.save()

        # Assert
        self.assertTrue(form.is_valid())
        self.job.refresh_from_db()
        match changed_data:
            case "contractor":
                self.assertEqual(self.job.contractor, self.new_contractor)
            case "status":
                self.assertEqual(self.job.status, new_status)
            case "comments":
                self.assertEqual(self.job.comments, new_comments)
            case "all":
                self.assertEqual(self.job.contractor, self.contractor)
                self.assertEqual(self.job.status, finished_status)
                self.assertEqual(self.job.comments, finished_comments)
