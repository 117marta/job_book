import datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.files.images import get_image_dimensions
from PIL import Image

from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import (
    AVATAR_ALLOWED_CONTENT_TYPES,
    AVATAR_DIMENSION_ERROR,
    AVATAR_FILE_ERROR,
    AVATAR_MAX_DIMENSION,
    AVATAR_MAX_SIZE,
    AVATAR_SIZE_ERROR,
    AVATAR_TYPE_ERROR,
    BIRTH_DATE_FORM_ERROR,
    LEGAL_AGE,
    PASSWORD_FORM_MATCH_ERROR,
    PASSWORD_FORM_NUMERIC_ERROR,
    TRADE_FORM_HELP_TEXT,
)
from users.models import User


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birth_date"].widget = forms.DateInput(attrs={"type": "date"})
        self.fields["trades"].help_text = TRADE_FORM_HELP_TEXT
        self.initial["trades"] = Trade.objects.get(abbreviation=ABBREVIATION_RAILWAY).pk

    def clean_birth_date(self):
        if value := self.cleaned_data.get("birth_date"):
            if value > datetime.date.today() - relativedelta(years=LEGAL_AGE):
                raise forms.ValidationError(BIRTH_DATE_FORM_ERROR)
            return value

    def clean_avatar(self):
        if avatar := self.cleaned_data.get("avatar"):
            if avatar.content_type not in AVATAR_ALLOWED_CONTENT_TYPES:
                raise forms.ValidationError(AVATAR_TYPE_ERROR)
            else:
                try:
                    with Image.open(avatar) as image:
                        image.verify()
                except Exception:
                    raise forms.ValidationError(AVATAR_FILE_ERROR)

            if avatar.size > AVATAR_MAX_SIZE:
                raise forms.ValidationError(AVATAR_SIZE_ERROR)

            width, height = get_image_dimensions(avatar)
            if width > AVATAR_MAX_DIMENSION or height > AVATAR_MAX_DIMENSION:
                raise forms.ValidationError(
                    AVATAR_DIMENSION_ERROR.format(max_dimension=AVATAR_MAX_DIMENSION)
                )
            return avatar

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(PASSWORD_FORM_MATCH_ERROR)
            elif password1.isdigit():
                raise forms.ValidationError(PASSWORD_FORM_NUMERIC_ERROR)
        return cleaned_data

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "role",
            "trades",
            "birth_date",
            "email",
            "avatar",
        ]
        widgets = {"trades": forms.CheckboxSelectMultiple}


class LoginForm(forms.Form):
    email = forms.CharField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput)


class AcceptOrDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["is_active"]

    @staticmethod
    def accept_users(users_list):
        User.objects.filter(pk__in=users_list).update(is_active=True)

    @staticmethod
    def delete_users(users_list):
        User.objects.filter(pk__in=users_list).delete()
