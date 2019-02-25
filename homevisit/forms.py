from datetime import timedelta
import logging

from django import forms
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit

from .models import Household, Person, Meeting, MeetingGroup, Feedback

logger = logging.getLogger(__name__)


def get_meeting_dates():
    now = timezone.now()
    max_start = now + timedelta(weeks=settings.HOMEVISIT_HIDE_WEEKS_AFTER)

    mtg_group_query = (
        MeetingGroup.objects
            .filter(date__gt=now)
            .filter(date__lt=max_start)
            .exclude(meeting__household__isnull=False)
            .order_by("date")
    )

    weeks_list = [("", "Select available date here...")]
    for group in mtg_group_query:
        weeks_list.append((group.id, group.date_string()))
    return weeks_list


class HouseholdForm(forms.ModelForm):
    meeting_dates = forms.ChoiceField(
        label="Choose meeting date",
        choices=get_meeting_dates,
        error_messages={
            "invalid_choice": "This date is not currently available. Please retry."
        },
        help_text='<a href="/faqs#no-availability">What if none of these dates/times work for me?</a>',  # noqa
    )

    meeting = forms.CharField(
        label="Choose meeting time",
        max_length=254,
        widget=forms.Select(),
        help_text="Choose meeting date first",
    )

    class Meta:
        model = Household
        fields = ["address"]

    def __init__(self, *args, **kwargs):
        super(HouseholdForm, self).__init__(*args, **kwargs)
        self.fields["address"].widget.attrs.update({"rows": "4"})

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Field("address", wrapper_class="col-md-12"),
                css_class="row",
            ),
            Div(
                Field("meeting_dates", wrapper_class="col-md-6"),
                Field("meeting", wrapper_class="col-md-6"),
                css_class="row",
            ),
        )

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
        fields = ["name", "email", "phone_number", "issue", "comment"]

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget.attrs.update({"rows": "4"})

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = reverse("contact")
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
            Div(Field("comment", wrapper_class="col-md-12"), css_class="row"),
        )
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-success"))
