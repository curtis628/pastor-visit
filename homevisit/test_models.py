import logging
from datetime import timedelta, date, time, datetime
from typing import List, Optional

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

import pytz


from .models import Household, Person, Meeting, Weekdays

logger = logging.getLogger(__name__)


def create_household(address):
    household = Household.objects.create(address=address)
    return household


def create_person(first_name, last_name, email, phone_number=None, household=None):
    person = Person(first_name=first_name, last_name=last_name, email=email)
    if phone_number:
        person.phone_number = phone_number
    if household:
        person.household = household

    person.full_clean()
    person.save()
    return person


def create_meeting(start, end, reserved=None, household=None, name="Test meeting"):
    meeting = Meeting(name=name, start=start, end=end)
    if reserved:
        meeting.reserved = reserved
    if household:
        meeting.household = household

    meeting.full_clean()
    meeting.save()
    return meeting


def create_example_data():
    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    start = now + timedelta(days=1)
    for ndx in range(0, 6):
        meeting = create_meeting(start=start, end=start + timedelta(hours=1))
        print("%s: Created %s" % (ndx + 1, meeting))
        start = start + timedelta(weeks=1)


class PersonModelTests(TestCase):
    def test_full_name(self):
        first_name = "TestFirstName"
        last_name = "TestLastName"
        email = "user@test.com"
        person = create_person(first_name, last_name, email)
        self.assertEqual(1, Person.objects.count())

        expected = "%s %s" % (first_name, last_name)
        self.assertEqual(expected, person.full_name)
        self.assertEqual(person.full_name, str(person))
        self.assertEqual(email, person.email)


class HouseholdModelTests(TestCase):
    def test_create(self):
        address = "Test address"
        household = create_household(address)
        self.assertEqual(1, Household.objects.count())
        self.assertEqual(address, household.address)
        self.assertEqual(address, str(household))

        self.assertFalse(household.owner_name())
        self.assertFalse(household.upcoming_meeting())


class RecurringMeetingTestConfig:
    name: Optional[str] = None
    start_dt: Optional[date] = None
    days: int = 14
    duration_mins: int = 60
    weekdays: List[Weekdays] = [Weekdays.MON, Weekdays.FRI]
    start_times: List[time] = [
        time(19, 0, 0),  # before "MOCK_NOW". 11:00AM PST
        time(20, 30, 0),  # after  "MOCK_NOW". 12:30PM PST
        time(22, 0, 0),  # after  "MOCK_NOW". 02:00PM PST
    ]

    def __str__(self):
        return (
            f"{self.name}: [start={self.start_dt}] [days={self.days}] {self.weekdays}."
            f"times: {self.start_times}"
        )


def populate_example_meetings(
    config: RecurringMeetingTestConfig, mock_now: datetime = None
):
    """Test helper that populates mock data for meetings

    Creates 60 minute meetings between 1/1/2018 - 1/15/2018 that occur:
      * Monday + Friday
      * Each meeting lasts 60 minutes
      * Each matching Weekday has 3 times:
        - 19:00 UTC
        - 20:30 UTC
        - 22:00 UTC

    NOTE: When creating mock meeting instances, we assume "now" is 1/1/2018 20:00 UTC
    """
    now = timezone.now() if mock_now is None else mock_now
    name = config.name if config.name else "Test recurring meeting"
    start_dt: date = config.start_dt if config.start_dt else now.date()
    end_dt: date = start_dt + timedelta(days=config.days)
    Meeting.schedule_recurring(
        name,
        start_dt,
        end_dt,
        config.duration_mins,
        config.weekdays,
        config.start_times,
        create_after=now,
    )


class MeetingModelTests(TestCase):
    def test_create(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)
        address = "Test Address"
        household = create_household(address)
        reserved = start
        meeting = create_meeting(start, end, reserved, household)

        self.assertEqual(1, Meeting.objects.count())
        self.assertEqual(address, meeting.household.address)
        self.assertFalse(meeting.owner_name())

    def test_start_in_past(self):
        start = timezone.now() - timedelta(hours=1)
        end = start + timedelta(hours=1)
        with self.assertRaisesRegex(ValidationError, "Date cannot be in the past"):
            create_meeting(start, end)

    def test_end_equal_to_start(self):
        start = timezone.now() + timedelta(hours=1)
        with self.assertRaisesRegex(
            ValidationError, "End date must come after Start date"
        ):
            create_meeting(start, end=start)

    def test_end_before_start(self):
        start = timezone.now() + timedelta(hours=1)
        end = start - timedelta(minutes=1)
        with self.assertRaisesRegex(
            ValidationError, "End date must come after Start date"
        ):
            create_meeting(start, end)

    def test_meeting_overlaps(self):
        start = timezone.now() + timedelta(hours=3)
        end = start + timedelta(hours=1)
        name = "Successful Meeting"
        create_meeting(start, end, name=name)

        # Creating the same meeting again should fail
        with self.assertRaisesRegex(
            ValidationError, "Cannot overlap with another meeting"
        ):
            create_meeting(start, end)

        # Creating a meeting that starts between the existing one should fail
        new_start = start + timedelta(minutes=10)
        new_end = end + timedelta(minutes=10)
        with self.assertRaisesRegex(
            ValidationError, "Cannot overlap with another meeting"
        ):
            create_meeting(new_start, new_end)

        # Creating a meeting that ends between the existing one should fail
        new_end = end - timedelta(minutes=10)
        new_start = start - timedelta(minutes=10)
        with self.assertRaisesRegex(
            ValidationError, "Cannot overlap with another meeting"
        ):
            create_meeting(new_start, new_end)

        self.assertEqual(1, Meeting.objects.count())
        self.assertEqual(start, Meeting.objects.get().start)
        self.assertEqual(name, Meeting.objects.get().name)

        # You can create a meeting that bumps before previous one
        new_end = start
        new_start = new_end - timedelta(hours=1)
        create_meeting(new_start, new_end)

        # ... and you can create one that bumps after
        new_start = end
        new_end = new_start + timedelta(hours=1)
        create_meeting(new_start, new_end)

        self.assertEqual(3, Meeting.objects.count())

    def test_schedule_meetings(self):
        mock_now: datetime = datetime(2018, 1, 1, 20, 0, 0, tzinfo=pytz.utc)
        config: RecurringMeetingTestConfig = RecurringMeetingTestConfig()
        populate_example_meetings(config, mock_now)

        # Ensure meetings created as expected.
        #  - 2 days/week: Mon+Fri. NOTE: 1/1/2018 was a Monday
        #  - 3 meetings/day: 19:00, 20:30, 22:00 UTC
        #  - First meeting on Monday, 1/1/2018 occurred before create_after
        #
        # Week 1: Mon (2 meetings), Fri (3 meetings)
        # Week 2: Mon (3 meetings), Fri (3 meetings)
        #  Total: 11
        expected_count = (
            len(config.weekdays) * len(config.start_times) * (config.days / 7) - 1
        )
        self.assertEqual(expected_count, Meeting.objects.count())

        # Monday, 1/1/2018 should only have 2 meetings since the first one < mock_now
        self.assertEqual(2, Meeting.objects.filter(start__date=date(2018, 1, 1)).count())

        # Monday, 1/8/2018 should have all 3 meetings though
        jan_8_meetings: List[Meeting] = list(
            Meeting.objects.filter(start__date=date(2018, 1, 8))
        )
        self.assertEqual(3, len(jan_8_meetings))
        for ndx, meeting in enumerate(jan_8_meetings):
            meeting_start = meeting.start.time()
            self.assertEqual(meeting_start, config.start_times[ndx])

    def test_meeting_string(self):
        next_year = timezone.now().year + 1
        start: datetime = datetime(next_year, 1, 1, 19, 0, 0, tzinfo=pytz.utc)
        end: datetime = start + timedelta(hours=1)
        meeting = create_meeting(start, end)

        self.assertEqual(f"Jan. 1, {next_year} 11:00 AM - 12:00 PM", str(meeting))
        self.assertIn(f"Jan. 1, {next_year} 11:00 AM - 12:00 PM", meeting.full_name())

        start = start + timedelta(days=1)
        end = end + timedelta(days=2)
        meeting = create_meeting(start, end)
        self.assertEqual(
            f"Jan. 2, {next_year} 11:00 AM - Jan. 3, {next_year} 12:00 PM", str(meeting)
        )
