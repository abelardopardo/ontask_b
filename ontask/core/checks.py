# -*- coding: utf-8 -*-

"""Functions to perform various checks."""
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.dataops import pandas, sql


def _check_logs(workflow: models.Workflow) -> bool:
    """Check that all logs are correctly created.

    :param workflow: Workflow being processed.
    :result: True or a failed assertion
    """
    assert(workflow.logs.exclude(name__in=models.Log.LOG_TYPES).count() == 0)
    return True


def check_wf_df(workflow: models.Workflow) -> bool:
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
            'Inconsistent data type {0}'.format(col.name)
        )

    # Verify that the columns marked as unique are preserved
    for col in workflow.columns.filter(is_key=True):
        assert pandas.is_unique_column(df[col.name]), (
            'Column {0} should be unique.'.format(col.name)
        )

    # Columns are properly numbered
    cpos = workflow.columns.values_list('position', flat=True)
    rng = range(1, len(cpos) + 1)
    assert sorted(cpos) == list(rng)

    return True


def sanity_checks() -> bool:
    """Perform various sanity checks for consistency.

    :result: True or an assertion fail
    """
    for workflow in models.Workflow.objects.all():
        check_wf_df(workflow)

        _check_logs(workflow)

    return True


def check_key_columns(workflow: models.Workflow):
    """Check that key columns maintain their property.

    Function used to verify that after changes in the DB the key columns
    maintain their property.

    :param workflow: Object to use for the verification.
    :return: Nothing. Raise exception if key column lost the property.
    """
    col_name = next(
        (
            col.name for col in workflow.columns.filter(is_key=True)
            if not sql.is_column_unique(
                workflow.get_data_frame_table_name(),
                col.name)),
        None)
    if col_name:
        raise Exception(_(
            'The new data does not preserve the key '
            + 'property of column "{0}"'.format(col_name)))
