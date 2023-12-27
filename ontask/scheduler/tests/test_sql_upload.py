"""Test the views to create a scheduled SQL operation

Assume we are using the initial workflow. We will use a table stored in the
same database. These are the steps:

1) Create a new table with a subset of the data in the original table and a
subset of the fields

  SELECT email, "Enrolment Type" INTO "__ONTASK_TEST_TABLE"
  FROM "__ONTASK_WORKFLOW_TABLE_1"
  WHERE "Enrolment Type" = 'HECS'
  ORDER BY email LIMIT 3;

2) Add a new column that does not exist in the initial dataframe

  ALTER TABLE "__ONTASK_TEST_TABLE"
  ADD COLUMN "NEW COLUMN" bigint;

3) Add two more users

  INSERT INTO "__ONTASK_TEST_TABLE" VALUES ('newuser1@bogus.com', 'HECS');
  INSERT INTO "__ONTASK_TEST_TABLE" VALUES ('newuser2@bogus.com', 'HECS');
  INSERT INTO "__ONTASK_TEST_TABLE" VALUES ('newuser3@bogus.com', 'HECS');

4) Change the Enrolment type to local

  UPDATE "__ONTASK_TEST_TABLE" SET "Enrolment Type" = 'Local';

5) Populate the column with a sequence from 1-n

  WITH rnq AS (
    SELECT email, row_number() OVER (ORDER BY email) AS rn
      FROM "__ONTASK_TEST_TABLE"
  )
  UPDATE "__ONTASK_TEST_TABLE" tt
  SET "NEW COLUMN" = (SELECT rn FROM rnq WHERE tt.email = rnq.email);

Execute the merge
"""

from django.conf import settings
from django_celery_beat.models import PeriodicTask
from rest_framework import status

from ontask import models, tests
from ontask.tasks.scheduled_ops import execute_scheduled_operation


class SchedulerViewCreateSQLUpload(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase,
):
    """Test the creation of a SQL Upload operation."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        initial_df = self.workflow.data_frame()

        # Create the new table in the DB for the scheduled operation
        tests.create_mock_sql_table()

        # Save some current variables for future checks
        current_ops = models.ScheduledOperation.objects.count()
        current_tasks = PeriodicTask.objects.count()
        current_nrows = self.workflow.nrows
        current_columns = self.workflow.ncols

        # Index page should be ok
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the connection pointing to localhost
        sql_conn = models.SQLConnection.objects.get(name='remote server 2')

        # Modify connection to point to the test DB
        sql_conn.db_name = settings.DATABASE_URL['NAME']
        sql_conn.save(update_fields=['db_name'])

        # GET the form to create the scheduled SQL operation
        resp = self.get_response('scheduler:sqlupload')
        self.assertTrue(status.is_success(resp.status_code))

        # POST incorrect form without a dst key
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'src_key': 'email',
                'how_merge': 'outer',
                'sql_connection': 3})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('operation requires the names', str(resp.content))

        # POST incorrect form without a src key
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'dst_key': 'email',
                'how_merge': 'outer',
                'sql_connection': 3})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('operation requires the names', str(resp.content))

        # POST incorrect form without a non-existent dst_key
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'dst_key': 'INCORRECT NAME',
                'src_key': 'email',
                'how_merge': 'outer',
                'sql_connection': 3})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('is not a key column', str(resp.content))

        # POST incorrect form without an incorrect dst_key
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'dst_key': 'Gender',
                'src_key': 'email',
                'how_merge': 'outer',
                'sql_connection': 3})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('is not a key column', str(resp.content))

        # POST incorrect form without a merge method
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'dst_key': 'Gender',
                'src_key': 'email',
                'sql_connection': 3})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('requires a merge method', str(resp.content))

        # POST the correct form to create the SQL operation
        resp = self.get_response(
            'scheduler:sqlupload',
            method='POST',
            req_params={
                'name': 'schedule sql upload',
                'execute_start': '05/31/2999 14:35',
                'sql_connection': 3,
                'dst_key': 'email',
                'src_key': 'email',
                'how_merge': 'outer',
                'db_password': 'xxx'})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(
            current_ops + 1,
            models.ScheduledOperation.objects.count())

        # Execute the operation
        s_item = self.workflow.scheduled_operations.get(
            name='schedule sql upload')
        execute_scheduled_operation(s_item.id)

        # Verify the result of the operation
        s_item.refresh_from_db()
        self.workflow.refresh_from_db()

        # Identical number of tasks pending than at the start
        self.assertEqual(current_tasks + 1, PeriodicTask.objects.count())

        # Operation must have status equal to DONE
        self.assertEqual(s_item.status, models.scheduler.STATUS_DONE)

        # Operation execution time must be reflected in the log field
        self.assertIsNotNone(s_item.last_executed_log)

        # Number of rows and columns in workflow has changed
        self.assertEqual(self.workflow.nrows, current_nrows + 3)
        self.assertEqual(self.workflow.ncols, current_columns + 1)

        # New column with the right name and type
        new_column = self.workflow.columns.filter(name='NEW COLUMN').first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.data_type, 'double')
        result_df = self.workflow.data_frame()

        # New rows with the right email
        email_values = list(result_df['email'])
        self.assertIn('newuser1@bogus.com', email_values)
        self.assertIn('newuser2@bogus.com', email_values)
        self.assertIn('newuser3@bogus.com', email_values)

        # Columns with the right value
        old_hecs_count = initial_df['Enrolment Type'].loc[
            initial_df['Enrolment Type'] == 'Local'].count()
        new_hecs_count = result_df['Enrolment Type'].loc[
            result_df['Enrolment Type'] == 'Local'].count()
        self.assertEqual(old_hecs_count + 6, new_hecs_count)
        self.assertEqual(result_df['NEW COLUMN'].count(), 6)
