import logging
from datetime import date, time, datetime, timedelta
from enum import IntEnum
from string import Template
from typing import List


from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

DATE_FORMAT = "%Y-%m-%d %I:%M%p %Z"

logger = logging.getLogger(__name__)


def validate_future_date(value):
    """Validate that 'value' is not a date in the past (if provided)."""
    if value and value <= timezone.now():
        raise ValidationError("Date cannot be in the past")


class Household(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.address


class Person(models.Model):
    household = models.ForeignKey(
        Household, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    phone_number = PhoneNumberField(blank=True)
    notes = models.TextField(blank=True)

    @property
    def full_name(self):
        """Returns the person's full name."""
        return "%s %s" % (self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class Weekdays(IntEnum):
    """Python uses Monday==0 and Sunday==6 to represent weekdays.

    see: https://docs.python.org/3/library/datetime.html#datetime.date.weekday
    """

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class Meeting(models.Model):
    _STR_TEMPLATE = Template("$name: $start - $end")

    name = models.CharField(max_length=50)
    start = models.DateTimeField(validators=[validate_future_date])
    end = models.DateTimeField()
    reserved = models.DateTimeField(
        null=True, blank=True, validators=[validate_future_date]
    )
    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, null=True, blank=True
    )

    def clean(self):
        if self.end <= self.start:
            raise ValidationError(
                {"end": _("End date must come after Start date.")}, code="invalid"
            )

        overlap = Meeting.objects.filter(end__gt=self.start).filter(start__lt=self.end)
        if overlap.count() > 0:
            raise ValidationError(
                {"start": _("Cannot overlap with another meeting")}, code="invalid"
            )

    @staticmethod
    def schedule_recurring(
        name: str,
        begin_date: date,
        end_date: date,
        duration_mins: int,
        weekdays: List[Weekdays],
        start_times: List[time],
        create_after: datetime = None,
    ) -> None:
        """Creates recurring Meeting instances based on parameters.

        :param name: the name to use for all meeting instances
        :param begin_date: the initial date of the recurring meetings
        :param end_date: the ending date of the recurring meetings
        :param duration_mins: the length of each meeting (in minutes)
        :param weekdays: set of Weekdays to schedule the meeting occurrences
        :param start_times: a list of starting times for each weekday
        :param create_after: only create meetings if after this datetime.
            If not provided, timezone.now() is used.
        """
        logger.debug(
            "Scheduling '%s' %s to %s meeting of length %s mins on [days=%s]. "
            "Starting times: %s",
            name,
            begin_date,
            end_date,
            duration_mins,
            weekdays,
            start_times,
        )

        _create_after: datetime = timezone.now() if create_after is None else create_after
        initial_date: date = _create_after.date()
        delta = end_date - initial_date
        # Iterate over each day between _create_after and end_date
        for day_num in range(delta.days):
            loop_date = initial_date + timedelta(days=day_num)
            # if loop_date lands on a weekday that was requested...
            if loop_date.weekday() in weekdays:
                for start_time in start_times:
                    mtg_start = datetime.combine(
                        loop_date, start_time, tzinfo=_create_after.tzinfo
                    )
                    mtg_end = mtg_start + timedelta(minutes=duration_mins)

                    # Create the meeting if start_time is later than _create_after
                    if mtg_start > _create_after:
                        mtg = Meeting.objects.create(
                            name=name, start=mtg_start, end=mtg_end
                        )
                        logger.info("Created %s", mtg)

    def __str__(self):
        start_local = timezone.localtime(self.start)
        end_local = timezone.localtime(self.end)

        return self._STR_TEMPLATE.substitute(
            name=self.name,
            start=start_local.strftime(DATE_FORMAT),
            end=end_local.strftime(DATE_FORMAT),
        )
