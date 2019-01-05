from datetime import timedelta
import logging

from django import forms
from django.utils import timezone
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit

from .models import Household, Person, Meeting, Feedback

logger = logging.getLogger(__name__)


def get_meetings():
    now = timezone.now()
    max_start = now + timedelta(weeks=12)

    mtg_query = (
        Meeting.objects.filter(start__gt=now)
        .filter(start__lt=max_start)
        .filter(household=None)
    )

    weeks_list = []
    for mtg in mtg_query:
        weeks_list.append((mtg.id, mtg))

    return weeks_list


class HouseholdForm(forms.ModelForm):
    meeting = forms.ChoiceField(
        label="Choose Meeting",
        choices=get_meetings,
        error_messages={
            "invalid_choice": "This meeting is not currently available. Please retry."
        },
        help_text='<a href="/faqs#no-availability">What if none of these times work for me?</a>',  # noqa
    )

    class Meta:
        model = Household
        fields = ["address"]

    def __init__(self, *args, **kwargs):
        super(HouseholdForm, self).__init__(*args, **kwargs)
        self.fields["address"].widget.attrs.update({"rows": "4"})

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("address", "meeting")

    def clean(self):
        super().clean()
        if "meeting" in self.cleaned_data:
            meeting_id = self.cleaned_data.get("meeting")
            query = Meeting.objects.filter(pk=meeting_id).filter(household=None)
            self.cleaned_data["meeting_obj"] = query.get()
            logger.debug("HouseholdForm valid with cleaned_data: %s", self.cleaned_data)
        return self.cleaned_data


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ["notes", "household"]

    def __init__(self, *args, **kwargs):
        super(OwnerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field("first_name", wrapper_class="col-md-6"),
                Field("last_name", wrapper_class="col-md-6"),
                css_class="row",
            ),
            Div(
                Field("email", wrapper_class="col-md-6"),
                Field("phone_number", wrapper_class="col-md-6"),
                css_class="row",
            ),
        )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "email", "phone_number", "issue", "feedback"]

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields["feedback"].widget.attrs.update({"rows": "4"})

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = reverse("feedback")
        self.helper.layout = Layout(
            Div(
                Field("name", wrapper_class="col-md-6"),
                Field("email", wrapper_class="col-md-6"),
                css_class="row",
            ),
            Div(
                Field("phone_number", wrapper_class="col-md-6"),
                Field("issue", wrapper_class="col-md-6"),
                css_class="row",
            ),
            Div(Field("feedback", wrapper_class="col-md-12"), css_class="row"),
        )
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-success"))
