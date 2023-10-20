from django.core.management.base import BaseCommand
from ontask.agent.utils.authenticate import authenticate_canvas
from ontask.agent.data_operations.data_ops import fetch_canvas_data, data_has_changes
import logging

class Command(BaseCommand):

    def fetch_ontask_data(self):
        # Placeholder function to fetch data from OnTask. You'll need to implement this.
        return {}

    def data_has_changes(self, canvas_data, ontask_data):
        # Placeholder function to determine if there are changes.
        # For now, using a simple equality check. Adjust based on your data structures.
        return canvas_data != ontask_data

    def handle(self, *args, **kwargs):
        # Call the authentication functions
        if not authenticate_canvas():
            logging.error('Failed to authenticate with Canvas.')
            return

        # Fetch the current Canvas data
        canvas_data = fetch_canvas_data()
        
        if canvas_data.empty:
            logging.error('Failed to fetch data from Canvas.')
            return
        else:
            pass
        
         # Fetch existing data in OnTask
        ontask_data = self.fetch_ontask_data()  

        # Check if there are changes between the two dataframes
        if data_has_changes(canvas_data, ontask_data):
            print("Data has changed. Proceed with updating OnTask.")
            # Check for data changes and update OnTask accordingly
            if self.data_has_changes(canvas_data, ontask_data):
           # merge_data_to_ontask(canvas_data)
                logging.info('OnTask table updated successfully.')
        
            else:
                logging.info('No changes detected. OnTask table update skipped.')

            self.stdout.write(self.style.SUCCESS('Agent operation completed.'))

        else:
            print("Data has not changed. No need to update OnTask.")

        