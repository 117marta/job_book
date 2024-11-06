import datetime
from unittest.mock import patch

from django.test import TestCase
from freezegun import freeze_time

from jobs.consts import EMAIL_JOB_UPCOMING_DEADLINE_CONTENT, EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT
from jobs.tasks import jobs_upcoming_contractor
from jobs.tests.factories import JobFactory


class TestJobsTasks(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job = JobFactory(deadline=datetime.date(2024, 11, 6))

    @freeze_time("2022-11-05")
    @patch("jobs.tasks.send_email_with_celery")
    def test_jobs_upcoming_contractor(self, mock_email):
        """
        Tests if the Contractor of the job gets an e-mail about deadline one day earlier.
        """
        # Act
        jobs_upcoming_contractor()

        # Assert
        mock_email.assert_called_once_with(
            user_pk=self.job.contractor.pk,
            template_name="users/email.html",
            subject=EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT.format(self.job.pk),
            content=EMAIL_JOB_UPCOMING_DEADLINE_CONTENT.format(self.job.pk),
        )
