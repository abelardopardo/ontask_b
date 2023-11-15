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
        quiz_id = 391

        # Fetch the current Canvas quiz stats
        # Call the function to fetch quiz statistics data
        self.stdout.write(self.style.SUCCESS(f'Starting to fetch data for course {course_id}, quiz {quiz_id}'))
        fetch_canvas_data_quiz_stats(course_id, quiz_id)

        self.stdout.write(self.style.SUCCESS('Finished fetching data.'))
        # Fetch the quiz submissions Canvas data
        canvas_data = fetch_canvas_data_submissions(course_id, quiz_id)
        
        if canvas_data.empty:
            logging.error('Failed to fetch data from Canvas.')
            return

        # Using Workflow ID 3 for now
        wid = 3

        # Updating data on OnTask
        quiz_stats_data = fetch_canvas_data_quiz_stats(course_id, quiz_id)
        if not quiz_stats_data.empty:
        # If the DataFrame is not empty, proceed to update OnTask
        
            # Update OnTask table with the new data
            update_success = update_ontask_table(quiz_stats_data, wid)
            if update_success:
                logging.info("The OnTask table was successfully updated with data from Canvas.")
            else:
                logging.error("Failed to update the OnTask table with data from Canvas.")
        else:
            logging.error("No data was fetched from Canvas, or the data is not in the expected format.")

        # Fetch existing data in OnTask
        ontask_data = fetch_ontask_data(wid)
        if data_has_changes(canvas_data, ontask_data):
            logging.info("Data has changed. Proceeding with OnTask update.")
            if update_ontask_table(canvas_data, wid):
                logging.info('OnTask table updated successfully.')
            else:
                logging.error('OnTask table update failed.')
        else:
            logging.info('No changes detected. OnTask update skipped.')
        
        self.stdout.write(self.style.SUCCESS('Agent operation completed.'))