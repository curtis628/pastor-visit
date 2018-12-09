from datetime import timedelta
import logging

from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field

from .models import Household, Person, Meeting

logger = logging.getLogger(__name__)


def get_meetings():
    now = timezone.now()
    max_start = now + timedelta(weeks=8)

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
    )

    class Meta:
        model = Household
        fields = ["address"]

    def __init__(self, *args, **kwargs):
        super(HouseholdForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("address", "meeting")

    def clean(self):
        super().clean()
        if "meeting" in self.cleaned_data:
            meeting_id = self.cleaned_data.get("meeting")
            logger.debug("Validating [meeting_id=%s]", meeting_id)
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
