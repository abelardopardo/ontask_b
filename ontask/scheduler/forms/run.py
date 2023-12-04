"""Forms required to schedule Action Run"""
from ontask.action import forms as action_forms
from ontask.scheduler.forms import ScheduleBasicForm


class ScheduleEmailForm(ScheduleBasicForm, action_forms.EmailActionForm):
    """Form to create/edit objects of the ScheduleAction of type email.

    One of the fields is a reference to a key column, which is a subset of
    the columns attached to the action. The subset is passed as the name
    arguments "columns" (list of key columns).

    There is an additional field to allow for an extra step to review and
    filter email addresses.
    """

    def __init__(self, *args, **kwargs):
        """Set field order."""
        super().__init__(*args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until',
            'item_column',
            'subject',
            'cc_email',
            'bcc_email',
            'confirm_items',
            'send_confirmation',
            'track_read'])


class ScheduleCanvasEmailForm(
    ScheduleBasicForm,
    action_forms.CanvasEmailActionForm
):
    """Form to edit ScheduleAction of types Canvas Email."""

    def __init__(self, *args, **kwargs):
        """Set field order."""
        super().__init__(*args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute',
            'multiple_executions',
            'frequency',
            'execute_until',
            'item_column',
            'subject'])


class ScheduleSendListForm(ScheduleBasicForm, action_forms.SendListActionForm):
    """Form to create/edit objects of the ScheduleAction of type send list."""

    def __init__(self, *args, **kwargs):
        """Set field order."""
        super().__init__(*args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until',
            'email_to',
            'subject',
            'cc_email',
            'bcc_email'])


class ScheduleJSONForm(ScheduleBasicForm, action_forms.JSONActionForm):
    """Form to edit ScheduleAction of type JSON."""

    def __init__(self, *args, **kwargs):
        """Set field order."""
        super().__init__(*args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until',
            'item_column',
            'confirm_items',
            'token'])


class ScheduleJSONReportForm(
    ScheduleBasicForm,
    action_forms.JSONReportActionForm
):
    """Form to edit ScheduleAction of types JSON Report."""

    def __init__(self, *args, **kwargs):
        """Set field order."""
        super().__init__(*args, **kwargs)
        self.order_fields([
            'name',
            'description_text',
            'execute_start',
            'multiple_executions',
            'frequency',
            'execute_until',
            'token'])
