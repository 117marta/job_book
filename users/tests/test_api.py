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
    """
    Test module for GET all user API.
    """

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
    """
    Test module for inserting a new user.
    """

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


class TestUserDetailsAPI(TestCase):
    """
    Test module for getting, updating and deleting an existing user record.
    """

    @classmethod
    def setUpTestData(cls):
        cls.email = "test_email@example.org"
        cls.user1 = UserFactory.create(email=cls.email)
        cls.invalid_pk = 13
        cls.valid_payload = {
            "first_name": "New Name",
            "phone": "111222333",
        }
        cls.invalid_payload = {
            "first_name": "",
            "email": "invalid_email@example",
            "trades": [cls.invalid_pk],
            "role": "example_role",
            "birth_date": "1994/12/16",
        }
        cls.url = reverse("api-user-details", kwargs={"pk": cls.user1.pk})
        cls.url_invalid = reverse("api-user-details", kwargs={"pk": cls.invalid_pk})

    def setUp(self):
        self.client = APIClient()

    def test_get_single_user(self):
        # Act
        response = self.client.get(self.url)
        user = User.objects.get(pk=self.user1.pk)
        serializer = UsersSerializer(user)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_user_invalid(self):
        # Act
        response = self.client.get(self.url_invalid)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_single_user(self):
        # Act
        response = self.client.delete(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_single_user_invalid(self):
        # Act
        response = self.client.delete(self.url_invalid)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_single_user(self):
        # Act
        response = self.client.put(
            path=self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(pk=self.user1.pk)
        self.assertEqual(user.first_name, self.valid_payload["first_name"])
        self.assertEqual(user.phone, self.valid_payload["phone"])
        self.assertEqual(user.email, self.email)

    def test_put_single_user_invalid(self):
        # Arrange
        expected_errors = [
            ("first_name", "This field may not be blank."),
            ("email", "Enter a valid email address."),
            ("role", '"example_role" is not a valid choice.'),
            ("trades", f'Invalid pk "{self.invalid_pk}" - object does not exist.'),
            ("birth_date", "Date has wrong format. use one of these formats instead: yyyy-mm-dd."),
        ]

        # Act
        response = self.client.put(
            path=self.url,
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = [(k, v[0].capitalize()) for k, v in response.data.items()]
        self.assertEqual(expected_errors, errors)
        user = User.objects.get(pk=self.user1.pk)
        self.assertEqual(user.first_name, self.user1.first_name)
        self.assertEqual(user.email, self.user1.email)
