"""Initialise the scheduler CRUD factory."""
from ontask.scheduler.services.edit_factory import SchedulerCRUDFactory

SCHEDULE_CRUD_FACTORY = SchedulerCRUDFactory()


def initialize_schedule_factory():
    from ontask.models import Action, Log
    from ontask.scheduler import services

    # Catalogue of Schedule. Tuples have:
    # - Operation Type: Log model value
    # - Class performing the CRUD operations
    schedule_catalogue = [
        (
            Action.PERSONALIZED_TEXT,
            services.ScheduledOperationEmailUpdateView),
        (
            Action.PERSONALIZED_CANVAS_EMAIL,
            services.ScheduledOperationCanvasEmailUpdateView),
        (
            Action.EMAIL_REPORT,
            services.ScheduledOperationEmailReportUpdateView),
        (
            Action.RUBRIC_TEXT,
            services.ScheduledOperationEmailUpdateView),
        (
            Action.PERSONALIZED_JSON,
            services.ScheduledOperationJSONUpdateView),
        (
            Action.JSON_REPORT,
            services.ScheduledOperationJSONReportUpdateView),
        (
            Log.WORKFLOW_DATA_SQL_UPLOAD,
            services.ScheduledOperationUpdateSQLUpload),
        (
            Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD,
            services.ScheduledOperationUpdateCanvasCourseEnrollmentUpload),
        (
            Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD,
            services.ScheduledOperationUpdateCanvasCourseQuizzesUpload)]

    for op_type, class_name in schedule_catalogue:
        SCHEDULE_CRUD_FACTORY.register_producer(op_type, class_name)
