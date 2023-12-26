"""Import packages and initialize the TASK_EXECUTE_FACTORY."""
from ontask.tasks.execute_factory import TaskExecuteFactory

TASK_EXECUTE_FACTORY = TaskExecuteFactory()


def initialize_task_factory():
    # Initialize TASK FACTORY
    from ontask.models import Log
    from ontask.action import services as action_services
    from ontask.dataops import services as dataops_services
    from ontask.workflow import services as workflow_services
    from ontask.dataops.services.sql_upload import ExecuteSQLUpload
    from ontask.dataops.services.canvas_upload import (
        ExecuteCanvasCourseQuizzesUpload,
        ExecuteCanvasCourseEnrollmentsUpload)

    # Catalogue of Tasks. Tuples have:
    # - Operation Type: Log model value
    # - Class performing the task execution
    task_catalogue = [
        # PERSONALIZED TEXT
        (Log.ACTION_RUN_PERSONALIZED_EMAIL,
         action_services.ActionRunProducerEmail),
        # EMAIL REPORT
        (Log.ACTION_RUN_EMAIL_REPORT,
         action_services.ActionRunProducerEmailReport),
        # PERSONALIZED JSON
        (Log.ACTION_RUN_PERSONALIZED_JSON,
         action_services.ActionRunProducerJSON),
        # JSON REPORT
        (Log.ACTION_RUN_JSON_REPORT,
         action_services.ActionRunProducerJSONReport),
        # CANVAS PERSONALIZED EMAIL
        (Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL,
         action_services.ActionRunProducerCanvasEmail),
        # INCREASE TRACK COUNT FOR MESSAGE
        (Log.WORKFLOW_INCREASE_TRACK_COUNT,
         dataops_services.ExecuteIncreaseTrackCount),
        # EXECUTE A PLUGIN
        (Log.PLUGIN_EXECUTE, dataops_services.ExecuteRunPlugin),
        # EXECUTE AN SQL UPLOAD
        (Log.WORKFLOW_DATA_SQL_UPLOAD, ExecuteSQLUpload),
        # EXECUTE A CANVAS COURSE ENROLLMENT UPLOAD
        (Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD,
         ExecuteCanvasCourseEnrollmentsUpload),
        # EXECUTE A CANVAS COURSE QUIZZES UPLOAD
        (Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD,
         ExecuteCanvasCourseQuizzesUpload),
        # UPDATE LUSER FIELD IN WORKFLOW
        (Log.WORKFLOW_UPDATE_LUSERS,
         workflow_services.ExecuteUpdateWorkflowLUser),
    ]

    for op_type, class_name in task_catalogue:
        TASK_EXECUTE_FACTORY.register_producer(op_type, class_name)
