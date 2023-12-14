"""Common classes to upload data."""
import pandas as pd

from django.urls import reverse

from ontask import models
from ontask.core import UserIsInstructor, WorkflowView
from ontask.dataops import pandas


def validate_and_store_temporary_data_frame(
        workflow: models.Workflow,
        data_frame: pd.DataFrame
) -> dict:
    """Check that the dataframe can be properly stored and store it.

    :return: Dict with information, and frame in the database or Exception
    with anomaly
    """
    # Verify the data frame
    pandas.verify_data_frame(data_frame)

    # Get frame info with three lists: names, types and is_key
    return pandas.store_temporary_dataframe(data_frame, workflow)


class UploadStart(UserIsInstructor, WorkflowView):
    data_type = None
    data_type_select = None
    prev_step_url = 'dataops:uploadmerge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'data_type': self.data_type,
            'data_type_select': self.data_type_select,
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'prev_step': reverse(self.prev_step_url)})
        return context
