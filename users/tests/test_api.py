from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
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
