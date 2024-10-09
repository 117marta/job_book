import datetime

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from trades.factories import TradeFactory
from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import LOGIN_SUCCESS_MESSAGE, PASSWORD_STRONG, REGISTER_SUCCESS_MESSAGE
from users.models import SITE_MANAGER, User


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
            "trade": Trade.objects.all().values_list("pk", flat=True),
            "birth_date": datetime.date(1964, 6, 3),
            "email": self.email,
            "password1": PASSWORD_STRONG,
            "password2": PASSWORD_STRONG,
        }

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home-page"))
        self.assertTrue(User.objects.filter(email=self.email).exists())
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(REGISTER_SUCCESS_MESSAGE, response_messages[0].message)


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
        User.objects.create_user(self.email, PASSWORD_STRONG)

        # Act
        response = self.client.post(self.url, data=data)
        response_messages = list(get_messages(response.wsgi_request))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home-page"))
        self.assertEqual(len(response_messages), 1)
        self.assertIn("success", response_messages[0].tags)
        self.assertEqual(LOGIN_SUCCESS_MESSAGE, response_messages[0].message)
