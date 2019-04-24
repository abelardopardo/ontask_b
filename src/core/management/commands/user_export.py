# -*- coding: utf-8 -*-

import shutil

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from workflow.models import Workflow
from workflow.ops import do_export_workflow_parse


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output_prefix',
                            default='ontask_',
                            help='Prefix for the GZ files')

        parser.add_argument('-u', '--useremail',
                            help='User email')


    def handle(self, *args, **options):

        user = get_user_model().objects.filter(
            email=options['useremail']
        ).first()
        # Obtain user
        if not user:
            self.stdout.write(self.style.ERROR(
                'User {0} unknown'.format(options['useremail'])
            ))
            return

        # Search for the workflow
        workflows = Workflow.objects.filter(
            user__email=options['useremail']
        ).prefetch_related('actions')

        for idx, workflow in enumerate(workflows):
            # Obtain file name
            filename = options['output_prefix'] + \
                       str(workflow.id).zfill(6) + '.gz'

            # Export the workflow and store it in the given file name
            print('Storing workflow in', filename)

            zbuf = do_export_workflow_parse(workflow, workflow.actions.all())
            zbuf.seek(0)
            with open(filename, 'wb') as f:
                shutil.copyfileobj(zbuf, f, length=131072)

