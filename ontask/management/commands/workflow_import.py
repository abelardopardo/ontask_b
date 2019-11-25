# -*- coding: utf-8 -*-

"""Command to import a workflow."""

import argparse

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ontask.models import Workflow
from ontask.workflow.services.import_export import do_import_workflow_parse


class Command(BaseCommand):
    """Import a given workflot to a given user."""

    help_txt = 'Imports a given workflow as the given user.'

    missing_args_message = "No workflow file provided."

    def add_arguments(self, parser):
        """Parse the arguments."""
        parser.add_argument(
            '-u',
            '--useremail',
            required=True,
            help='User email')

        parser.add_argument(
            '-n',
            '--name',
            help='Workflow name (only valid if a single file is given)')

        parser.add_argument(
            '-r',
            dest='replace',
            action='store_true',
            help='Replace workflow if it exists')

        # Mandatory file name
        parser.add_argument(
            'args',
            metavar='workflow_file',
            nargs='+',
            type=argparse.FileType('rb'),
            help='Workflow file')

    def handle(self, *args, **options):
        """Execute the command to import a workflow."""
        # Obtain user
        user = get_user_model().objects.filter(
            email=options['useremail'],
        ).first()

        if not user:
            raise CommandError('User {0} not found'.format(
                options['username']))

        if options.get('name') and len(args) > 1:
            raise CommandError(
                'Workflow name cannot be given when importing '
                + 'multiple workflows.',
            )

        # Search for a workflow with the given name
        workflow = Workflow.objects.filter(
            user__email=options['useremail'],
            name=options['name'],
        ).first()

        if workflow and not options['replace']:
            raise CommandError(
                'A workflow with this name already exists',
            )

        if workflow and options['replace']:
            # Remove the workflow before uploading it again
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'Deleting workflow {0}'.format(options['name']),
                ))
            workflow.delete()

        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS(
                'Importing workflow in {0} as user {1}'.format(
                    args[0].name,
                    user.email,
                ),
            ))

        do_import_workflow_parse(user, options['name'], args[0])
