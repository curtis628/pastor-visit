import logging

from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .forms import HouseholdForm, OwnerForm, FeedbackForm

logger = logging.getLogger(__name__)


class HouseholdCreateView(CreateView):
    template_name = "homevisit/index.html"
    form_class = HouseholdForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner_form"] = OwnerForm(prefix="ownerForm")

        household_form = context["form"]
        meeting_field = household_form.fields["meeting"]
        meeting_choices = [choice for choice in meeting_field.choices]
        meeting_nums = len(meeting_choices)
        if meeting_nums == 0:
            logger.warning("There are no meetings to choose from!")
            context["no_meetings_error"] = True
        return context

    @transaction.atomic
    def post(self, request):
        owner_form = OwnerForm(request.POST, prefix="ownerForm")
        household_form = HouseholdForm(request.POST)

        if owner_form.is_valid() and household_form.is_valid():
            household = household_form.save()

            owner = owner_form.save(commit=False)
            owner.household = household
            owner.save()

            meeting = household_form.cleaned_data["meeting_obj"]
            meeting.household = household
            meeting.reserved = timezone.now()
            meeting.save()
            logger.info(
                "Created [house=%s] with [owner=%s] [meeting=%s]",
                household,
                owner,
                meeting,
            )

            return HttpResponseRedirect(reverse("success"))

        context = {"owner_form": owner_form, "form": household_form}
        return render(request, "homevisit/index.html", context)


class SuccessView(TemplateView):
    template_name = "homevisit/success.html"


class AboutView(TemplateView):
    template_name = "homevisit/about.html"


class FeedbackCreateView(CreateView):
    template_name = "homevisit/feedback.html"
    form_class = FeedbackForm
    success_url = "/feedback/success"


class FeedbackSuccessView(TemplateView):
    template_name = "homevisit/feedback_success.html"
