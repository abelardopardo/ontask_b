# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import codecs
import getopt
import shlex
import sys
import csv

import os
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

___doc___ = """Script to create users. Execute without parameters for help"""


def run(*script_args):
    """
    Script to create users in the platform from a CSV file with a column
    containing email addresses. Invocation example:

    python manage.py runscript create_users \
           --script-args "-d -i -e 'emailcolumn' users.csv"

    :param script_args: Arguments given to the script.
            -d Turns on debug
            -i make users members of the instructor group (def. False)
            -e <string> email column name (def. email)
            <filename> CSV filename containing the data
    :return: Changes reflected in the dt
    """

    # If there is no argument given, bomb out.
    if len(script_args) == 0:
        print(run.__doc__)
        sys.exit(1)

    # Parse the arguments
    argv = shlex.split(script_args[0])

    # Default values for the arguments
    debug = False
    email_column_name = 'email'
    make_instructors = False
    filenames = []

    # Parse options
    try:
        opts, args = getopt.getopt(argv, "die:")
    except getopt.GetoptError as e:
        print(e.msg)
        print(run.__doc__)
        sys.exit(2)

    # Store option values
    for optstr, value in opts:
        if optstr == "-d":
            debug = True
        elif optstr == "-i":
            make_instructors = True
        elif optstr == "-e":
            email_column_name = value

    if len(args) == 0:
        print('Script needs at least a file as last argument.')
        print(run.__doc__)
        sys.exit(2)

    filenames = args
    not_present = [x for x in filenames if not os.path.exists(x)]
    if not_present:
        print('Files not found: ', ', '.join(not_present))
        sys.exit(2)

    if debug:
        print('Options:')
        print(' Debug:' + str(debug))
        print(' Email column name:', email_column_name)
        print(' Make instructors:', str(make_instructors))
        print(' Files: ' + ', '.join(filenames))

    if make_instructors:
        # Create the instructor group if it does not exist
        if not Group.objects.filter(name='instructor').exists():
            group = Group(name='instructor')
            group.save()
        else:
            group = Group.objects.get(name='instructor')

    for file_name in filenames:

        # Open the file for reading
        file_in = codecs.open(file_name, 'rU')
        dialect = csv.Sniffer().sniff(file_in.read(1024))
        file_in.seek(0)
        data_in = csv.reader(file_in, dialect)

        line_number = 0
        header_detected = False
        email_idx = -1
        for data in data_in:
            # Count the line number to flag anomalies
            line_number += 1

            # If mark has not been detected yet
            if not header_detected:
                if email_column_name not in data:
                    # Line does not match, skip it
                    continue

                # At this point the email  column has been detected
                header_detected = True

                # Get index of email column
                email_idx = data.index(email_column_name)

                if debug:
                    print('Columns:', data, file=sys.stderr)
                    print('Lookup idx:', email_idx, file=sys.stderr)

                # Proceed with the following lines
                continue

        # Safety check. If something went wrong when the CSV file was
        # exported, it is very likely that the string #REF! is present. If
        # so, notify and stop.
        if '#REF!' in data:
            print('Line', line_number, 'contains incorrect data',
                  file=sys.stderr)
            sys.exit(1)

        # At this point we are processing a data line

        # If the number of fields does not match then number of columns Flag!
        if email_idx >= len(data):
            print('Mismatched line', line_number, 'skipping', file=sys.stderr)
            continue

        # Get the email string
        email_string = data[email_idx]

        # Get or create the user
        user, created = get_user_model().objects.get_or_create(
            email=email_string
        )

        if debug and created:
            print('User ' + email_string + ' created.')

        if not make_instructors:
            # No need to make instructor, so continue
            continue

        if debug:
            print('Adding user ' + user.email + ' to group ' + group.name)

        user.groups.add(group)
        user.save()
