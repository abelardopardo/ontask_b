"""Upload/Merge dataframe from a CANVAS connection."""
from typing import Dict, Optional, Tuple
import pandas as pd
from bs4 import BeautifulSoup

from ontask import models
from ontask.core import canvas_ops
from ontask.dataops.services import common
from ontask.dataops import pandas

question_prefix = '{0}_{1}_{2} {3}'
submission_at_prefix = '{0}_{1} Submission At'
submission_start_prefix = '{0}_{1} Last Submission Start'
submission_finish_prefix = '{0}_{1} Last Submission Finished'
attempt_prefix = '{0}_{1} Attempts'
score_prefix = '{0}_{1} Score'
submission_type_prefix = '{0}_{1} Submission Type'


def _create_submission_names(
        canvas_course_id: int,
        assignment_quiz_id: int,
) -> Tuple[str, str, str, str, str]:
    """Create column names given the course, assignment and quiz IDs

    :param canvas_course_id: Integer with the course id
    :param assignment_quiz_id: Integer with the assignment id
    :return submission_at, submission_start, submission_finish, attempt, score
    """

    return (
        submission_at_prefix.format(
            canvas_course_id,
            assignment_quiz_id),
        submission_start_prefix.format(
            canvas_course_id,
            assignment_quiz_id),
        submission_finish_prefix.format(
            canvas_course_id,
            assignment_quiz_id),
        attempt_prefix.format(
            canvas_course_id,
            assignment_quiz_id),
        score_prefix.format(canvas_course_id, assignment_quiz_id)
    )


def _process_question_answers(
        answers: list,
        question_name: str,
        data_frame_source: dict
):
    """Traverse the "answers" structure and collect student-> text info."""
    to_concat = set()
    for answer in answers:
        if answer.get('responses', 0) == 0:
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
            response = user_row.get(question_name, [])
            response.append(answer['text'])
            user_row[question_name] = response
            to_concat.add(user_id)

    # concat the answers for the given set of users
    for user_id in to_concat:
        user_row = data_frame_source[user_id]
        user_row[question_name] = ' |&&| '.join(user_row[question_name])


def _process_question_statistic(
        canvas_course_id: int,
        quiz_id: int,
        question_stat: dict,
        question_names: dict,
        data_frame_source: dict
):
    """Process the answers in a question.

    The process contemplates four type of questions as stated in 'question_type'
    - multiple_answers_question,
    - true_false_question,
    - multiple_choice_question,
    - fill_in_multiple_blanks_question

    The result is reflected in the data_frame_source.
    """
    question_type = question_stat['question_type']
    question_name = question_prefix.format(
        canvas_course_id,
        quiz_id,
        question_stat['id'],
        question_names[question_stat['id']])

    if question_type == 'fill_in_multiple_blanks_question':
        answers = []
        for answer_set in question_stat['answer_sets']:
            # Concatenate answers in all answer sets
            answers.extend(answer_set['answers'])
    else:
        # These are the remaining cases:
        # - multiple_answers_question
        # - true_false_question
        # - multiple_choice_question
        answers = question_stat['answers']

    _process_question_answers(answers, question_name, data_frame_source)


def _extract_quiz_answer_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        quiz_id: int,
        data_frame_source: dict):

    question_names = canvas_ops.request_and_access(
        'get_quiz_questions',
        oauth_info,
        user_token,
        [canvas_course_id, quiz_id])
    question_names = dict([
        (
            str(qinfo['id']),
            BeautifulSoup(qinfo['question_name'], 'lxml').text)
        for qinfo in question_names])

    quiz_stats = canvas_ops.request_and_access(
        'get_quiz_statistics',
        oauth_info,
        user_token,
        [canvas_course_id, quiz_id],
        result_key='quiz_statistics')

    # Loop over all elements with quiz statistics
    for qstat in quiz_stats['quiz_statistics']:
        # Loop over all questions
        for question_stat in qstat['question_statistics']:
            _process_question_statistic(
                canvas_course_id,
                quiz_id,
                question_stat,
                question_names,
                data_frame_source)


def _extract_enrollment_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        data_frame_source: dict):
    """Extract enrollment information from Canvas and add to given data frame

    :param oauth_info: Oauth info to connect to Canvas
    :param user_token: User token to authorize the canvas connection
    :param canvas_course_id: Canvas course
    :param data_frame_source: Data frame to expand with the data
    """

    students = canvas_ops.request_and_access(
        'get_course_enrolment',
        oauth_info,
        user_token,
        [canvas_course_id, 'active'])

    for student in students:
        user_id = student['user']['id']
        user_value = {
            'id': user_id,
            'name': student['user']['name']}
        user_row = data_frame_source.get(user_id)
        if not user_row:
            user_row = user_value
            data_frame_source[user_id] = user_row
        user_row.update(user_value)


def _extract_quiz_submission_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        quiz_id: int,
        data_frame_source: dict):

    quiz_submission = canvas_ops.request_and_access(
        'get_quiz_submissions',
        oauth_info,
        user_token,
        [canvas_course_id, quiz_id],
        result_key='quiz_submissions')

    # Loop over all submissions in a quiz
    for submission in quiz_submission['quiz_submissions']:
        # Create the required column names
        (
            _,
            submission_start_column_name,
            submission_finish_column_name,
            attempt_column_name,
            score_column_name
        ) = _create_submission_names(canvas_course_id, quiz_id)

        user_id = submission['user_id']

        # Get or create the user row
        user_row = data_frame_source.get(user_id)
        if not user_row:
            user_row = {'id': user_id}
            data_frame_source[user_id] = user_row

        # Check if this is a more recent attempt
        if (
                submission['attempt'] and
                submission['attempt'] > user_row.get(attempt_column_name, 0)
        ):
            # This is a more recent submission, refresh data
            user_row[submission_start_column_name] = submission['started_at']
            user_row[submission_finish_column_name] = submission['finished_at']
            user_row[attempt_column_name] = submission['attempt']
            user_row[score_column_name] = submission['kept_score']


def _extract_assignment_submission_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        assignment_id: int,
        data_frame_source: dict):

    assignment_submissions = canvas_ops.request_and_access(
        'get_assignment_submissions',
        oauth_info,
        user_token,
        [canvas_course_id, assignment_id])

    for submission in assignment_submissions:
        if not submission['attempt']:
            # Submission with no attempts, skip
            continue

        (
            submission_at_column_name,
            _,
            _,
            attempt_column_name,
            score_column
        ) = _create_submission_names(canvas_course_id, assignment_id)

        submission_type = submission_type_prefix.format(
            canvas_course_id,
            assignment_id)
        user_id = submission['user_id']

        # Get or create the user row
        user_row = data_frame_source.get(user_id)
        if not user_row:
            user_row = {'id': user_id}
            data_frame_source[user_id] = user_row

        # Check if this is a more recent attempt
        if submission['attempt'] > user_row.get(attempt_column_name, 0):
            # This is a more recent submission, refresh data
            user_row[submission_at_column_name] = submission['submitted_at']
            user_row[submission_type] = submission['submission_type']
            user_row[attempt_column_name] = submission['attempt']
            user_row[score_column] = submission['entered_score']


def create_df_from_canvas_course(
        user: models.OnTaskUser,
        target_url: str,
        course_id: int,
        upload_enrollment: bool,
        upload_quizzes: bool,
        upload_assignments: bool,
        include_course_id_column: bool,
        columns_to_upload: list = None
) -> pd.DataFrame:
    """Create a data frame from the information in a canvas course

    :param user: OnTaskUser performing the operation
    :param target_url: URL of the Canvas server
    :param course_id: Canvas course
    :param upload_enrollment: Whether to upload the enrollment information
    :param upload_quizzes: Whether to upload the quizzes information
    :param upload_assignments: Whether to upload the assignments information
    :param include_course_id_column: Whether to include a course id column
    :param columns_to_upload: Columns in the workflow to upload
    :return: The Pandas data frame with the extracted information
    """
    # Verify parameter
    canvas_course_id = canvas_ops.verify_course_id(course_id)

    columns_to_upload = [] if columns_to_upload is None else columns_to_upload

    # Get the oauth info
    oauth_info, user_token = canvas_ops.get_oauth_and_user_token(
        user,
        target_url)

    # List of dictionaries to then create the Data Frame
    data_frame_source = {}

    # Upload Enrollments
    if upload_enrollment:
        _extract_enrollment_information(
            oauth_info,
            user_token,
            canvas_course_id,
            data_frame_source)

    # Upload Quizzes
    if upload_quizzes:
        # Fetch all quizzes for the course
        quizzes = canvas_ops.request_and_access(
            'get_course_quizzes',
            oauth_info,
            user_token,
            [course_id])

        # Build the data frame source with the information from quizzes
        for quiz in quizzes:
            quiz_id = quiz['id']

            # Get the answer information
            _extract_quiz_answer_information(
                oauth_info,
                user_token,
                canvas_course_id,
                quiz_id,
                data_frame_source)

            # Get the quiz submission information
            _extract_quiz_submission_information(
                oauth_info,
                user_token,
                canvas_course_id,
                quiz_id,
                data_frame_source)

    # Upload Assignments
    if upload_assignments:
        # Get all the assignments in a course
        assignments = canvas_ops.request_and_access(
            'get_course_assignments',
            oauth_info,
            user_token,
            [canvas_course_id])

        for assignment in assignments:
            # Get the assignment submission information
            _extract_assignment_submission_information(
                oauth_info,
                user_token,
                canvas_course_id,
                assignment['id'],
                data_frame_source)

    # Create the data frame with the collected data
    result = pd.DataFrame(data_frame_source.values())

    if include_course_id_column:
        # Insert column with course id if required
        result['canvas course id'] = canvas_course_id

    # Reorder the columns
    column_names = [
        cname for cname in result.columns.to_list()
        if cname != 'id' and cname != 'name' and cname != 'canvas course id']

    if columns_to_upload:
        # Drop the ones that are not in the columns to upload
        column_names = [
            cname for cname in column_names if cname in columns_to_upload]

    head_column_names = ['id']
    if upload_enrollment:
        # If the enrollment has been updated, include name as head column
        head_column_names.append('name')

    if include_course_id_column:
        # If the canvas course id column was added, include it as head column
        head_column_names.append('canvas course id')

    # Sort the columns leaving ID as the first one
    result = result[head_column_names + sorted(column_names)]

    return result


class ExecuteCanvasCourseUpload:
    @staticmethod
    def execute_operation(
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Perform a Canvas Course Upload asynchronously.

        :param user: User object
        :param workflow: Workflow object
        :param action: Empty
        :param payload: has fields:
          - dst_key: Key column in the existing dataframe (if any) for merge
          - src_key: Key column in the external dataframe (for merge)
          - how_merge: Merge method: inner, outer, left, right
          - canvas_course_id: Unique course id in canvas
          - target_url: URL for the remote canvas instance
          - upload_enrollment: Whether to upload the enrollment information
          - upload_quizzes: Whether to upload the quizzes information
          - upload_assignments: Whether to upload the assignments information
          - include_course_id_column: Whether to include a course id column
          - columns_to_upload: Columns in the workflow to upload
        :param log_item: Optional log item object.
        """
        data_frame = create_df_from_canvas_course(
            user,
            payload.pop('target_url'),
            payload.pop('canvas_course_id'),
            payload.pop('upload_enrollment'),
            payload.pop('upload_quizzes'),
            payload.pop('upload_assignments'),
            payload.pop('include_course_id_column'),
            payload.pop('columns_to_upload'))

        # Create session
        session = common.create_session()

        # Lock the workflow for processing
        common.access_workflow(user, session, workflow.id, log_item)

        # Merge or upload the data frame
        pandas.perform_dataframe_set_or_update(
            workflow,
            data_frame,
            common.get_how_merge(payload, log_item),
            common.get_key(payload, 'src_key', log_item),
            common.get_key(payload, 'dst_key', log_item),
            log_item)
