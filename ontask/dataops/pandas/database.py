"""Functions to manipulate Pandas DataFrames and related operations."""
from typing import Dict, List, Mapping, Optional
from sqlalchemy.engine.url import URL

import pandas as pd
import sqlalchemy
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.translation import gettext as _

from ontask import LOGGER, OnTaskSharedState, OnTaskDataFrameNoKey
from ontask.dataops import pandas, sql

# Translation between OnTask data types and SQLAlchemy
ONTASK_TO_SQLALCHEMY = {
    'string': sqlalchemy.UnicodeText(),
    'integer': sqlalchemy.BigInteger(),
    'double': sqlalchemy.Float(),
    'boolean': sqlalchemy.Boolean(),
    'datetime': sqlalchemy.DateTime(timezone=True),
}


def set_engine() -> None:
    """Create a persistent SQLAlchemy connection to the DB."""
    if getattr(OnTaskSharedState, 'engine', None):
        return

    OnTaskSharedState.engine = create_db_engine(
        drivername='postgresql+psycopg2',
        username=settings.DATABASES['default'].get('USER'),
        password=settings.DATABASES['default'].get('PASSWORD'),
        host=settings.DATABASES['default'].get('HOST'),
        port=settings.DATABASES['default'].get('PORT'),
        database=settings.DATABASES['default'].get('NAME'))


def create_db_engine(
        drivername: str = None,
        username: str = None,
        password: str = None,
        host: str = None,
        port: int = None,
        database: str = None,
        query: dict = None
):
    """Create SQLAlchemy DB Engine to connect Pandas <-> DB.

    Function that creates the engine object to connect to the database. The
    object is required by the pandas functions to_sql and from_sql

    :param drivername: Dialect (oracle, mysql, postgresql, etc.) and DB API
      driver (psycopg2, ...) for the engine
    :param username: Username to connect with the database
    :param password: Password to connect with the database
    :param host: Host for the connection
    :param port: Port for the connection
    :param database: database name
    :param query: A dictionary with additional parameters for the connection

    :return: the engine

    See create_engine in SQLAlchemy Documentation for details
    """

    engine_url = URL.create(
        drivername,
        username,
        password,
        host,
        port,
        database,
        query)

    if settings.DEBUG:
        LOGGER.debug('Creating engine with database parameters')

    return sqlalchemy.create_engine(
        engine_url,
        client_encoding=str('utf8'),
        echo=False,
        paramstyle='format',
        connect_args={'connect_timeout': 300})


def destroy_db_engine(db_engine=None):
    """Destroys the DB SQAlchemy engine.

    :param db_engine: Engine to destroy
    :return: Nothing
    """
    if db_engine:
        db_engine.dispose()
    else:
        if getattr(OnTaskSharedState, 'engine', None):
            OnTaskSharedState.engine.dispose()


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
        LOGGER.debug('Loading table %s', table_name)

    if columns or filter_exp:
        # A list of columns or a filter exp is given
        query, query_fields = sql.get_select_query_txt(
            table_name,
            column_names=columns,
            filter_formula=filter_exp)
        with OnTaskSharedState.engine.connect() as sqlalchemy_connection:
            data_frame = pd.read_sql_query(
                query,
                sqlalchemy_connection,
                params=tuple(query_fields))
            return data_frame

    # No special fields given, load the whole thing
    with OnTaskSharedState.engine.connect() as sqlalchemy_connection:
        data_frame = pd.read_sql_table(table_name, sqlalchemy_connection)

    return data_frame


def store_table(
    data_frame: pd.DataFrame,
    table_name: str,
    dict_type: Optional[Mapping] = None,
):
    """Store a data frame in the DB.

    dict_type is a dictionary of (column_name, column_type) column type can be:

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
    :param dict_type: dictionary with (column_name, data type) to force the
    storage of certain data types
    :return: Nothing. Side effect in the DB
    """
    # Check the length of the column names
    if any(len(cname) > sql.COLUMN_NAME_SIZE for cname in data_frame.columns):
        raise Exception(
            _('Column name is longer than {0} characters').format(
                sql.COLUMN_NAME_SIZE))

    if dict_type is None:
        dict_type = {}

    with cache.lock(table_name):
        with OnTaskSharedState.engine.connect() as sqlalchemy_connection:
            # We overwrite the content and do not create an index
            data_frame.to_sql(
                table_name,
                sqlalchemy_connection,
                if_exists='replace',
                index=False,
                dtype={
                    key: ONTASK_TO_SQLALCHEMY[type_value]
                    for key, type_value in dict_type.items()})


def verify_data_frame(data_frame: pd.DataFrame):
    """Verify consistency properties in a DF.

    Verify that the data frame complies with the properties:

    1) There is at least one key column

    2) All column names are below the maximum size

    :param data_frame: Data frame to verify
    :return: None or an exception with the description of the problem in the
    text
    """
    # If the data frame does not have any unique key, it is not useful (no
    # way to uniquely identify rows). There must be at least one.
    if not pandas.has_unique_column(data_frame):
        raise OnTaskDataFrameNoKey(_(
            'The data has no column with unique values per row. '
            + 'At least one column must have unique values.'))

    if any(len(cname) > sql.COLUMN_NAME_SIZE for cname in data_frame.columns):
        raise Exception(
            _('Column name is longer than {0} characters').format(
                sql.COLUMN_NAME_SIZE))


def is_table_in_db(table_name: str) -> bool:
    """Check if the given table is in the DB."""
    with connection.cursor() as cursor:
        return table_name in [
            conn.name
            for conn in connection.introspection.get_table_list(cursor)]
