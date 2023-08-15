"""Command to execute SQL code when migrating to version 9."""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """Class executing SQL code required to migrate to version 9."""

    help = """This command executes SQL code required to migrate through
    version 9 of the platform. The command needs to run before the execution
    of the 'migrate' step."""

    def handle(self, *args, **options):
        """Execute SQL code directly in the database.

        :param args: Arguments given to the command (None!)
        :param options: Options parsed
        :return: Nothing
        """
        with connection.cursor() as cursor:
            queries = [
                "INSERT INTO django_migrations (app, name, applied) "
                "VALUES ('ontask', '0001_authtools_user_initial',"
                "CURRENT_TIMESTAMP)",
                "INSERT INTO django_migrations (app, name, applied) "
                "VALUES ('ontask', '0002_django18', CURRENT_TIMESTAMP)",
                "DELETE FROM django_migrations WHERE app = 'authtools'",
                "UPDATE django_content_type SET app_label = 'ontask' "
                "WHERE app_label = 'authtools' AND model = 'user'"]

            for q in queries:
                self.stdout.write('Executing ' + q)
                cursor.execute(q)
