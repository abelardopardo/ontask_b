# -*- coding: utf-8 -*-

"""Upload DataFrames from Files."""
from typing import Optional, Dict
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import pandas as pd
from django.conf import settings
from smart_open import smart_open

from ontask.dataops.pandas import create_db_engine
from ontask.models import SQLConnection, AthenaConnection


def _process_object_column(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Perform additional steps in every object dataframe column.

    The process includes:

    1) Strip empty spaces

    2) Try date/time conversion

    3) If the previous fails, replace NaN with None as it will be done once it
    is dumped and reloaded from the DB

    :param data_frame:

    :return: new data frame
    """
    for column in list(data_frame.columns):
        if data_frame[column].dtype.name == 'object':
            if all(
                isinstance(x, bool) or pd.isna(x) for x in data_frame[column]
            ):
                # Column contains booleans + NaN, skip
                continue

            # Column is a string! Remove the leading and trailing white
            # space
            data_frame[column] = data_frame[column].str.strip().fillna(
                data_frame[column])

            # Try the datetime conversion
            try:
                series = pd.to_datetime(
                    data_frame[column],
                    infer_datetime_format=True,
                    utc=True)
            except (ValueError, TypeError):
                # Datetime failed. Rows with no value may be read as NaN from
                # the read CSV but will turn into None when looping through the
                # DB, so ensure consistency.
                data_frame[column] = data_frame[column].where(
                    pd.notnull(data_frame[column]),
                    None)
            else:
                # Datetime conversion worked!
                # If the series has not time zone information, locaize it
                if series.dt.tz is None:
                    data_frame[column] = series.dt.tz_localize(
                        'UTC').dt.tz_convert(settings.TIME_ZONE)
                # Make sure the series is in local time.
                data_frame[column] = series.dt.tz_convert(
                    settings.TIME_ZONE)

    return data_frame


def load_df_from_csvfile(
    file_obj,
    skiprows: Optional[int] = 0,
    skipfooter: Optional[int] = 0,
) -> pd.DataFrame:
    """Load a data frame from a CSV file.

    Given a file object, try to read the content as a CSV file and transform
    into a data frame. The skiprows and skipfooter are number of lines to skip
    from the top and bottom of the file (see read_csv in pandas).

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param file_obj: File object to read the CSV content

    :param skiprows: Number of lines to skip at the top of the document

    :param skipfooter: Number of lines to skip at the bottom of the document

    :return: Resulting data frame, or an Exception.
    """
    data_frame = pd.read_csv(
        file_obj,
        index_col=False,
        infer_datetime_format=True,
        quotechar='"',
        skiprows=skiprows,
        skipfooter=skipfooter,
        encoding='utf-8')

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return _process_object_column(data_frame)


def load_df_from_excelfile(file_obj, sheet_name: str) -> pd.DataFrame:
    """Load a data frame from a sheet in an excel file.

    Given a file object, try to read the content as a Excel file and transform
    into a data frame. The sheet_name is the name of the sheet to read.

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param file_obj: File object to read the CSV content

    :param sheet_name: Sheet in the file to read

    :return: Resulting data frame, or an Exception.
    """
    data_frame = pd.read_excel(
        file_obj,
        sheet_name=sheet_name,
        index_col=False,
        infer_datetime_format=True,
        quotechar='"')

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return _process_object_column(data_frame)


def load_df_from_s3(
    aws_key: str,
    aws_secret: str,
    bucket_name: str,
    file_path: str,
    skiprows: Optional[int] = 0,
    skipfooter: Optional[int] = 0,
) -> pd.DataFrame:
    """Load data from a S3 bucket.

    Given a file object, try to read the content and transform it into a data
    frame.

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param aws_key: Key to access the S3 bucket

    :param aws_secret: Secret to access the S3 bucket

    :param bucket_name: Bucket name

    :param file_path: Path to access the file within the bucket

    :param skiprows: Number of lines to skip at the top of the document

    :param skipfooter: Number of lines to skip at the bottom of the document

    :return: Resulting data frame, or an Exception.
    """
    path_prefix = ''
    if aws_key and aws_secret:
        # If key/secret are given, create prefix
        path_prefix = '{0}:{1}@'.format(aws_key, aws_secret)

    data_frame = pd.read_csv(
        smart_open('s3://{0}{1}/{2}'.format(
            path_prefix,
            bucket_name,
            file_path)),
        index_col=False,
        infer_datetime_format=True,
        quotechar='"',
        skiprows=skiprows,
        skipfooter=skipfooter,
        encoding='utf-8',
    )

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return _process_object_column(data_frame)


def load_df_from_googlesheet(
    url_string: str,
    skiprows: Optional[int] = 0,
    skipfooter: Optional[int] = 0,
) -> pd.DataFrame:
    """Load a Pandas DataFrame from a google sheet.

    Given a file object, try to read the content as a CSV file and transform
    into a data frame. The skiprows and skipfooter are number of lines to skip
    from the top and bottom of the file (see read_csv in pandas).

    It also tries to convert as many columns as possible to date/time format
    (testing the conversion on every string column).

    :param url_string: URL where the file is available

    :param skiprows: Number of lines to skip at the top of the document

    :param skipfooter: Number of lines to skip at the bottom of the document

    :return: Resulting data frame, or an Exception.
    """
    # Process the URL provided by google. If the URL is obtained using the
    # GUI, it has as suffix /edit?[parameters]. This part needs to be
    # replaced by the suffix /export?format=csv
    # For example from:
    # https://docs.google.com/spreadsheets/d/DOCID/edit?usp=sharing
    # to
    # https://docs.google.com/spreadsheets/d/DOCID/export?format=csv&gid=0
    parse_res = urlparse(url_string)
    if parse_res.path.endswith('/edit'):
        qs_dict = parse_qs(parse_res.query)
        qs_dict['format'] = 'csv'
        new_fragment = parse_res.fragment
        if 'gid=' in parse_res.fragment:
            qs_dict['gid'] = parse_res.fragment.split('=')[1]
            new_fragment = ''

        url_string = urlunparse([
            parse_res.scheme,
            parse_res.netloc,
            parse_res.path.replace('/edit', '/export'),
            parse_res.params,
            urlencode(qs_dict, doseq=True),
            new_fragment,
        ])

    # Process the link using pandas read_csv
    return load_df_from_csvfile(url_string, skiprows, skipfooter)


def load_df_from_sqlconnection(
    conn_item: SQLConnection,
    run_params: Dict,
) -> pd.DataFrame:
    """Load a DF from a SQL connection.

    :param conn_item: SQLConnection object with the connection parameters.

    :param password: Password

    :return: Data frame or raise an exception.
    """
    # Get the engine from the DB
    db_engine = create_db_engine(
        conn_item.conn_type,
        conn_item.conn_driver,
        conn_item.db_user,
        run_params['password'],
        conn_item.db_host,
        conn_item.db_name)

    # Try to fetch the data
    data_frame = pd.read_sql_table(run_params['db_table'], db_engine)

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return _process_object_column(data_frame)


def load_df_from_athenaconnection(
    conn_item: AthenaConnection,
    run_params: Dict,
) -> pd.DataFrame:
    """Load a DF from an Athena connection.

    run_params has:
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    table_name: Optional[str] = None

    from pyathena import connect
    from pyathena.pandas_cursor import PandasCursor

    cursor = connect(aws_access_key_id='YOUR_ACCESS_KEY_ID',
               aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
               aws_session_token='YOUR_SESSION_TOKEN',
               s3_staging_dir='s3://YOUR_S3_BUCKET/path/to/',
               region_name='us-west-2',
               cursor_class=PandasCursor).cursor()

    df = cursor.execute("SELECT * FROM many_rows").as_pandas()
    print(df.describe())
    print(df.head())

    :param conn_item: AthenaConnection object with the connection parameters.

    :param table_name: table name

    :return: Data frame or raise an exception.
    """
    # TODO: Implement this function
    data_frame = pd.DataFrame()

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return _process_object_column(data_frame)
