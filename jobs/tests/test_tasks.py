import datetime
from unittest.mock import patch

from django.test import TestCase
from freezegun import freeze_time
from parameterized import parameterized

from jobs.consts import (
    EMAIL_JOB_UPCOMING_DEADLINE_CONTENT,
    EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT,
    JobStatuses,
)
from jobs.tasks import jobs_upcoming_deadline_contractor
from jobs.tests.factories import JobFactory


class TestJobsTasks(TestCase):
    @parameterized.expand(
        [
            ("2024-11-06", JobStatuses.MAKING_DOCUMENTS, True),
            ("2024-11-06", JobStatuses.FINISHED, False),
            ("2024-11-05", JobStatuses.ONGOING, False),
            ("2024-11-05", JobStatuses.CLOSED, False),
        ]
    )
    @patch("jobs.tasks.send_email_with_celery")
    def test_jobs_upcoming_deadline_contractor(self, deadline, status, send_email, mock_email):
        """
        Tests if the Contractor of the job gets an e-mail about deadline one day earlier.
        """
        # Assert
        job = JobFactory.create(
            deadline=datetime.datetime.strptime(deadline, "%Y-%m-%d").date(), status=status
        )

        # Act
        with freeze_time("2024-11-05"):
            jobs_upcoming_deadline_contractor()

        # Assert
        if send_email:
            mock_email.assert_called_once_with(
                user_pk=job.contractor.pk,
                subject=EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT.format(job.pk),
                content=EMAIL_JOB_UPCOMING_DEADLINE_CONTENT.format(job.pk),
            )
        else:
            mock_email.assert_not_called()
