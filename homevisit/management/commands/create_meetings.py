import argparse
import logging

import pytz
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from homevisit.models import Meeting, Weekdays

logger = logging.getLogger(__name__)
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
pacific = pytz.timezone("US/Pacific")

WEEKDAY_NAMES = [day.name for day in list(Weekdays)]
WEEKDAY_VALUES = [day.value for day in list(Weekdays)]


def _valid_date(s):
    try:
        return datetime.strptime(s, DATE_FORMAT).date()
    except ValueError:
        msg = f"'{s}' is not a valid date. Expected format: {DATE_FORMAT}."
        raise argparse.ArgumentTypeError(msg)


def _valid_time(s):
    try:
        return datetime.strptime(s, TIME_FORMAT).time()
    except ValueError:
        msg = f"'{s}' is not a valid time. Expected format: {TIME_FORMAT}."
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = "creates new batches of meetings based on parameters"

    def add_arguments(self, parser):
        parser.add_argument("name", help="The name of this batch of meetings")
        parser.add_argument(
            "begin_date",
            help="The initial date of this meeting batch: YYYY-mm-dd",
            type=_valid_date,
        )
        parser.add_argument(
            "final_date",
            help="The last date of this meeting batch: YYYY-mm-dd",
            type=_valid_date,
        )
        parser.add_argument(
            "start_time",
            help="The meeting's starting time: HH:MM (24 clock)",
            type=_valid_time,
        )
        parser.add_argument(
            "days",
            help="The days of the week the meetings will occur. Ex: 'MON WED FRI'",
            metavar="day",
            nargs="+",
            choices=WEEKDAY_NAMES,
        )
        parser.add_argument(
            "--duration-mins",
            help="The meeting's duration (in minutes). Default: 60",
            type=int,
            default=60,
        )

    def handle(self, *args, **options):
        name = options["name"]
        begin_date = options["begin_date"]
        final_date = options["final_date"]
        start_time = options["start_time"]
        duration_mins = options["duration_mins"]
        days = options["days"]

        logger.info(
            "Creating meeting batch using:\n"
            f"          name: {name}\n"
            f"    begin_date: {str(begin_date)}\n"
            f"    final_date: {str(final_date)}\n"
            f"    start_time: {str(start_time)}\n"
            f" duration_mins: {duration_mins}\n"
            f"          days: {days}"
        )

        date_pst = pacific.localize(datetime.combine(begin_date, start_time))
        while date_pst.date() <= final_date:
            weekday = date_pst.weekday()
            if Weekdays(weekday).name in days:
                meeting_start_pst = pacific.localize(
                    datetime.combine(date_pst.date(), start_time)
                )
                meeting_start_utc = meeting_start_pst.astimezone(pytz.utc)
                meeting_end_utc = meeting_start_utc + timedelta(minutes=duration_mins)
                meeting = Meeting(name=name, start=meeting_start_utc, end=meeting_end_utc)
                meeting.save()
                self.stdout.write(self.style.SUCCESS(f"Created meeting: {str(meeting)}"))
            date_pst = date_pst + timedelta(days=1)
