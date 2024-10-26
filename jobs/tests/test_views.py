import datetime
from urllib.parse import urlencode

from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from jobs.consts import (
    EMAIL_JOB_CREATE_SUBJECT,
    JOB_CREATE_SUCCESS_MESSAGE,
    JobKinds,
    JOBS_PER_PAGE,
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

        # Arrange
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("jobs-all"))
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(JOB_CREATE_SUCCESS_MESSAGE, response_messages[0].message)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, EMAIL_JOB_CREATE_SUBJECT)
