# -*- coding: utf-8 -*-

"""Script to create users. Execute without parameters for help."""
from builtins import str
import codecs
import csv
import os
import sys
from typing import Any, List

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Cldss implementing the command to create users."""

    help_msg = """Script to create the initial database content."""

    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Parse the arguments."""
        parser.add_argument(
            '-i',
            '--instructor',
            action='store_true',
            help='make users instructors')

        parser.add_argument(
            '-e',
            '--email',
            default='email',
            help='name of the email column')

        parser.add_argument(
            '-p',
            default='boguspwd',
            help='Default password value')

        parser.add_argument(
            'csvfile',
            type=str,
            nargs='*',
            help='CSV files')

    def handle(self, *args, **options):
        """Execute the command, process the file and create the users."""
        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS('Initializing the database'))
        group = Group.objects.filter(name='instructor').first()
        if group:
            self.stdout.write('Instructor group already exists. Bypassing.')
        else:
            # Create the instructor group if it does not exist
            self.stdout.write('Creating instructor group')
            group = Group(name='instructor')
            group.save()

        if not options['instructor']:
            group = None

        if not options['csvfile']:
            # If there is no argument we are done.
            return

        filenames = options['csvfile']
        not_present = [
            fname for fname in filenames if not os.path.exists(fname)
        ]
        if not_present:
            self.stdout.write(self.style.ERROR(
                'These files were not found: ' + ', '.join(not_present),
            ))
            filenames = [
                fname
                for fname in options['csvfile']
                if fname not in not_present]

        if not filenames:
            self.stdout.write(self.style.ERROR(
                'No files provided to create users. Terminating',
            ))
            return

        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS('Step: Obtaining emails'))

        # Get the emails
        emails = self.get_column_value_list(
            filenames,
            options['email'],
            options['verbosity'] > 0)

        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS('Step: Creating users'))

        self.create_users(
            emails,
            options['p'],
            group,
            options['verbosity'] > 0)

    @staticmethod
    def get_column_value_list(filenames, column_name, debug=False):
        """Get the values of the given column from all filenames.

        Function that given a set of filenames returns the list of values
        concatenating all the columns with name "column_name"
        :param filenames: List of filenames
        :param column_name: Column name to search.
        :param debug: Boolean controlling the log messages.
        :return: List of values.
        """
        to_return = []
        for file_name in filenames:

            # Open the file for reading
            file_in = codecs.open(file_name, 'rU')
            dialect = csv.Sniffer().sniff(file_in.read(1024))
            file_in.seek(0)
            data_in = csv.reader(file_in, dialect=dialect, delimiter=str(','))

            if debug:
                print('Parsing file ' + file_name)

            to_return += process_csv_file(data_in, column_name)

        return to_return

    @staticmethod
    def create_users(emails, password, group=None, debug=False):
        """Create users with the given information.

        Given a list of emails, create demo users with the initial password,
        make them members of the given group

        :param emails: List of emails
        :param password: Password to assign to all users
        :param group: Make users members of this group (if given)
        :param debug: Boolean controlling the printing of debug messages
        :return: Effect in the database
        """
        for email in emails:
            # Get or create the user
            user, created = get_user_model().objects.get_or_create(email=email)
            if created:
                user.name = 'User Name'
                user.set_password(password)
                user.save()

            if debug and created:
                print('User ' + email + ' created.')

            if not group:
                # No need to add to group
                continue

            if group not in user.groups.all():
                if debug:
                    print(
                        'Adding user ' + user.email + ' to group '
                        + group.name)

                user.groups.add(group)
                user.save()


def process_csv_file(data_in, column_name) -> List[Any]:
    """Process a CSV file (already open) and return list of values in column.

    :param data_in: file object already open and ready to be used.
    :param column_name: Name of the column from where to extract the data.
    :return: List of values in the column
    """
    to_return = []

    line_number = 0
    header_detected = False
    col_idx = -1
    for line_data in data_in:
        # Count the line number to flag anomalies
        line_number += 1

        # If mark has not been detected yet
        if not header_detected:
            if column_name not in line_data:
                # Line does not match, skip it
                continue

            # At this point the column has been detected
            header_detected = True

            # Get index of the column
            col_idx = line_data.index(column_name)

            # Proceed with the following lines
            continue

        # Safety check. If something went wrong when the CSV file was
        # exported, it is very likely that the string #REF! is
        # present. If so, notify and stop.
        if '#REF!' in line_data or '#VALUE' in line_data:
            print(
                'Line',
                line_number,
                'contains incorrect data',
                file=sys.stderr)
            sys.exit(1)

        # At this point we are processing a data line

        # If the number of fields does not match then number of
        # columns Flag!
        if col_idx >= len(line_data):
            print(
                'Mismatched line',
                line_number,
                'skipping',
                file=sys.stderr)
            continue

        # append the string
        to_return.append(line_data[col_idx])

    return to_return
