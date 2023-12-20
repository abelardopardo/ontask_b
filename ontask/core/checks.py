"""Functions to perform various checks."""
from datetime import datetime
from typing import List, Set, Optional
from zoneinfo import ZoneInfo

from django import db
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.dataops import pandas, sql


def _check_logs(workflow: models.Workflow) -> bool:
    """Check that all logs are correctly created.

    :param workflow: Workflow being processed.
    :result: True or a failed assertion
    """
    assert (not (workflow.logs.exclude(
        name__in=models.Log.LOG_TYPES).exists()))
    return True


def check_workflow(workflow: models.Workflow) -> bool:
    """Check consistency between Workflow info and the data frame.

    Check the consistency between the information stored in the workflow
    and the structure of the underlying dataframe

    :param workflow: Workflow object
    :return: Boolean stating the result of the check. True: Correct.
    """
    # Get the df
    df = pandas.load_table(workflow.get_data_frame_table_name())

    # Set values in case there is no df
    if df is not None:
        dfnrows = df.shape[0]
        dfncols = df.shape[1]
        df_col_names = list(df.columns)
    else:
        dfnrows = 0
        dfncols = 0
        df_col_names = []

    # Check 1: Number of rows and columns
    assert workflow.nrows == dfnrows, 'Inconsistent number of rows'
    assert workflow.ncols == dfncols, 'Inconsistent number of columns'

    # Identical sets of columns
    wf_cols = workflow.columns.all()
    assert set(df_col_names) == {col.name for col in wf_cols}, (
        'Inconsistent set of columns'
    )

    # Identical data types
    # for n1, n2 in zip(wf_cols, df_col_names):
    for col in wf_cols:
        df_dt = pandas.datatype_names.get(df[col.name].dtype.name)
        if col.data_type == 'boolean' and df_dt == 'string':
            # This is the case of a column with Boolean and Nulls
            continue

        assert col.data_type == df_dt, (
            'Inconsistent data type {0}: workflow = {1}, data = {2}'.format(
                col.name,
                col.data_type,
                df_dt
            )
        )

    # Verify that the columns marked as unique are preserved
    for col in workflow.columns.filter(is_key=True):
        assert pandas.is_unique_series(df[col.name]), (
            'Column {0} should be unique.'.format(col.name)
        )

    # Columns are properly numbered
    cpos = workflow.columns.values_list('position', flat=True)
    rng = range(1, len(cpos) + 1)
    assert sorted(cpos) == list(rng)

    # Verify the name of the workflow
    assert (
        workflow.data_frame_table_name
        == workflow.df_table_prefix.format(workflow.id)), \
        'Inconsistent table name'

    # Verify the sanity of all the actions
    for action in workflow.actions.all():
        check_action(action)

    return True


def check_action(action: models.Action) -> bool:
    """Check consistency in Action object.

    Perform various sanity checks for an action

    :param action: Workflow object
    :return: Boolean stating the result of the check. True: Correct.
    """

    # Conditions should not have the number of columns equal to zero and should
    # not be filters.
    for cond in action.conditions.all():
        assert cond.columns.exists()

    return True


def sanity_checks() -> bool:
    """Perform various sanity checks for consistency.

    :result: True or an assertion fail
    """
    for workflow in models.Workflow.objects.all():
        check_workflow(workflow)

        _check_logs(workflow)

    return True


def check_key_columns(workflow: models.Workflow):
    """Check that key columns maintain their property.

    Function used to verify that after changes in the DB the key columns
    maintain their property.

    :param workflow: Object to use for the verification.
    :return: Nothing. Raise exception if key column lost the property.
    """
    col_name = next((
        col.name for col in workflow.columns.filter(is_key=True)
        if not sql.is_column_unique(
            workflow.get_data_frame_table_name(),
            col.name)),
        None)
    if col_name:
        raise Exception(_(
            'The new data does not preserve the key '
            + 'property of column "{0}"'.format(col_name)))


def fix_non_unique_object_names(
        obj_names: Set[str],
        duplicates: List[db.models.Model],
):
    """Rename objects to remove duplicated names.

    :param obj_names: Names currently existing that need to be unique
    :param duplicates: Objects with duplicated names
    :return: Reflect changes in the database
    """

    # Process each duplicated object to change the name
    for obj in duplicates:
        suffix = 1
        while obj.name in obj_names:
            # While the name is in the obj_names, keep increasing suffix
            obj.name = obj.name + '_' + str(suffix)
            obj.save()
            suffix += 1


def validate_crontab(time_from, frequency, time_until) -> Optional[str]:
    """Verify that fields time_from, frequency and time_until are correct.

    This method is intended to verify the consistency of a definition of a
    time interval (from time_from until time_until) with an optional
    "crontab" style string stipulating the frequency.

    There are eight possible combinations when specifying the time_from,
    frequency and time_until parameters depending on their values:

    1) None, None, None: ERROR. Something is needed
    2) None, None, True: ERROR. Only time_until is given.
    3) None, True, None: Never ending frequency starting immediately.
    4) None, True, True: Frequency and an expiry date.
    5) True, None, None: SINGLE time instance at a given date/time.
    6) True, None, True: ERROR: Missing frequency.
    7) True, True, None: Frequency starts in the future, never stops.
    8) True, True, True: Frequency starting and stopping at a given time.

    :param time_from: Datetime when time starts
    :param frequency: String with a crontab format
    :param time_until: Datetime to when time stops
    :return: Error message string, or Nothing if everything is fine.
    """
    if not time_from and not frequency:
        # Cases 1 and 2
        return _('Incorrect execution time specification.')

    # From and Until are given, but there is no frequency.
    if time_from and not frequency and time_until:
        # Case 6
        return _('Frequency of execution is missing.')

    now = datetime.now(ZoneInfo(settings.TIME_ZONE))
    if time_until and time_until < now:
        # Case 4 and 8 when current date/time is later
        return _('Execution times in the past. No execution possible.')

    if time_from and not frequency and not time_until and time_from < now:
        # Case 5 when the start time is in the past
        return _('Execution time is in the past. No execution possible.')

    if time_from and time_until and time_until < time_from:
        return _('Incorrect execution dates.')

    return None
