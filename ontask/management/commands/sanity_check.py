"""Command to run a set of sanity checks in the database."""
from django.core.management.base import BaseCommand

from ontask.core.checks import sanity_checks

class Command(BaseCommand):
    """Class implementing a command to run the sanity checks."""

    help = """This command performs a set of sanity checks in the database.
    If any anomaly is detected, an exception is raised."""
    
    def handle(self, *args, **options):
        """Execute command to run sanity checks.

        :param args: Arguments given to the command (None!)
        :param options: Options parsed
        :return: Nothing
        """
        sanity_checks()
