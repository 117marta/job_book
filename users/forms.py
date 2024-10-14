import datetime

from dateutil.relativedelta import relativedelta
from django import forms

from trades.models import ABBREVIATION_RAILWAY, Trade
from users.const import (
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
        fields = ["first_name", "last_name", "phone", "role", "trades", "birth_date", "email"]
        widgets = {"trades": forms.CheckboxSelectMultiple}


class LoginForm(forms.Form):
    email = forms.CharField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput)


class AcceptOrDeleteForm(forms.Form):
    action_checkbox = forms.BooleanField()
