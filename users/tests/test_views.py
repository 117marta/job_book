import datetime
from urllib.parse import urlencode

from django.contrib.messages import get_messages
from django.core import mail
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from jobs.consts import JobStatuses
from jobs.tests.factories import JobFactory
from trades.factories import TradeFactory
from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import (
    ADMIN_NECESSITY_MESSAGE,
    EMAIL_ACCEPTANCE_SUBJECT,
    EMAIL_REGISTRATION_SUBJECT,
    LOGIN_NECESSITY_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    PASSWORD_STRONG,
    REGISTRATION_SUCCESS_MESSAGE,
    USERS_ACCEPTED,
    USERS_DELETED,
    USERS_OBJECTS_PER_PAGE,
)
from users.models import SITE_MANAGER, User
from users.tests.factories import UserFactory


def _assert_redirects_and_response_messages(
    self, response, response_messages, message_txt, alert="success"
):
    self.assertEqual(response.status_code, 302)
    self.assertRedirects(response, reverse("home-page"))
    self.assertEqual(len(response_messages), 1)
    self.assertIn(alert, response_messages[0].tags)
    self.assertEqual(message_txt, response_messages[0].message)


class TestUserRegistration(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("registration")
        cls.email = "email_registration@test.pl"
        TradeFactory.create(abbreviation=ABBREVIATION_RAILWAY)

    def setUp(self):
        self.client = Client()

    def test_get_should_return_200(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_should_create_an_user_and_send_an_email(self):
        # Arrange
        data = {
            "first_name": "Genowefa",
            "last_name": "Nowakowska",
            "phone": "123123123",
            "role": SITE_MANAGER,
            "trades": Trade.objects.all().values_list("pk", flat=True),
            "birth_date": datetime.date(1964, 6, 3),
            "email": self.email,
            "password1": PASSWORD_STRONG,
            "password2": PASSWORD_STRONG,
            "is_active": True,
        }

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        _assert_redirects_and_response_messages(
            self, response, response_messages, REGISTRATION_SUCCESS_MESSAGE
        )
        self.assertTrue(User.objects.filter(email=self.email).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, EMAIL_REGISTRATION_SUBJECT)


class TestUserLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("login")
        cls.email = "email_login@test.pl"

    def setUp(self):
        self.client = Client()

    def test_get_should_return_200(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_post_should_log_in_an_user(self):
        # Arrange
        data = {
            "email": self.email,
            "password": PASSWORD_STRONG,
        }
        User.objects.create_user(email=self.email, password=PASSWORD_STRONG, is_active=True)

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        _assert_redirects_and_response_messages(
            self, response, response_messages, LOGIN_SUCCESS_MESSAGE
        )


class TestUserLogout(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("logout")
        cls.user = UserFactory.create(is_active=True)

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_log_out(self):
        # Act
        response = self.client.get(self.url)
        redirect_url = f"{reverse('login')}?{urlencode({'next': self.url})}"

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_get_logged_in_user_can_log_out(self):
        # Arrange
        self.client.force_login(user=self.user)

        # Act
        response = self.client.get(self.url)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        _assert_redirects_and_response_messages(
            self, response, response_messages, LOGOUT_SUCCESS_MESSAGE, "success"
        )
        self.user.refresh_from_db()
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestUserPanel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("panel")
        cls.user = UserFactory.create(is_active=True)

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        """
        Not logged-in user is not allowed to enter the page.
        """
        # Act
        response = self.client.get(self.url)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        _assert_redirects_and_response_messages(
            self, response, response_messages, LOGIN_NECESSITY_MESSAGE, "info"
        )

    def test_get_logged_in_user_can_enter(self):
        """
        Logged-in user is allowed to enter the page.
        """
        # Arrange
        self.client.force_login(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_get_jobs_statistics(self):
        """
        Check if the statistics displays the correct number of jobs depending on the role.
        """
        # Arrange
        self.client.force_login(user=self.user)
        JobFactory.create(principal=self.user, status=JobStatuses.WAITING)
        JobFactory.create(principal=self.user, status=JobStatuses.ACCEPTED)
        JobFactory.create(principal=self.user, status=JobStatuses.ACCEPTED)
        JobFactory.create(principal=self.user, status=JobStatuses.READY_TO_STAKE_OUT)
        JobFactory.create(principal=self.user, status=JobStatuses.DATA_PASSED)
        JobFactory.create(principal=self.user, status=JobStatuses.CLOSED)
        JobFactory.create(contractor=self.user, status=JobStatuses.WAITING)
        JobFactory.create(contractor=self.user, status=JobStatuses.REFUSED)
        JobFactory.create(contractor=self.user, status=JobStatuses.CLOSED)
        expected_stats = {
            "principal": {
                "all": 6,
                "statuses": {
                    "waiting": 1,
                    "accepted": 2,
                    "refused": 0,
                    "making documents": 0,
                    "ready to stake out": 1,
                    "data passed": 1,
                    "ongoing": 0,
                    "finished": 0,
                    "closed": 1,
                },
            },
            "contractor": {
                "all": 3,
                "statuses": {
                    "waiting": 1,
                    "accepted": 0,
                    "refused": 1,
                    "making documents": 0,
                    "ready to stake out": 0,
                    "data passed": 0,
                    "ongoing": 0,
                    "finished": 0,
                    "closed": 1,
                },
            },
        }

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.context["jobs_statistics"], expected_stats)


class TestUsersAll(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("users-all")
        cls.user = UserFactory.create(is_active=True)

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
        self.client.force_login(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_users_all_pagination(self):
        """
        Checks if a page is divided into smaller pages based on the USERS_OBJECTS_PER_PAGE.
        """
        # Arrange
        self.client.force_login(user=self.user)
        UserFactory.create_batch(size=20)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["paginator"].count, User.objects.count(), USERS_OBJECTS_PER_PAGE + 1
        )
        self.assertEqual(response.context["paginator"].num_pages, 2)


class TestAcceptOrDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("accept-or-delete")
        cls.user_admin = UserFactory.create(is_active=True, is_admin=True)
        cls.user_active = UserFactory.create(is_active=True)
        UserFactory.create_batch(3)

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

    def test_get_not_admin_user_cannot_enter(self):
        """
        Logged-in user is not allowed to enter the page.
        """
        # Arrange
        self.client.force_login(user=self.user_active)

        # Act
        response = self.client.get(self.url)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home-page"))
        self.assertEqual(len(response_messages), 1)
        self.assertIn("danger", response_messages[0].tags)
        self.assertEqual(ADMIN_NECESSITY_MESSAGE, response_messages[0].message)

    def test_get_admin_user_can_enter(self):
        """
        An admin user is allowed to enter the page.
        """
        # Arrange
        self.client.force_login(user=self.user_admin)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_action_accept_should_accept_users_and_send_an_email(self):
        """
        An admin user can accept an inactive users. After this action an e-mail is sent.
        """
        # Arrange
        self.client.force_login(user=self.user_admin)
        users_count = User.objects.count()
        users_to_accept = User.objects.filter(is_active=False).values_list("pk", flat=True)
        data = {"action_checkbox": users_to_accept, "action_accept": [""]}

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(
            USERS_ACCEPTED.format(users_to_accept.count()), response_messages[0].message
        )
        self.assertEqual(User.objects.filter(is_active=True).count(), users_count)
        self.assertEqual(len(mail.outbox), users_to_accept.count())
        self.assertEqual(set([mail.subject for mail in mail.outbox]), {EMAIL_ACCEPTANCE_SUBJECT})

    def test_post_action_delete_should_delete_users(self):
        """
        An admin user can delete an inactive users. After this action an e-mail is sent.
        """
        # Arrange
        self.client.force_login(user=self.user_admin)
        users_count = User.objects.count()
        users_to_delete = User.objects.values_list("pk", flat=True)[:2]
        data = {"action_checkbox": users_to_delete, "action_delete": [""]}

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_messages), 1)
        self.assertIn("danger", response_messages[0].tags)
        self.assertEqual(
            USERS_DELETED.format(users_to_delete.count()), response_messages[0].message
        )
        self.assertEqual(User.objects.count(), users_count - users_to_delete.count())
