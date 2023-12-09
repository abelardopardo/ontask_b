"""Upload/Merge dataframe from a CANVAS connection."""
from typing import Dict, Optional
import pandas as pd

from django.utils.translation import gettext_lazy as _

from ontask import models, OnTaskException
from ontask.core import canvas_ops
from ontask.dataops.services import common
from ontask.dataops import pandas


def _extract_quiz_answer_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        quiz_id: int,
        data_frame_source: dict):
    question_prefix = '{0}_{1} Canvas Question'

    quiz_stats = canvas_ops.get_quiz_statistics(
        oauth_info,
        user_token,
        canvas_course_id,
        quiz_id)

    # Loop over all elements with quiz statistics
    for qstat in quiz_stats['quiz_statistics']:
        # Loop over all questions
        for question_stat in qstat['question_statistics']:
            question_name = question_prefix.format(
                quiz_id,
                question_stat['id'])
            # Loop over all answers
            for answer in question_stat['answers']:
                if answer['responses'] == 0:
                    # Skip answers with no responses
                    continue
                # Loop over each user answer
                for user_id, user_name in zip(
                        answer['user_ids'],
                        answer['user_names']):
                    # Fetch the corresponding row
                    user_row = data_frame_source.get(user_id)
                    if not user_row:
                        # It is a new row, create row structure
                        user_row = {
                            'id': user_id,
                            'name': user_name}
                        data_frame_source[user_id] = user_row

                    # Update value in the row
                    user_row[question_name] = answer['text']


def _extract_quiz_submission_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        quiz_id: int,
        data_frame_source: dict):
    submission_start_prefix = '{0}_{1} Canvas Last Submission Start'
    submission_finish_prefix = '{0}_{1} Canvas Last Submission Finished'
    attempt_prefix = '{0}_{1} Canvas Attempts'
    score_prefix = '{0}_{1} Canvas Score'

    quiz_submission = canvas_ops.get_quiz_submissions(
        oauth_info,
        user_token,
        canvas_course_id,
        quiz_id)

    # Loop over all submissions in a quiz
    for submission in quiz_submission['quiz_submissions']:
        # Create the required column names
        submission_start_column_name = submission_start_prefix.format(
            canvas_course_id,
            quiz_id)
        submission_finish_column_name = submission_finish_prefix.format(
            canvas_course_id,
            quiz_id)
        attempt_column_name = attempt_prefix.format(
            canvas_course_id,
            quiz_id)
        score_prefix = score_prefix.format(canvas_course_id, quiz_id)
        user_id = submission['user_id']

        # Get or create the user row
        user_row = data_frame_source.get(user_id)
        if not user_row:
            user_row = {'id': user_id}
            data_frame_source[user_id] = user_row

        # Check if this is a more recent attempt
        if submission['attempt'] > user_row.get(attempt_column_name, 0):
            # This is a more recent, refresh data
            user_row[attempt_column_name] = submission['attempt']
            user_row[score_prefix] = submission['kept_score']
            user_row[submission_start_column_name] = submission['started_at']
            user_row[submission_finish_column_name] = submission['finished_at']


def load_df_from_course_canvas_enrollment_list(
        user: models.OnTaskUser,
        target_url: str,
        course_id: int
) -> pd.DataFrame:
    """Load data frame from a Canvas course enrollment list.

    Given the Canvas target_url and a course ID, obtain the enrollmen list
    and load a dataframe with that list on the current workflow.

    :param user: User object for authentication purposes.
    :param target_url: Name of the Canvas instance to use.
    :param course_id: Canvas Course ID (integer)
    :return: Data Frame after obtaining it from Canvas.
    """

    # Verify parameter
    canvas_course_id = canvas_ops.verify_course_id(course_id)

    # Get the oauth info
    oauth_info, user_token = canvas_ops.get_oauth_and_user_token(
        user,
        target_url)

    students = canvas_ops.get_course_enrolment(
        oauth_info,
        user_token,
        canvas_course_id)

    data_frame_source = []
    for student in students:
        data_frame_source.append({
            'id': student['user']['id'],
            'name': student['user']['name']})

    # Create the data frame with the collected data
    return pd.DataFrame(data_frame_source)


class ExecuteCanvasUploadQuizzes:
    """Process the Canvas upload operation in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.WORKFLOW_DATA_SQL_UPLOAD

    def execute_operation(
        self,
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Perform a Canvas upload asynchronously.

        :param user: User object
        :param workflow: Workflow object
        :param action: Empty
        :param payload: has fields:
          - dst_key: Key column in the existing dataframe (if any) for merge
          - src_key: Key column in the external dataframe (for merge)
          - how_merge: Merge method: inner, outer, left, right
          - canvas_course_id: Unique course id in canvas
          - target_url: URL for the remote canvas instance
        :param log_item: Optional logitem object.
        """
        # Get relevant data from the payload
        canvas_course_id = canvas_ops.verify_course_id(
            payload.get('canvas_course_id'),
            log_item)

        # Authenticate with Canvas

        # Get the oauth info
        oauth_info, user_token = canvas_ops.get_oauth_and_user_token(
            user,
            payload.get('target_url'))

        # Fetch data from canvas and create the src_df

        # Fetch all quizzes for the course
        quizzes = canvas_ops.get_course_quizzes(
            oauth_info,
            user_token,
            canvas_course_id)

        # Build the data frame source with the information from quizzes
        data_frame_source = {}
        for quiz in quizzes:
            quiz_id = quiz['id']

            # Get the answer information
            _extract_quiz_answer_information(
                oauth_info,
                user_token,
                canvas_course_id,
                quiz_id,
                data_frame_source)

            # Get the submission information
            _extract_quiz_submission_information(
                oauth_info,
                user_token,
                canvas_course_id,
                quiz_id,
                data_frame_source)

        # Create the data frame with the collected data
        src_df = pd.DataFrame(data_frame_source.values())

        # Merge or upload the data frame

        # Create session
        session = common.create_session()

        # Lock the workflow for processing
        common.access_workflow(user, session, workflow.id, log_item)

        pandas.perform_dataframe_set_or_update(
            workflow,
            src_df,
            common.get_how_merge(payload, log_item),
            common.get_key(payload, 'src_key', log_item),
            common.get_key(payload, 'dst_key', log_item),
            log_item)
