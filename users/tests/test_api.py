import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from trades.factories import TradeFactory
from users.const import PASSWORD_STRONG
from users.models import CLERK_OF_THE_WORKS, User
from users.serializers import UsersSerializer
from users.tests.factories import UserFactory


class TestUserAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.url = reverse("api-get-users")

    def setUp(self):
        self.client = APIClient()

    def test_get_user(self):
        # Arrange
        users = User.objects.all()
        serializer = UsersSerializer(users, many=True)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestCreateUserAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trade = TradeFactory()
        cls.valid_payload = {
            "first_name": "User",
            "last_name": "Valid",
            "email": "user_valid@example.org",
            "role": CLERK_OF_THE_WORKS,
            "phone": "123123123",
            "password": PASSWORD_STRONG,
            "trades": [
                cls.trade.pk,
            ],
        }

        cls.invalid_payload = {
            "first_name": "User",
            "role": CLERK_OF_THE_WORKS,
            "phone": "123456789",
            "password": PASSWORD_STRONG,
            "trades": [
                5,
            ],
        }
        cls.url = reverse("api-create-user")

    def setUp(self):
        self.client = APIClient()

    def test_post_valid_user(self):
        # Act
        response = self.client.post(
            self.url, data=json.dumps(self.valid_payload), content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_user(self):
        # Arrange
        expected_fields_error = ["last_name", "email", "trades"]

        # Act
        response = self.client.post(
            self.url, data=json.dumps(self.invalid_payload), content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual([*response.data], expected_fields_error)
