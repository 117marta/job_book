from urllib.parse import urlencode

from django.test import Client, TestCase
from django.urls import reverse

from jobs.consts import JOBS_PER_PAGE
from jobs.models import Job
from jobs.tests.factories import JobFactory
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
