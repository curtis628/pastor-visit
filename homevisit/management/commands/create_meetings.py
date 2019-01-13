import pytz
from datetime import datetime
from django.core.management.base import BaseCommand

from homevisit.models import Meeting, Weekdays
from homevisit.test_models import RecurringMeetingTestConfig, populate_example_meetings


class Command(BaseCommand):
    help = "creates new meetings using hard-coded values"

    # use add_arguments later instead of hard-coding
    # def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        pacific = pytz.timezone("US/Pacific")
        start_date_pst = pacific.localize(datetime(2019, 1, 29, 19, 0))
        start_date = start_date_pst.astimezone(pytz.utc)

        Meeting.objects.all().delete()
        config = RecurringMeetingTestConfig()
        config.name = "Round 1: Jan-Apr on Tues"
        config.start_dt = start_date.date()
        config.days = 42
        config.weekdays = [Weekdays.WED]
        config.start_times = [start_date.time()]
        populate_example_meetings(config)

        # add dates after DST happens. Should fix this, but no time.
        start_date_pst = pacific.localize(datetime(2019, 3, 12, 19, 0))
        start_date = start_date_pst.astimezone(pytz.utc)
        config.start_dt = start_date.date()
        config.days = 49
        config.start_times = [start_date.time()]
        populate_example_meetings(config)

        # Cancel one date
        cancel_date_pst = pacific.localize(datetime(2019, 3, 19, 0, 0))
        cancel = Meeting.objects.filter(start__gte=cancel_date_pst)[0]
        cancel.delete()
        self.stdout.write(self.style.SUCCESS("Canceling 3/19 Meeting..."))

        self.stdout.write(
            self.style.SUCCESS("Successfully created all meeting instances")
        )
