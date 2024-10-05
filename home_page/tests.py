from django.test import TestCase, Client
from django.urls import reverse


class TestHomePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("home-page")

    def setUp(self):
        self.client = Client()

    def test_get_should_return_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
