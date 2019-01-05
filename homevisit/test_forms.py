from django.test import TestCase

from .forms import OwnerForm, HouseholdForm
from .models import Meeting
from .test_models import RecurringMeetingTestConfig, populate_example_meetings


class OwnerFormTests(TestCase):
    def _verify_form(self, data, expected):
        owner_form = OwnerForm(data=data)
        self.assertEqual(expected, owner_form.is_valid())

    def test_names_invalid(self):
        form_data = {}
        self._verify_form(form_data, False)

    def test_phone_invalid(self):
        form_data = dict(
            first_name="TestFirst", last_name="TestLast", phone_number="bad phone number"
        )
        self._verify_form(form_data, False)

    def test_email_invalid(self):
        form_data = dict(
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="530-777-7777",
            email="bad email",
        )
        self._verify_form(form_data, False)

    def test_valid(self):
        form_data = dict(
            first_name="TestFirst", last_name="TestLast", email="user@test.com"
        )
        self._verify_form(form_data, True)

        form_data["last_name"] = "TestLast"
        form_data["phone_number"] = "530-777-7777"
        self._verify_form(form_data, True)

        form_data["email"] = "user@test.com"
        self._verify_form(form_data, True)


class HouseholdFormTests(TestCase):
    meeting_config: RecurringMeetingTestConfig

    def setUp(self):
        self.meeting_config = RecurringMeetingTestConfig()
        populate_example_meetings(self.meeting_config)

    def _clean_setup_data(self):
        Meeting.objects.all().delete()

    def _verify_error(self, form_errors, expected_key, expected_substring):
        self.assertIn(expected_key, form_errors)
        self.assertIn(expected_substring, form_errors[expected_key][0])

    def _verify_form(self, data, expected):
        household_form = HouseholdForm(data=data)
        self.assertEqual(expected, household_form.is_valid())
        return household_form

    def test_initial_form(self):
        form = HouseholdForm()
        meeting_choice_field = form.fields["meeting"]

        # choices should be pre-populated by default, due to setUp() method
        choices = [choice for choice in meeting_choice_field.choices]
        self.assertTrue(len(choices) > 0)

    def test_initial_form_no_meetings(self):
        self._clean_setup_data()
        # form = HouseholdForm()
        # meeting_choice_field = form.fields["meeting"]
        # TODO what should happen?

    def test_required_fields(self):
        form_data = dict()
        form = self._verify_form(form_data, False)
        self.assertEqual(2, len(form.errors))
        self._verify_error(form.errors, "address", "required")
        self._verify_error(form.errors, "meeting", "required")

        form_data = dict(address="TestAddress")
        form = self._verify_form(form_data, False)
        self.assertEqual(1, len(form.errors))
        self._verify_error(form.errors, "meeting", "required")

        meeting_choice = Meeting.objects.all()[0]
        form_data = dict(meeting=meeting_choice.id)
        form = self._verify_form(form_data, False)
        self.assertEqual(1, len(form.errors))
        self._verify_error(form.errors, "address", "required")

    def test_form_hides_distant_future_choices(self):
        self._clean_setup_data()

        # HouseholdForm only shows 12 weeks of meeting instances...
        # ... so let's create 20 weeks of meeting instances to test it.
        self.meeting_config.days = 7 * 20
        populate_example_meetings(self.meeting_config)
        form = HouseholdForm()

        # ensure that all meetings aren't shown on form's select choice
        choices = [choice for choice in form.fields["meeting"].choices]
        choice_count = len(choices)
        total_count = Meeting.objects.count()
        self.assertTrue(
            total_count > choice_count,
            f"[total_count={total_count}] [choice_count={choice_count}]",
        )

    def test_valid(self):
        meeting_choice = Meeting.objects.all()[0]
        form_data = dict(address="Test Address Value", meeting=meeting_choice.id)
        form = self._verify_form(form_data, True)

        self.assertEqual(meeting_choice, form.cleaned_data["meeting_obj"])
