# -*- coding: utf-8 -*-

"""Functions to manipulate Pandas DataFrames an related operations."""

import logging
from builtins import next
from typing import Dict, List, Mapping, Optional

import pandas as pd
import sqlalchemy
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.translation import ugettext as _
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from dataops.sql_query import get_rows, get_select_query_txt
from ontask import OnTaskDataFrameNoKey

logger = logging.getLogger('console')


class TypeDict(dict):
    """Class to detect multiple datetime types in Pandas."""

    def get(self, key):
        """Detect if given key is equal to any stored value."""
        return next(
            otype for dtype, otype in self.items() if key.startswith(dtype)
        )


# Translation between pandas data type names, and those handled in OnTask
pandas_datatype_names = TypeDict({
    'object': 'string',
    'int64': 'integer',
    'float64': 'double',
    'bool': 'boolean',
    'datetime64[ns': 'datetime',
})

# Translation between OnTask data types and SQLAlchemy
ontask_to_sqlalchemy = {
    'string': sqlalchemy.UnicodeText(),
    'integer': sqlalchemy.BigInteger(),
    'double': sqlalchemy.Float(),
    'boolean': sqlalchemy.Boolean(),
    'datetime': sqlalchemy.DateTime(timezone=True),
}

# SQLAlchemy DB Engine to use with Pandas (required by to_sql, from_sql
engine: Optional[Engine] = None


def create_db_engine(
    dialect: str,
    driver: str,
    username: str,
    password: str,
    host: str,
    dbname: str,
):
    """Create SQLAlchemy DB Engine to connect Pandas <-> DB.

    Function that creates the engine object to connect to the database. The
    object is required by the pandas functions to_sql and from_sql

    :param dialect: Dialect for the engine (oracle, mysql, postgresql, etc)
    :param driver: DBAPI driver (psycopg2, ...)
    :param username: Username to connect with the database
    :param password: Password to connect with the database
    :param host: Host to connect with the database
    :param dbname: database name
    :return: the engine
    """
    # DB engine
    database_url = '{dial}{drv}://{usr}:{pwd}@{h}/{dbname}'.format(
        dial=dialect,
        drv=driver,
        usr=username,
        pwd=password,
        h=host,
        dbname=dbname,
    )

    if settings.DEBUG:
        logger.debug(
            'Creating engine: {db_url}',
            extra={'db_url': database_url})

    return create_engine(
        database_url,
        client_encoding=str('utf8'),
        encoding=str('utf8'),
        echo=False,
        paramstyle='format')


def destroy_db_engine(db_engine):
    """Destroys the DB SQAlchemy engine.

    :param db_engine: Engine to destroy

    :return: Nothing
    """
    db_engine.dispose()


def load_table(
    table_name: str,
    columns: Optional[List[str]] = None,
    filter_exp: Optional[Dict] = None,
) -> Optional[pd.DataFrame]:
    """Load a Pandas data frame from the SQL DB.

    :param table_name: Table name

    :param columns: Optional list of columns to load (all if NOne is given)

    :param filter_exp: JSON expression to filter a subset of rows

    :return: data frame
    """
    if table_name not in connection.introspection.table_names():
        return None

    if settings.DEBUG:
        logger.debug('Loading table {tbl}', extra={'tbl': table_name})

    if columns or filter_exp:
        # A list of columns or a filter exp is given
        query, query_fields = get_select_query_txt(
            table_name,
            column_names=columns,
            filter_formula=filter_exp)
        return pd.read_sql_query(query, engine, params=query_fields)

    # No special fields given, load the whole thing
    return pd.read_sql(table_name, engine)


def store_table(
    data_frame: pd.DataFrame,
    table_name: str,
    dtype: Optional[Mapping] = None,
):
    """Store a data frame in the DB.

    dtype is a dictionary of (column_name, column_type) column type can be:

    - 'boolean',
    - 'datetime',
    - 'double',
    - 'integer',
    - 'string'

    The function will use these to translate into (respectively)

    - sqlalchemy.Boolean()
    - sqlalchemy.DateTime()
    - sqlalchemy.Float()
    - sqlalchemy.BigInteger()
    - sqlalchemy.UnicodeText()

    :param data_frame: The data frame to store

    :param table_name: The name of the table in the DB

    :param dtype: dictionary with (column_name, data type) to force the storage
    of certain data types

    :return: Nothing. Side effect in the DB
    """
    if dtype is None:
        dtype = {}

    with cache.lock(table_name):
        # We ovewrite the content and do not create an index
        data_frame.to_sql(
            table_name,
            engine,
            if_exists='replace',
            index=False,
            dtype={
                (key, ontask_to_sqlalchemy[tvalue])
                for key, tvalue in dtype.items()
            },
        )


def get_subframe(table_name, filter_formula, column_names) -> pd.DataFrame:
    """Load the subframe using the filter and column names.

    Execute a select query to extract a subset of the dataframe and turn the
     resulting query set into a data frame.

    :param table_name: Table

    :param filter_formula: Formula to filter the data (or None)

    :param column_names: [list of column names], QuerySet with the data rows

    :return: DataFrame
    """
    # Create the DataFrame and set the column names
    return pd.DataFrame.from_records(
        get_rows(
            table_name,
            column_names,
            filter_formula,
        ).fetchall(),
        columns=column_names,
        coerce_float=True)


def get_column_statistics(df_column):
    """Calculate a set of statistics or a DataFrame columm.

    Given a data frame with a single column, return a set of statistics
    depending on its type.

    :param df_column: data frame with a single column

    :return: A dictionary with keys depending on the type of column
      {'min': minimum value (integer, double an datetime),
       'q1': Q1 value (0.25) (integer, double),
       'mean': mean value (integer, double),
       'median': median value (integer, double),
       'mean': mean value (integer, double),
       'q3': Q3 value (0.75) (integer, double),
       'max': maximum value (integer, double an datetime),
       'std': standard deviation (integer, double),
       'counts': (integer, double, string, datetime, Boolean',
       'mode': (integer, double, string, datetime, Boolean,
       or None if the column has all its values to NaN
    """
    if len(df_column.loc[df_column.notnull()]) == 0:
        # The column has no data
        return None

    # Dictionary to return
    to_return = {
        'min': 0,
        'q1': 0,
        'mean': 0,
        'median': 0,
        'q3': 0,
        'max': 0,
        'std': 0,
        'mode': None,
        'counts': {},
    }

    data_type = pandas_datatype_names.get(df_column.dtype.name)

    if data_type == 'integer' or data_type == 'double':
        quantiles = df_column.quantile([0, .25, .5, .75, 1])
        to_return['min'] = '{0:g}'.format(quantiles[0])
        to_return['q1'] = '{0:g}'.format(quantiles[.25])
        to_return['mean'] = '{0:g}'.format(df_column.mean())
        to_return['median'] = '{0:g}'.format(quantiles[.5])
        to_return['q3'] = '{0:g}'.format(quantiles[.75])
        to_return['max'] = '{0:g}'.format(quantiles[1])
        to_return['std'] = '{0:g}'.format(df_column.std())

    to_return['counts'] = df_column.value_counts().to_dict()
    mode = df_column.mode()
    if len(mode) == 0:
        mode = '--'
    to_return['mode'] = mode[0]

    return to_return


def check_wf_df(workflow):
    """Check consistency between Workflow info and the data frame.

    Check the consistency between the information stored in the workflow
    and the structure of the underlying dataframe

    :param workflow: Workflow object

    :return: Boolean stating the result of the check. True: Correct.
    """
    # Get the df
    df = load_table(workflow.get_data_frame_table_name())

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
        df_dt = pandas_datatype_names.get(df[col.name].dtype.name)
        if col.data_type == 'boolean' and df_dt == 'string':
            # This is the case of a column with Boolean and Nulls
            continue

        assert col.data_type == df_dt, (
            'Inconsistent data type {0}'.format(col.name)
        )

    # Verify that the columns marked as unique are preserved
    for col in workflow.columns.filter(is_key=True):
        assert is_unique_column(df[col.name]), (
            'Column {0} should be unique.'.format(col.name)
        )

    return True


def is_unique_column(df_column):
    """Check if a column has unique non-empty values.

    :param df_column: Column of a pandas data frame

    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.dropna().unique()) == len(df_column)


def are_unique_columns(data_frame: pd.DataFrame) -> List[bool]:
    """Check if columns have unique non-empty values.

    :param data_frame: Pandas data frame

    :return: Array of Booleans stating of a column has unique values
    """
    return [
        is_unique_column(data_frame[col]) for col in list(data_frame.columns)
    ]


def has_unique_column(data_frame: pd.DataFrame) -> bool:
    """Verify if the data frame has a unique column.

    :param data_frame:

    :return: Boolean with the result
    """
    return any(
        is_unique_column(data_frame[col]) for col in data_frame.columns
    )


def verify_data_frame(data_frame: pd.DataFrame) -> None:
    """Verify consistency properties in a DF.

    Verify that the data frame complies with two properties:
    1) The names of the columns are all different
    2) There is at least one key column

    :param data_frame: Data frame to verify

    :return: None or an exception with the descripton of the problem in the
    text
    """
    # If the data frame does not have any unique key, it is not useful (no
    # way to uniquely identify rows). There must be at least one.
    if not has_unique_column(data_frame):
        raise OnTaskDataFrameNoKey(_(
            'The data has no column with unique values per row. '
            + 'At least one column must have unique values.'),
        )

    return None
