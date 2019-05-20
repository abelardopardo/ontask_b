# -*- coding: utf-8 -*-

"""Functions to manipulate Pandas DataFrames an related operations."""

import logging
from typing import Dict, List, Mapping, Optional

import pandas as pd
import sqlalchemy
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.translation import ugettext as _
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from dataops.pandas.datatypes import pandas_datatype_names
from dataops.pandas.columns import has_unique_column, is_unique_column
from dataops.sql import get_select_query_txt
from ontask import OnTaskDataFrameNoKey

logger = logging.getLogger('console')

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


def set_engine():
    """Create a persistmt SQLAlchemy connection to the DB."""
    global engine

    if engine:
        return

    engine = create_db_engine(
        'postgresql',
        '+psycopg2',
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['HOST'],
        settings.DATABASES['default']['NAME'],
    )


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


def destroy_db_engine(db_engine = None):
    """Destroys the DB SQAlchemy engine.

    :param db_engine: Engine to destroy

    :return: Nothing
    """
    global engine

    if db_engine:
        db_engine.dispose()
    else:
        engine.dispose()

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
    return pd.read_sql_table(table_name, engine)


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
                key: ontask_to_sqlalchemy[tvalue]
                for key, tvalue in dtype.items()
            },
        )


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
