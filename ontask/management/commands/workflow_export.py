"""Command to export a single workflow."""
import shutil

from django.core.management.base import BaseCommand

from ontask import models
from ontask.workflow import services


class Command(BaseCommand):
    """Command to export a single workflow."""

    def add_arguments(self, parser):
        """Parse the command arguments."""
        parser.add_argument(
            '-o',
            '--output',
            default='ontask_workflow.gz',
            help='Output GZ file')

        parser.add_argument(
            '-w',
            help='Workflow ID')

    def handle(self, *args, **options):
        """Export a single workflow."""
        # Obtain workflow id
        wid = options['w']

        # Search for the workflow
        workflow = models.Workflow.objects.filter(pk=wid).first()
        if not workflow:
            self.stdout.write(self.style.ERROR(
                'There is no workflow with the given IDs',
            ))
            return

        # Obtain file name
        filename = options['output']

        # Export the workflow and store it in the given file name
        print('Storing in', filename)

        zbuf = services.do_export_workflow_parse(
            workflow,
            workflow.actions.all())
        zbuf.seek(0)
        with open(filename, 'wb') as f_obj:
            shutil.copyfileobj(zbuf, f_obj, length=131072)
