import logging
from string import Template

from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from .forms import HouseholdForm, OwnerForm, FeedbackForm
from .models import Faq

logger = logging.getLogger(__name__)

SUBJECT = "Meeting scheduled with Will and Lindy!"
BODY = Template(
    "Thanks, $name! You're all set for Lindy and I to visit you on $meeting at:\n\n"
    "$address\n\n"
    "If you need to cancel or change this meeting (or if you have any questions), "
    'please <a href="/feedback">contact us on the website</a>.\n\n'
    "Looking forward to seeing you!\n"
    "Will and Lindy"
)


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
                str(household).replace("\r\n", ". "),
                owner,
                meeting,
            )

            msg = BODY.substitute(
                name=owner.first_name,
                meeting=str(meeting),
                address=household.address,
                host_name=settings.HOST_NAME,
            )
            html_msg = msg.replace("\n", "<br>")
            messages.info(request, html_msg, extra_tags="safe")

            if settings.EMAIL_HOST_USER:
                logger.debug("Sending email to %s with body:\n%s", owner.email, msg)
                send_mail(
                    SUBJECT,
                    msg,
                    "homevisit@gmail.com",
                    [owner.email],
                    html_message=html_msg,
                )
            else:
                logger.info("Email is disabled")

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


class FaqListView(ListView):
    template_name = "homevisit/faqs.html"
    model = Faq
