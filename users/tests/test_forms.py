import datetime

from django.test import Client, TestCase
from freezegun import freeze_time
from parameterized import parameterized

from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import (
    BIRTH_DATE_FORM_ERROR,
    PASSWORD_FORM_MATCH_ERROR,
    PASSWORD_FORM_NUMERIC_ERROR,
    PASSWORD_NUMERIC,
    PASSWORD_STRONG,
)
from users.forms import RegistrationForm
from users.models import SITE_MANAGER, User


class TestUserRegistrationForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "email@test.com"
        cls.data = {
            "phone": "123123123",
            "role": SITE_MANAGER,
            "trade": Trade.objects.all().values_list("pk", flat=True),
            "email": cls.email,
            "password1": PASSWORD_STRONG,
            "password2": PASSWORD_STRONG,
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

    @parameterized.expand([("2010, 10, 10", False), ("1995, 05, 05", True)])
    def test_registration_birth_date(self, fake_date, is_valid):
        """
        Check if the test will pass depending on the fake date of birth.
        """
        # Arrange
        expected_errors = {"birth_date": [BIRTH_DATE_FORM_ERROR]}

        # Act
        with freeze_time(fake_date):
            form = RegistrationForm(data=self.data)
            self.data["birth_date"] = datetime.date.today()

        # Assert
        if is_valid:
            self.assertTrue(form.is_valid())
        else:
            self.assertFalse(form.is_valid())
            self.assertEqual(expected_errors, form.errors)

    @parameterized.expand(
        [
            ("Of$KxIgL8i", "Of$KxIgL8", False),
            (PASSWORD_NUMERIC, PASSWORD_NUMERIC, False),
            (PASSWORD_STRONG, PASSWORD_STRONG, True),
        ]
    )
    def test_registration_password(self, password1, password2, is_valid):
        """
        Test different cases of passwords combinations.
        """
        # Arrange
        if password1 != password2:
            expected_errors = {"__all__": [PASSWORD_FORM_MATCH_ERROR]}
        else:
            expected_errors = {"__all__": [PASSWORD_FORM_NUMERIC_ERROR]}

        # Act
        form = RegistrationForm(data=self.data)
        self.data["password1"] = password1
        self.data["password2"] = password2

        # Assert
        if is_valid:
            self.assertTrue(form.is_valid())
        else:
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


class TestUserLoginForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "email_login@test.com"

    def setUp(self):
        self.client = Client()

    @parameterized.expand(
        [
            (PASSWORD_STRONG, True),
            (PASSWORD_NUMERIC, False),
        ]
    )
    def test_login_form(self, password, is_valid):
        # Arrange
        self.user = User.objects.create(email=self.email)
        self.user.set_password(password)
        self.user.save()

        # Act
        user_login = self.client.login(email=self.email, password=PASSWORD_STRONG)

        # Assert
        if is_valid:
            self.assertTrue(user_login)
        else:
            self.assertFalse(user_login)
