import datetime
from urllib.parse import urlencode

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from trades.factories import TradeFactory
from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import (
    LOGIN_NECESSITY_MESSAGE,
    LOGIN_SUCCESS_MESSAGE,
    LOGOUT_SUCCESS_MESSAGE,
    PASSWORD_STRONG,
    REGISTER_SUCCESS_MESSAGE,
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

    def test_post_should_create_an_user(self):
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
            self, response, response_messages, REGISTER_SUCCESS_MESSAGE
        )
        self.assertTrue(User.objects.filter(email=self.email).exists())


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
        cls.user = UserFactory.create()

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
        cls.user = UserFactory.create()

    def setUp(self):
        self.client = Client()

    def test_get_not_logged_in_user_cannot_enter(self):
        # Act
        response = self.client.get(self.url)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        _assert_redirects_and_response_messages(
            self, response, response_messages, LOGIN_NECESSITY_MESSAGE, "info"
        )

    def test_get_logged_in_user_can_enter(self):
        # Arrange
        self.client.force_login(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)


class TestUsersAll(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("users-all")
        cls.user = UserFactory.create()

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

    def test_users_all_pagination(self):
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
