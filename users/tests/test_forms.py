from django.test import TestCase

from trades.models import ABBREVIATION_RAILWAY, Trade
from users.models import SITE_MANAGER, User
from users.forms import RegistrationForm


class TestUserRegistrationForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "email_existing@test.com"
        cls.data = {
            "phone": "123123123",
            "role": SITE_MANAGER,
            "trade": Trade.objects.all().values_list("pk", flat=True),
            "email": cls.email,
            "password1": "123",
            "password2": "123",
        }
        Trade.objects.create(
            name="Test Name", abbreviation=ABBREVIATION_RAILWAY, description="Test Description"
        )

    def test_registration_empty_data(self):
        """
        Test should fail, because empty data is sent.
        """
        # Arrange
        expected_errors = {
            "phone": ["This field is required."],
            "role": ["This field is required."],
            "trade": ["This field is required."],
            "email": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
        }
        # Act
        form = RegistrationForm(data={})

        # Assert
        self.assertFalse(form.is_valid())
        self.assertEqual(expected_errors, form.errors)

    def test_registration_existing_email(self):
        """
        Test should fail, because user with the given email already exists.
        """
        # Arrange
        User.objects.create_user(email=self.email)
        expected_errors = {"email": ["User with this Email address already exists."]}

        # Act
        form = RegistrationForm(data=self.data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertEqual(expected_errors, form.errors)

    def test_registration_correct_data(self):
        """
        Test should pass, because the correct data is sent.
        """
        # Arrange
        self.data["email"] = "email_other@test.com"

        # Act
        form = RegistrationForm(data=self.data)

        # Assert
        self.assertTrue(form.is_valid())
