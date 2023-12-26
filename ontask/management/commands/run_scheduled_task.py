"""Command to execute a scheduled task given a scheduled task ID."""
from ontask.tasks.scheduled_ops import execute_scheduled_operation

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Class implementing a command to execute a scheduled task."""

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            '-t',
            '--task',
            required=True,
            type=int,
            help='Task ID')

        parser.add_argument(
            '-e',
            '--email',
            required=True,
            help='User email')

    def handle(self, *args, **options):
        """Execute command to execute scheduled task.

        :param args: Arguments given to the command
        :param options: Options parsed
        :return: Nothing
        """

        user_model = get_user_model()

        user = user_model.objects.filter(email=options['email']).first()
        if not user:
            self.stdout.write(self.style.ERROR(
                'User {0} does not exist'.format(options['email'])))

        execute_scheduled_operation(options['task'])