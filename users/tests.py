from django.test import TestCase, Client
from django.urls import reverse
import datetime

from trades.models import ABBREVIATION_RAILWAY, Trade
from users.models import SITE_MANAGER, User


class TestUserRegistration(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("registration")
        cls.email = "email_registration@test.pl"
        cls.password = "password123"
        Trade.objects.create(
            name="Test Name", abbreviation=ABBREVIATION_RAILWAY, description="Test Description"
        )

    def setUp(self):
        self.client = Client()

    def test_get_should_return_200(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_get_should_create_an_user(self):
        # Arrange
        data = {
            "first_name": "Genowefa",
            "last_name": "Nowakowska",
            "phone": "123123123",
            "role": SITE_MANAGER,
            "trade": Trade.objects.all().values_list("pk", flat=True),
            "birth_date": datetime.date(1964, 6, 3),
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
        }

        # Act
        response = self.client.post(self.url, data=data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home-page"))
        self.assertTrue(User.objects.filter(email=self.email).exists())
