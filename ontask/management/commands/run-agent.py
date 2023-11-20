from django.core.management.base import BaseCommand
import logging
import os
import environ
import json

# Load the values in the env file if it exists
AGENT_ENV_FILENAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../agent/utils/agent.env'))

if os.path.exists(AGENT_ENV_FILENAME):
    environ.Env.read_env(str(AGENT_ENV_FILENAME))

from ontask.agent.utils.authenticate import authenticate_canvas
from ontask.agent.data_operations.data_ops import (
    fetch_canvas_data_submissions,
    fetch_ontask_data,
    data_has_changes,
    update_ontask_table,
    fetch_canvas_data_quiz_stats
)

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.env = environ.Env()

    def __fetch_resource__(self, course_id, quiz_id):
        return fetch_canvas_data_quiz_stats(course_id, quiz_id)

    def __process_resource__(self, wid, resource):
        if not resource.empty:
            update_success = update_ontask_table(resource, wid)
            if update_success:
                logging.info(f"The OnTask table was successfully updated with data from Canvas for WID {wid}.")
            else:
                logging.error(f"Failed to update the OnTask table with data from Canvas for WID {wid}.")
        else:
            logging.error(f"No data was fetched from Canvas, or the data is not in the expected format for WID {wid}.")

    def handle(self, *args, **kwargs):
        if not authenticate_canvas():
            logging.error('Failed to authenticate with Canvas.')
            return

        # Load the course config from env
        courses_config = json.loads(self.env('PYTHON_COURSE', default="{}"))

        for wid, course_info in courses_config.items():
            course_id = course_info.get('course_id')
            quizzes = course_info.get('quizzes')

            if course_id is not None and quizzes is not None:
                for quiz_id in quizzes:
                    logging.info(f"Processing workflow {wid} for course {course_id}, quiz {quiz_id}")
                    resource = self.__fetch_resource__(course_id, quiz_id)
                    self.__process_resource__(wid, resource)
            else:
                logging.error(f"Workflow ID {wid} is missing course_id or quizzes in the configuration.")
