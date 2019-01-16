import logging

from django.core.management.base import BaseCommand

from homevisit.models import Meeting
from homevisit.management.commands.create_meetings import _valid_date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "cancels meetings based on parameters"

    def add_arguments(self, parser):
        parser.add_argument(
            "dates",
            help=f"The dates to cancel. Expected format: YYYY-mm-dd",
            metavar="date",
            nargs="+",
            type=_valid_date,
        )

    def handle(self, *args, **options):
        dates = options["dates"]
        logger.info(
            f"Cancelling meetings that occur on: %s ...",
            [str(cancel_dt) for cancel_dt in dates],
        )

        for cancel_date in dates:
            meeting = Meeting.objects.filter(start__date=cancel_date)
            if meeting:
                meeting.delete()
                logger.info(f"Cancelled {str(cancel_date)} meeting")
