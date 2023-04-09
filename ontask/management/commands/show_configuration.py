"""Command to show the configuration execution."""
from django.core.management.base import BaseCommand
from settings.base import show_configuration


class Command(BaseCommand):
    """Class implementing a command to show the configuration."""

    help = """This command prints all the configuration variables that affect
    the execution of OnTask. It is useful to verify that the configuration is
    correct.
    """

    def handle(self, *args, **options):
        """Execute command to show the configuration.

        :param args: Arguments given to the command (None!)
        :param options: Options parsed
        :return: Nothing
        """
        show_configuration()
