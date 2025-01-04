import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.test.utils import override_settings

from jobs.consts import JobKinds, JobStatuses
from jobs.management.commands.jobs_monthly_status import Command
from jobs.tests.factories import JobFactory


class TestMonthlyStatus(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = datetime.datetime.now()
        cls.last_month = cls.today - relativedelta(months=1)
        cls.job_1 = JobFactory.create(status=JobStatuses.WAITING, kind=JobKinds.STAKING)
        cls.job_2 = JobFactory.create(status=JobStatuses.WAITING, kind=JobKinds.INVENTORY)
        cls.job_3 = JobFactory.create(status=JobStatuses.ACCEPTED, kind=JobKinds.INVENTORY)
        cls.job_4 = JobFactory.create(status=JobStatuses.MAKING_DOCUMENTS, kind=JobKinds.OTHER)
        cls.job_5 = JobFactory.create(status=JobStatuses.ONGOING, kind=JobKinds.OTHER)
        cls.job_6 = JobFactory.create(status=JobStatuses.FINISHED, kind=JobKinds.STAKING)

    @patch("jobs.management.commands.jobs_monthly_status.Command.export_csv")
    def test_export_csv(self, mock_file):
        # Arrange
        with override_settings(USE_TZ=False):
            self.job_1.created = self.last_month
            self.job_1.save()
            self.job_2.created = self.last_month
            self.job_2.save()
            self.job_3.created = self.last_month
            self.job_3.save()
            self.job_4.created = self.last_month
            self.job_4.save()
            self.job_6.created = self.last_month
            self.job_6.save()
        last_month_formatted = self.last_month.strftime("%d.%m.%Y")
        expected_call = [
            (
                self.job_1.pk,
                last_month_formatted,
                JobStatuses.WAITING.value,
                JobKinds.STAKING.value,
                False,
            ),
            (
                self.job_2.pk,
                last_month_formatted,
                JobStatuses.WAITING.value,
                JobKinds.INVENTORY.value,
                False,
            ),
            (
                self.job_3.pk,
                last_month_formatted,
                JobStatuses.ACCEPTED.value,
                JobKinds.INVENTORY.value,
                False,
            ),
            (
                self.job_4.pk,
                last_month_formatted,
                JobStatuses.MAKING_DOCUMENTS.value,
                JobKinds.OTHER.value,
                False,
            ),
            (
                self.job_6.pk,
                last_month_formatted,
                JobStatuses.FINISHED.value,
                JobKinds.STAKING.value,
                False,
            ),
            ["Number of jobs:", 5],
            (
                [
                    "waiting",
                    "accepted",
                    "refused",
                    "making_documents",
                    "ready_to_stake_out",
                    "data_passed",
                    "ongoing",
                    "finished",
                    "closed",
                ]
            ),
            ([2, 1, 0, 1, 0, 0, 0, 1, 0]),
            (["staking", "inventory", "other"]),
            ([2, 2, 1]),
        ]

        # Act
        Command().handle()

        # Assert
        mock_file.assert_called_with(expected_call)
