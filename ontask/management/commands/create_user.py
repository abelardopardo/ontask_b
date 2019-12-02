# -*- coding: utf-8 -*-

"""Command to create a single user."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Class implementing a command to create a single user."""

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            '-u',
            '--username',
            default='User Name',
            help='User name')

        parser.add_argument(
            '-e',
            '--email',
            default='user@bogus.com',
            help='User email')

        parser.add_argument(
            '-i',
            '--instructor',
            action='store_true',
            help='Include in instructor group')

        parser.add_argument(
            '-p',
            default='boguspwd',
            help='User password')

    def handle(self, *args, **options):
        """Execute command to create a single user.

        :param args: Arguments given to the command
        :param options: Options parsed
        :return: Nothing
        """
        user_model = get_user_model()

        user = user_model.objects.filter(email=options['email']).first()
        if user:
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'User {0} already exists'.format(options['username']),
                ))
        else:
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'Creating user {0} ({1})'.format(
                        options['username'],
                        options['email'],
                    ),
                ))
            user = user_model.objects.create_user(
                name=options['username'],
                email=options['email'],
                password=options['p'],
            )

        if not options['instructor']:
            # No need to check if member of instructor group
            return

        group = Group.objects.filter(name='instructor').first()
        if not group:
            self.stdout.write(self.style.ERROR(
                'Instructor group does not exist. Initialize the DB first.',
            ))
            return

        user.groups.add(group)
        user.save()
