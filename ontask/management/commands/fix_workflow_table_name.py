"""Command to assign the correct value at workflow table name."""
from django.core.management.base import BaseCommand

from ontask.models import Workflow


class Command(BaseCommand):
    """Class implementing a command to fix workflow table names."""

    help = """This command traverses all workflows in the database and
    overrides the table name field with the correct one created with the id.
    If the argument --dry-run is given, the discrepancies are printed,
    but no action is taken."""

    def add_arguments(self, parser):
        # Optional argument -n to do a dry run, flag but not run operations
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help='Print the operations but do not perform any changes')

    def handle(self, *args, **options):
        """Execute command to fix workflow table names.

        :param args: Arguments given to the command (--dry-run for dry run)
        :param options: Options parsed
        :return: Nothing
        """
        empty = True
        for w in Workflow.objects.exclude(data_frame_table_name__exact=''):
            if w.data_frame_table_name != w.df_table_prefix.format(w.id):
                empty = False
                if options['dry_run']:
                    print(
                        'Workflow {0}: '.format(w.id),
                        w.data_frame_table_name)
                else:
                    w.data_frame_table_name = w.df_table_prefix.format(w.id)
                    w.save()
        if empty:
            print('No anomalies detected.')
