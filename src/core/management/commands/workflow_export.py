# -*- coding: utf-8 -*-

import shutil

from django.core.management.base import BaseCommand

from workflow.models import Workflow
from workflow.ops import do_export_workflow_parse


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output',
                            default='ontask_workflow.gz',
                            help='Output GZ file')

        parser.add_argument('-w',
                            help='Workflow ID')


    def handle(self, *args, **options):

        # Obtain workflow id
        wid = options['w']

        # Search for the workflow
        workflow = Workflow.objects.filter(pk=wid).first()
        if not workflow:
            self.stdout.write(self.style.ERROR(
                'There is no workflow with the given IDs'
            ))
            return

        # Obtain file name
        filename = options['output']

        # Export the workflow and store it in the given file name
        print('Storing in', filename)

        zbuf = do_export_workflow_parse(workflow, workflow.actions.all())
        zbuf.seek(0)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(zbuf, f, length=131072)

