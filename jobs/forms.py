import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django import forms
from django.db.models import Case, Value, When

from jobs.consts import DEADLINE_FORM_ERROR, KM_HELP_TEXT
from jobs.models import Job, JobFile
from users.models import SURVEYOR, User


class JobModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name} {obj.first_name} [{obj.get_role_display()}]"


class JobCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["principal"].initial = self.user
        self.fields["contractor"].queryset = User.objects.annotate(
            match_order=Case(
                When(role__iexact=SURVEYOR, then=Value(0)),
                default=Value(1),
            )
        ).order_by("match_order", "last_name", "first_name")
        self.fields["km_from"].help_text = self.fields["km_to"].help_text = KM_HELP_TEXT

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Field("principal", wrapper_class="col-md-6"),
                Field("contractor", wrapper_class="col-md-6"),
                css_class="row d-flex justify-content-evenly",
            ),
            Div(
                Field("kind", wrapper_class="col-md-6"),
                Field("trade", wrapper_class="col-md-6"),
                css_class="row d-flex justify-content-evenly",
            ),
            Field("description", wrapper_class="col-md-12"),
            Div(
                Field("km_from", wrapper_class="col-md-6"),
                Field("km_to", wrapper_class="col-md-6"),
                css_class="row d-flex justify-content-evenly",
            ),
            Div(
                Field("deadline", wrapper_class="col-md-6"),
                Field("comments", wrapper_class="col-md-6"),
                css_class="row d-flex justify-content-evenly",
            ),
            # Submit("submit", "Create a job", css_class="btn btn-warning bg-gradient"),
        )

    def clean_deadline(self):
        if value := self.cleaned_data.get("deadline"):
            if value < datetime.date.today():
                raise forms.ValidationError(DEADLINE_FORM_ERROR)
            return value

    class Meta:
        model = Job
        exclude = ["status"]
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }
        field_classes = {
            "principal": JobModelChoiceField,
            "contractor": JobModelChoiceField,
        }


class JobViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["principal"].initial = self.instance
        self.fields["contractor"].queryset = User.objects.annotate(
            match_order=Case(
                When(role__iexact=SURVEYOR, then=Value(0)),
                default=Value(1),
            )
        ).order_by("match_order", "last_name", "first_name")
        self.fields["principal"].disabled = True
        self.fields["kind"].disabled = True
        self.fields["trade"].disabled = True
        self.fields["km_from"].disabled = True
        self.fields["km_to"].disabled = True
        self.fields["description"].disabled = True
        self.fields["deadline"].disabled = True

        if not self.user_can_edit():
            self.fields["contractor"].disabled = True
            self.fields["status"].disabled = True
            self.fields["comments"].disabled = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field("principal", wrapper_class="col-md-4"),
                Field("contractor", wrapper_class="col-md-4"),
                Field("status", wrapper_class="col-md-4"),
                css_class="row d-flex justify-content-evenly",
            ),
            Div(
                Field("km_from", wrapper_class="col-md-2"),
                Field("km_to", wrapper_class="col-md-2"),
                Field("deadline", wrapper_class="col-md-2"),
                Field("kind", wrapper_class="col-md-3"),
                Field("trade", wrapper_class="col-md-3"),
                css_class="row d-flex justify-content-evenly",
            ),
            Field("description", wrapper_class="col-md-12"),
            Field("comments", wrapper_class="col-md-12"),
        )

    def user_can_edit(self):
        return self.instance.principal == self.user or self.instance.contractor == self.user

    class Meta:
        model = Job
        fields = "__all__"
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }
        field_classes = {
            "principal": JobModelChoiceField,
            "contractor": JobModelChoiceField,
        }


class JobFileForm(forms.ModelForm):

    class Meta:
        model = JobFile
        fields = ["file"]

        widgets = {
            "file": forms.TextInput(attrs={"type": "File", "multiple": True}),
        }
