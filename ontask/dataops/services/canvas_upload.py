"""Upload/Merge dataframe from a CANVAS connection."""
from typing import Dict, Optional, Tuple
import pandas as pd
from bs4 import BeautifulSoup

from ontask import models
from ontask.core import canvas_ops, OnTaskDebug
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
            OnTaskDebug.set_trace(answer.get('text', 'No text key in answer'))
            response.append(answer.get('text', ''))
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

    question_names = canvas_ops.get_quiz_questions(
        oauth_info,
        user_token,
        canvas_course_id,
        quiz_id)
    OnTaskDebug.set_trace(
        str([qinfo['question_name'] for qinfo in question_names])
    )
    question_names = dict([
        (
            str(qinfo['id']),
            BeautifulSoup(qinfo['question_name'], 'lxml').text)
        for qinfo in question_names])
    OnTaskDebug.set_trace()

    quiz_stats = canvas_ops.get_quiz_statistics(
        oauth_info,
        user_token,
        canvas_course_id,
        quiz_id)

    # Loop over all elements with quiz statistics
    for qstat in quiz_stats['quiz_statistics']:
        # Loop over all questions
        OnTaskDebug.set_trace('Quiz ID: {}'.format(qstat['id']))
        for question_stat in qstat['question_statistics']:
            _process_question_statistic(
                canvas_course_id,
                quiz_id,
                question_stat,
                question_names,
                data_frame_source)


def _extract_quiz_submission_information(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        canvas_course_id: int,
        quiz_id: int,
        data_frame_source: dict):

    quiz_submission = canvas_ops.get_quiz_submissions(
        oauth_info,
        user_token,
        canvas_course_id,
        quiz_id)

    # Loop over all submissions in a quiz
    for submission in quiz_submission['quiz_submissions']:
        OnTaskDebug.set_trace('Quiz Submission: {0}/{1}/{2}'.format(
            submission['quiz_id'],
            submission['user_id'],
            submission['id']))
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

    assignment_submissions = canvas_ops.get_assignment_submissions(
        oauth_info,
        user_token,
        canvas_course_id,
        assignment_id)

    for submission in assignment_submissions:
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
        if (
                submission['attempt'] and
                submission['attempt'] > user_row.get(attempt_column_name, 0)
        ):
            # This is a more recent submission, refresh data
            user_row[submission_at_column_name] = submission['submitted_at']
            user_row[submission_type] = submission['submission_type']
            user_row[attempt_column_name] = submission['attempt']
            user_row[score_column] = submission['entered_score']


def create_df_from_canvas_course_enrollment(
        user: models.OnTaskUser,
        target_url: str,
        course_id: int
) -> pd.DataFrame:
    """Load data frame from a Canvas course enrollment list.

    Given the Canvas target_url and a course ID, obtain the enrollment list
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
        OnTaskDebug.set_trace('')
        user_details = canvas_ops.get_user_details(
            oauth_info,
            user_token,
            student['user']['id']
        )
        OnTaskDebug.set_trace('')
        data_frame_source.append({
            'id': student['user']['id'],
            'name': user_details[0]['name'],
            'first name': user_details[0]['first_name'],
            'canvas course id': course_id})
        OnTaskDebug.set_trace('')

    # Create the data frame with the collected data
    return pd.DataFrame(data_frame_source)


def create_df_from_canvas_course_quizzes(
        user: models.OnTaskUser,
        target_url: str,
        course_id: int,
        columns_to_upload: list = None
) -> pd.DataFrame:
    """Load data frame from a Canvas with information about quizzes in a course.

    Given the Canvas target_url and a course ID, obtain all the information
    related to quizzes in the course and create a pandas Data Frame.

    :param user: User object for authentication purposes.
    :param target_url: Name of the Canvas instance to use.
    :param course_id: Canvas Course ID (integer)
    :param columns_to_upload: List of columns to upload. Empty means upload all
    :return: Data Frame after obtaining it from Canvas.
    """
    # Verify parameter
    if columns_to_upload is None:
        columns_to_upload = []
    canvas_course_id = canvas_ops.verify_course_id(course_id)

    # Get the oauth info
    oauth_info, user_token = canvas_ops.get_oauth_and_user_token(
        user,
        target_url)

    students = canvas_ops.get_course_enrolment(
        oauth_info,
        user_token,
        canvas_course_id)

    data_frame_source = {}
    for student in students:
        OnTaskDebug.set_trace('Student ID: {}'.format(student['user']['id']))
        student_id = student['user']['id']
        data_frame_source[student_id] = {
            'id': student_id,
            'canvas course id': course_id}

    # Fetch all quizzes for the course
    quizzes = canvas_ops.get_course_quizzes(
        oauth_info,
        user_token,
        canvas_course_id)

    # Build the data frame source with the information from quizzes
    for quiz in quizzes:
        OnTaskDebug.set_trace('Quiz Title: {}'.format(quiz['title']))
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

    # Process the assignment submissions now
    assignments = canvas_ops.get_course_assignments(
        oauth_info,
        user_token,
        canvas_course_id)

    for assignment in assignments:
        OnTaskDebug.set_trace('Course Assignment: {0}'.format(
            assignment['name']))
        # Get the assignment submission information
        _extract_assignment_submission_information(
            oauth_info,
            user_token,
            canvas_course_id,
            assignment['id'],
            data_frame_source)

    # Create the data frame with the collected data
    result = pd.DataFrame(data_frame_source.values())

    # Reorder the columns
    column_names = [
        cname for cname in result.columns.to_list()
        if cname != 'id' and cname != 'name' and cname != 'canvas course id']

    if columns_to_upload:
        # Drop the ones that are not in the columns to upload
        column_names = [
            cname for cname in column_names if cname in columns_to_upload]

    # # Insert canvas course id field
    # result.loc[:, 'canvas course id'] = canvas_course_id
    #
    # Sort the columns leaving ID as the first one
    result = result[['id', 'canvas course id'] + sorted(column_names)]

    return result


class ExecuteCanvasUploadBasic:
    @staticmethod
    def execute_dataframe_update(
            user: models.OnTaskUser,
            workflow: models.Workflow,
            data_frame: pd.DataFrame,
            payload: dict,
            log_item: models.Log
    ):
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


class ExecuteCanvasCourseEnrollmentsUpload(ExecuteCanvasUploadBasic):
    """Process the Canvas Course Enrollment Upload operation in a workflow."""
    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = (
            models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD)

    @staticmethod
    def execute_operation(
        user,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None,
        payload: Optional[Dict] = None,
        log_item: Optional[models.Log] = None,
    ):
        """Perform a Canvas Course Enrollment upload asynchronously.

        :param user: User object
        :param workflow: Workflow object
        :param action: Empty
        :param payload: has fields:
          - dst_key: Key column in the existing dataframe (if any) for merge
          - src_key: Key column in the external dataframe (for merge)
          - how_merge: Merge method: inner, outer, left, right
          - canvas_course_id: Unique course id in canvas
          - target_url: URL for the remote canvas instance
        :param log_item: Optional log item object.
        """
        # Create the data frame with the collected data
        src_df = create_df_from_canvas_course_enrollment(
            user,
            payload.get('target_url'),
            payload.get('canvas_course_id'))

        # Update the dataframe
        super(
            ExecuteCanvasCourseEnrollmentsUpload,
            ExecuteCanvasCourseEnrollmentsUpload
        ).execute_dataframe_update(
            user,
            workflow,
            src_df,
            payload,
            log_item)


class ExecuteCanvasCourseQuizzesUpload(ExecuteCanvasUploadBasic):
    """Process the Canvas Course Quizzes upload operation in a workflow."""

    def __init__(self):
        """Assign default fields."""
        super().__init__()
        self.log_event = models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD

    @staticmethod
    def execute_operation(
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
        :param log_item: Optional log item object.
        """
        # Create the data frame with the collected data
        src_df = create_df_from_canvas_course_quizzes(
            user,
            payload.get('target_url'),
            payload.get('canvas_course_id'),
            payload.get('columns_to_upload'))

        # Update the dataframe
        super(
            ExecuteCanvasCourseQuizzesUpload,
            ExecuteCanvasCourseQuizzesUpload
        ).execute_dataframe_update(
            user,
            workflow,
            src_df,
            payload,
            log_item)
