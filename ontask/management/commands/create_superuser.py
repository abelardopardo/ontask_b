"""File with a command to create a superuser."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Class to implement a command to create the superuser."""

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            '-u',
            '--username',
            required=True,
            help='Super user name')

        parser.add_argument(
            '-e',
            '--email',
            required=True,
            help='Super user email')

        parser.add_argument(
            '-p',
            '--password',
            required=True,
            help='Super user password')

    def handle(self, *args, **options):  # noqa: Z110
        """Run the command to create the superuse.

        :param args: Args received by the command
        :param options: Parsed options
        :return: Reflects changes in the DB.
        """
        user_model = get_user_model()

        if not user_model.objects.filter(email=options['email']).exists():
            user_model.objects.create_superuser(
                name=options['username'],
                email=options['email'],
                password=options['p'],
            )
