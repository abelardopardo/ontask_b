# -*- coding: utf-8 -*-
import argparse

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from workflow.models import Workflow
from workflow.ops import do_import_workflow_parse


class Command(BaseCommand):
    help = 'Imports a given workflow as the given user.'

    missing_args_message = (
        "No workflow file provided."
    )

    def add_arguments(self, parser):

        parser.add_argument('-u', '--useremail',
                            required=True,
                            help='User email')

        parser.add_argument('-n', '--name',
                            required=True,
                            help='workflow name')

        parser.add_argument('-r',
                            dest='replace',
                            action='store_true',
                            help='Replace workflow if it exists')

        # Mandatory file name
        parser.add_argument('args',
                            metavar='workflow_file',
                            nargs=1,
                            type=argparse.FileType('rb'),
                            help='Workflow file')


    def handle(self, *args, **options):

        # Obtain user
        user = get_user_model().objects.filter(
            email=options['useremail']
        ).first()

        if not user:
            raise CommandError('User {0} not found'.format(options['username']))

        # if options['']
        # Search for a workflow with the given name
        workflow = Workflow.objects.filter(
            user__email=options['useremail'],
            name=options['name']
        ).first()

        if workflow and not options['replace']:
            raise CommandError(
                'A workflow with this name already exists'
            )

        if workflow and options['replace']:
            # Remove the workflow before uploading it again
            if options['verbosity']:
                self.stdout.write(self.style.SUCCESS(
                    'Deleting workflow {0}'.format(options['name'])
                ))
            workflow.delete()

        if options['verbosity']:
            self.stdout.write(self.style.SUCCESS(
                'Importing workflow in {0} as user {1}'.format(
                    args[0].name, user.email
                )
            ))

        do_import_workflow_parse(user, options['name'], args[0])

