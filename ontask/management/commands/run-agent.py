from django.core.management.base import BaseCommand
from ontask.agent.utils.authenticate import authenticate_canvas
from ontask.agent.data_operations.data_ops import fetch_canvas_data_submissions, fetch_ontask_data, data_has_changes, update_ontask_table, fetch_canvas_data_quiz_stats
import logging

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if not authenticate_canvas():
            logging.error('Failed to authenticate with Canvas.')
            return

        # Set course_id and quiz_id
        course_id = 396
        quiz_id = 377

        # Fetch the current Canvas quiz stats
        # Call the function to fetch quiz statistics data
        self.stdout.write(self.style.SUCCESS(f'Starting to fetch data for course {course_id}, quiz {quiz_id}'))
        fetch_canvas_data_quiz_stats(course_id, quiz_id)

        self.stdout.write(self.style.SUCCESS('Finished fetching data. Check aaa.csv for output.'))
        # Fetch the quiz submissions Canvas data
        canvas_data = fetch_canvas_data_submissions(course_id, quiz_id)
        
        if canvas_data.empty:
            logging.error('Failed to fetch data from Canvas.')
            return

        # Using Workflow ID 1 for now; this can be dynamic based on your needs
        wid = 1

        # Fetch existing data in OnTask
        ontask_data = fetch_ontask_data()

        if data_has_changes(canvas_data, ontask_data):
            logging.info("Data has changed. Proceeding with OnTask update.")
            if update_ontask_table(canvas_data, wid):
                logging.info('OnTask table updated successfully.')
            else:
                logging.error('OnTask table update failed.')
        else:
            logging.info('No changes detected. OnTask update skipped.')
        
        self.stdout.write(self.style.SUCCESS('Agent operation completed.'))