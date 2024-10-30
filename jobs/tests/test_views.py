import datetime
from unittest import mock
from urllib.parse import urlencode

from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from parameterized import parameterized

from jobs.consts import (
    EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT,
    EMAIL_JOB_CHANGE_STATUS_SUBJECT,
    EMAIL_JOB_CREATE_SUBJECT,
    JOB_CREATE_SUCCESS_MESSAGE,
    JOB_SAVE_SUCCESS_MESSAGE,
    JobKinds,
    JOBS_PER_PAGE,
    JobStatuses,
)
from jobs.models import Job
from jobs.tests.factories import JobFactory
from trades.factories import TradeFactory
from users.models import SITE_MANAGER, SURVEYOR
from users.tests.factories import UserFactory


class TestJobsAll(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("jobs-all")
        cls.user = UserFactory.create(is_active=True)

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        # Act
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?{urlencode({'next': self.url})}"

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_get_logged_in_user_can_enter(self):
        # Arrange
        self.client.force_login(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_jobs_all_pagination(self):
        # Arrange
        self.client.force_login(user=self.user)
        jobs_count = JOBS_PER_PAGE + 1
        JobFactory.create_batch(size=jobs_count)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["paginator"].count, jobs_count)
        self.assertEqual(Job.objects.count(), jobs_count)
        self.assertEqual(response.context["paginator"].num_pages, 2)


class TestJobsCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("jobs-create")
        cls.principal = UserFactory.create(is_active=True, role=SITE_MANAGER)
        cls.surveyor = UserFactory.create(is_active=True, role=SURVEYOR)
        cls.trade = TradeFactory.create()

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        """
        Not logged-in user is not allowed to enter the page.
        """
        # Act
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?{urlencode({'next': self.url})}"

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_get_logged_in_user_can_enter(self):
        """
        Logged-in user is allowed to enter the page.
        """
        # Arrange
        self.client.force_login(user=self.principal)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_create_a_job_and_send_an_email(self):
        """
        Logged-in user can create a new job and e-mail is sent to the contractor of this job.
        """
        # Arrange
        self.client.force_login(user=self.principal)
        data = {
            "principal": self.principal.pk,
            "contractor": self.surveyor.pk,
            "kind": JobKinds.STAKING,
            "trade": self.trade.pk,
            "description": "Please stake the track axis out.",
            "km_from": "19.000",
            "km_to": "19.750",
            "deadline": datetime.date.today() + datetime.timedelta(days=3),
            "comments": "On-site contact with Jan Kowalski: 500600700",
        }

        # Act
        response = self.client.post(path=self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("jobs-all"))
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(JOB_CREATE_SUCCESS_MESSAGE, response_messages[0].message)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, EMAIL_JOB_CREATE_SUBJECT)


class TestJobView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.principal = UserFactory.create(is_active=True, role=SITE_MANAGER)
        cls.contractor = UserFactory.create(is_active=True, role=SURVEYOR)
        cls.new_contractor = UserFactory.create(
            first_name="Ryszard", last_name="Świtaj", is_active=True, role=SURVEYOR
        )
        cls.job = JobFactory.create(
            principal=cls.principal,
            contractor=cls.contractor,
            kind=JobKinds.STAKING,
            status=JobStatuses.MAKING_DOCUMENTS,
        )
        cls.url = reverse("jobs-job", kwargs={"job_pk": cls.job.pk})

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        """
        Not logged-in user is not allowed to enter the page.
        """
        # Act
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?{urlencode({'next': self.url})}"

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    @parameterized.expand(["contractor", "new_contractor"])
    def test_get_check_if_the_fields_are_editable(self, contractor_type):
        """
        If user is not a Principal or the Contractor of the Job, all the fields should be disabled.
        If user is a Principal or the Contractor of the Job, the contractor, status and comments should be editable.
        """
        # Arrange
        contractor = getattr(self, contractor_type)
        self.client.force_login(user=contractor)

        # Act
        response = self.client.get(path=self.url)
        form = response.context["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        match contractor_type:
            case "contractor":
                self.assertNotIn("disabled", form["contractor"].as_text())
                self.assertNotIn("disabled", form["status"].as_text())
                self.assertNotIn("disabled", form["comments"].as_textarea())
            case "new_contractor":
                self.assertIn("disabled", form["contractor"].as_text())
                self.assertIn("disabled", form["status"].as_text())
                self.assertIn("disabled", form["comments"].as_textarea())

    @mock.patch("jobs.views.send_email_with_celery")
    def test_update_a_job_and_send_emails(self, mock_email):
        """
        Contractor changes the job status, person assigned to this job and adds a comment.
        """
        # Arrange
        self.client.force_login(user=self.contractor)
        data = {
            "contractor": self.new_contractor.pk,
            "status": JobStatuses.READY_TO_STAKE_OUT,
            "comments": "I am changing this job to the Ryszard Świtaj and give a new status",
        }

        # Act
        response = self.client.post(path=self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))
        job = Job.objects.last()

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("jobs-all"))
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(JOB_SAVE_SUCCESS_MESSAGE, response_messages[0].message)
        self.assertEqual(job.contractor, self.new_contractor)
        self.assertEqual(job.status, JobStatuses.READY_TO_STAKE_OUT)
        self.assertEqual(job.comments, data["comments"])

        mock_email.delay.assert_has_calls(
            [
                # Change status -> e-mail to the Principal
                mock.call(
                    user_pk=self.principal.pk,
                    template_name="users/email.html",
                    subject=EMAIL_JOB_CHANGE_STATUS_SUBJECT.format(self.job.pk),
                    content=mock.ANY,
                ),
                # Change Contractor -> e-mail to the new Contractor
                mock.call(
                    user_pk=self.new_contractor.pk,
                    template_name="users/email.html",
                    subject=EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT.format(self.job.pk),
                    content=mock.ANY,
                ),
            ]
        )


class TestMyJobsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.principal = UserFactory.create(is_active=True)
        cls.contractor = UserFactory.create(is_active=True)
        JobFactory.create(principal=cls.principal, status=JobStatuses.WAITING)
        JobFactory.create(principal=cls.principal, status=JobStatuses.WAITING)
        JobFactory.create(principal=cls.principal, status=JobStatuses.ACCEPTED)
        JobFactory.create(principal=cls.principal, status=JobStatuses.DATA_PASSED)
        JobFactory.create(principal=cls.principal, status=JobStatuses.DATA_PASSED)
        JobFactory.create(principal=cls.principal, status=JobStatuses.DATA_PASSED)
        JobFactory.create(principal=cls.principal, status=JobStatuses.FINISHED)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.WAITING)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.REFUSED)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.MAKING_DOCUMENTS)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.MAKING_DOCUMENTS)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.READY_TO_STAKE_OUT)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.DATA_PASSED)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.ONGOING)
        JobFactory.create(contractor=cls.contractor, status=JobStatuses.CLOSED)
        JobFactory.create(
            principal=cls.principal, contractor=cls.contractor, status=JobStatuses.ONGOING
        )
        JobFactory.create(
            principal=cls.principal, contractor=cls.contractor, status=JobStatuses.MAKING_DOCUMENTS
        )
        cls.url = reverse("jobs-my-jobs")

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        """
        Not logged-in user is not allowed to enter the page.
        """
        # Act
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?{urlencode({'next': self.url})}"

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_get_user_see_no_jobs(self):
        """
        The user does not see the jobs until he/she selects a role.
        """
        # Arrange
        self.client.force_login(user=self.principal)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("jobs", response.context)

    @parameterized.expand(
        [
            ("principal", None, 2),
            ("principal", "waiting", 2),
            ("principal", "accepted", 1),
            ("principal", "refused", 0),
            ("principal", "making_documents", 1),
            ("principal", "ready_to_stake_out", 0),
            ("principal", "data_passed", 3),
            ("principal", "ongoing", 1),
            ("principal", "finished", 1),
            ("principal", "closed", 0),
            ("contractor", None, 1),
            ("contractor", "waiting", 1),
            ("contractor", "accepted", 0),
            ("contractor", "refused", 1),
            ("contractor", "making_documents", 3),
            ("contractor", "ready_to_stake_out", 1),
            ("contractor", "data_passed", 1),
            ("contractor", "ongoing", 2),
            ("contractor", "finished", 0),
            ("contractor", "closed", 1),
        ]
    )
    def test_get_user_see_waiting_jobs(self, role, status, count):
        """
        After the user chose a role - the jobs are visible.
        The jobs are filtered by the role (principal/contractor) and also by the status.
        """
        # Arrange
        user = getattr(self, role)
        self.client.force_login(user=user)
        session = self.client.session
        session.update({"role": role})
        session.save()

        # Act
        if status:
            response = self.client.get(reverse("jobs-my-jobs", kwargs={"status": status}))
        else:
            response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("jobs", response.context)
        self.assertEqual(response.context["jobs"].count(), count)
