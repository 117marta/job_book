from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.db.models import Case, Value, When

from jobs.consts import KM_HELP_TEXT
from jobs.models import Job
from users.models import SURVEYOR, User


class JobModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name} {obj.first_name} [{obj.get_role_display()}]"


class JobCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["principal"].initial = self.instance
        self.fields["contractor"].queryset = User.objects.annotate(
            match_order=Case(
                When(role__iexact=SURVEYOR, then=Value(0)),
                default=Value(1),
            )
        ).order_by("match_order", "last_name", "first_name")
        self.fields["km_from"].help_text = self.fields["km_to"].help_text = KM_HELP_TEXT

        self.helper = FormHelper()
        self.helper = FormHelper()
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
            Submit("submit", "Create a job", css_class="btn btn-danger bg-gradient"),
        )

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
