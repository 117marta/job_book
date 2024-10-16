import datetime
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from django.test import Client, TestCase
from freezegun import freeze_time
from parameterized import parameterized
from PIL import Image

from trades.factories import TradeFactory
from trades.models import ABBREVIATION_RAILWAY
from users.const import (
    AVATAR_DIMENSION_ERROR,
    AVATAR_MAX_DIMENSION,
    AVATAR_SIZE_ERROR,
    AVATAR_TYPE_ERROR,
    BIRTH_DATE_FORM_ERROR,
    PASSWORD_FORM_MATCH_ERROR,
    PASSWORD_FORM_NUMERIC_ERROR,
    PASSWORD_NUMERIC,
    PASSWORD_STRONG,
)
from users.forms import AcceptOrDeleteForm, RegistrationForm
from users.models import SITE_MANAGER, User
from users.tests.factories import UserFactory


class TestUserRegistrationForm(TestCase):
    correct_dimensions = (100, 100)
    correct_size = 1024 * 1024
    incorrect_dimensions = (700, 700)
    incorrect_size = correct_size * 5

    @classmethod
    def setUpTestData(cls):
        cls.trade = TradeFactory.create(abbreviation=ABBREVIATION_RAILWAY)
        cls.email = "email@test.com"
        cls.data = {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone": "123123123",
            "role": SITE_MANAGER,
            "trades": [cls.trade.pk],
            "email": cls.email,
            "password1": PASSWORD_STRONG,
            "password2": PASSWORD_STRONG,
            "is_active": True,
        }

    @staticmethod
    def _create_temporary_avatar(file_format, dimensions, file_size):
        file = BytesIO()
        image = Image.new("RGB", dimensions)
        image.save(fp=file, format=file_format)
        file.seek(0)

        image_file = InMemoryUploadedFile(
            file=file,
            field_name=None,
            name=f"test_image.{file_format}",
            content_type=file_format,
            size=file_size,
            charset=None,
        )
        return image_file

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

    def test_registration_empty_data(self):
        """
        Test should fail, because empty data is sent.
        """
        # Arrange
        expected_errors = {
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "phone": ["This field is required."],
            "role": ["This field is required."],
            "trades": ["This field is required."],
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

    @parameterized.expand(
        [
            ("JPEG", correct_dimensions, correct_size, True),
            ("JPEG", correct_dimensions, incorrect_size, False),
            ("JPEG", incorrect_dimensions, correct_size, False),
            ("JPEG", incorrect_dimensions, incorrect_size, False),
            ("PNG", correct_dimensions, correct_size, True),
            ("PNG", correct_dimensions, incorrect_size, False),
            ("PNG", incorrect_dimensions, correct_size, False),
            ("PNG", incorrect_dimensions, incorrect_size, False),
            ("GIF", correct_dimensions, correct_size, False),
            ("PDF", correct_dimensions, correct_size, False),
        ]
    )
    def test_registration_avatar(self, file_format, file_dimensions, file_size, is_valid):
        """
        Test different cases of avatar format, dimensions and size combinations.
        """
        # Arrange
        avatar = self._create_temporary_avatar(
            file_format=file_format, dimensions=file_dimensions, file_size=file_size
        )

        if file_format == "GIF":
            expected_errors = {"avatar": [AVATAR_TYPE_ERROR]}
        elif file_format == "PDF":
            expected_errors = {
                "avatar": [
                    "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
                ]
            }
        else:
            if file_dimensions != self.correct_dimensions:
                expected_errors = {
                    "avatar": [AVATAR_DIMENSION_ERROR.format(max_dimension=AVATAR_MAX_DIMENSION)]
                }
            if file_size != self.correct_size:
                expected_errors = {"avatar": [AVATAR_SIZE_ERROR]}

        # Act
        form = RegistrationForm(data=self.data, files={"avatar": avatar})

        # Assert
        if is_valid:
            self.assertTrue(form.is_valid())
        else:
            self.assertFalse(form.is_valid())
            self.assertEqual(expected_errors, form.errors)


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
        self.user = User.objects.create(email=self.email, is_active=True)
        self.user.set_password(PASSWORD_STRONG)
        self.user.save()

        # Act
        user_login = self.client.login(email=self.email, password=password)

        # Assert
        if is_valid:
            self.assertTrue(user_login)
        else:
            self.assertFalse(user_login)


class TestAcceptOrDeleteForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory.create(is_active=True)
        UserFactory.create_batch(4)

    @parameterized.expand(
        [
            ("action_accept", "all"),
            ("action_accept", 2),
            ("action_delete", "all"),
            ("action_delete", 2),
        ],
    )
    def test_accept_or_delete(self, action, users_count):
        # Arrange
        users_to_action = User.objects.filter(is_active=False).values_list("pk", flat=True)
        if users_count != "all":
            users_to_action = users_to_action[:users_count]
        data = {"action_checkbox": users_to_action, action: [""]}

        # Act
        form = AcceptOrDeleteForm(data=data)
        if action == "action_accept":
            form.accept_users(users_to_action)
        else:
            form.delete_users(users_to_action)

        # Assert
        self.assertTrue(form.is_valid())
        if users_count == "all":
            if action == "action_accept":
                self.assertEqual(User.objects.filter(is_active=True).count(), 5)
                self.assertEqual(User.objects.filter(is_active=False).count(), 0)
            else:
                self.assertEqual(User.objects.filter(is_active=True).count(), 1)
                self.assertEqual(User.objects.filter(is_active=False).count(), 0)
        else:
            if action == "action_accept":
                self.assertEqual(User.objects.filter(is_active=True).count(), 3)
                self.assertEqual(User.objects.filter(is_active=False).count(), 2)
            else:
                self.assertEqual(User.objects.filter(is_active=True).count(), 1)
                self.assertEqual(User.objects.filter(is_active=False).count(), 2)
