"""Factory to execute the different operations."""
from typing import Any

from ontask import core, models
from ontask.action import services as action_services
from ontask.dataops import services as dataops_services
from ontask.workflow import services as workflow_services
from ontask.dataops.services.sql_upload import ExecuteSQLUpload
from ontask.dataops.services.canvas_upload import (
    ExecuteCanvasCourseQuizzesUpload, ExecuteCanvasCourseEnrollmentsUpload)


class TaskExecuteFactory(core.FactoryBase):
    """Factory to execute scheduled operations."""

    def execute_operation(self, operation_type, **kwargs) -> Any:
        """Execute the given operation.

        Invoke the object that implements the following method
        def execute_operation(
            self,
            user,
            workflow: Optional[models.Workflow] = None,
            action: Optional[models.Action] = None,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
        ):

        :param operation_type: String encoding the type of operation
        :param kwargs: Parameters passed to execution
        :return: Whatever is returned by the execution
        """
        try:
            producer_cls = self._get_producer(operation_type)
        except ValueError:
            return

        return producer_cls().execute_operation(**kwargs)


TASK_EXECUTE_FACTORY = TaskExecuteFactory()

# PERSONALIZED TEXT
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.ACTION_RUN_PERSONALIZED_EMAIL,
    action_services.ActionRunProducerEmail)

# EMAIL REPORT
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.ACTION_RUN_EMAIL_REPORT,
    action_services.ActionRunProducerEmailReport)

# PERSONALIZED JSON
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.ACTION_RUN_PERSONALIZED_JSON,
    action_services.ActionRunProducerJSON)

# JSON REPORT
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.ACTION_RUN_JSON_REPORT,
    action_services.ActionRunProducerJSONReport)

# CANVAS PERSONALIZED EMAIL
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL,
    action_services.ActionRunProducerCanvasEmail)

# INCREASE TRACK COUNT FOR MESSAGE
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.WORKFLOW_INCREASE_TRACK_COUNT,
    dataops_services.ExecuteIncreaseTrackCount)

# EXECUTE A PLUGIN
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.PLUGIN_EXECUTE,
    dataops_services.ExecuteRunPlugin)

# EXECUTE AN SQL UPLOAD
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.WORKFLOW_DATA_SQL_UPLOAD,
    ExecuteSQLUpload)

# EXECUTE A CANVAS COURSE ENROLLMENT UPLOAD
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD,
    ExecuteCanvasCourseEnrollmentsUpload)

# EXECUTE A CANVAS COURSE QUIZZES UPLOAD
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD,
    ExecuteCanvasCourseQuizzesUpload)

# UPDATE LUSER FIELD IN WORKFLOW
# ------------------------------------------------------------------------------
TASK_EXECUTE_FACTORY.register_producer(
    models.Log.WORKFLOW_UPDATE_LUSERS,
    workflow_services.ExecuteUpdateWorkflowLUser)
