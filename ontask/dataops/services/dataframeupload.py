# -*- coding: utf-8 -*-

"""Upload DataFrames from various sources."""
from typing import Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings
from django.utils.translation import ugettext as _
import pandas as pd
from pyathena import connect
import smart_open

from ontask import models
from ontask.dataops import pandas, sql


def process_object_column(data_frame: pd.DataFrame) -> pd.DataFrame:
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
    return process_object_column(data_frame)


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
    return process_object_column(data_frame)


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

    if settings.ONTASK_TESTING:
        uri = 'file:///{1}/{2}'.format(
            path_prefix,
            bucket_name,
            file_path)
    else:
        uri = 's3://{0}{1}/{2}'.format(
            path_prefix,
            bucket_name,
            file_path)
    data_frame = pd.read_csv(
        smart_open.open(uri),
        index_col=False,
        infer_datetime_format=True,
        quotechar='"',
        skiprows=skiprows,
        skipfooter=skipfooter,
        encoding='utf-8',
    )

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    return process_object_column(data_frame)


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


def batch_load_df_from_athenaconnection(
    workflow: models.Workflow,
    conn: models.AthenaConnection,
    run_params: Dict,
    log_item: models.Log
):
    """Batch load a DF from an Athena connection.

    run_params has:
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    table_name: Optional[str] = None
    key_column_name[str] = None
    merge_method[str] = None

    from pyathena import connect
    from pyathena.pandas_cursor import PandasCursor

    cursor = connect(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        s3_staging_dir=staging_dir,
        region_name=region_name)

    df = pd.read_sql('SELECT * FROM given_table_name', cursor)
    print(df.describe())
    print(df.head())

    :param workflow: Workflow to store the new data
    :param conn: AthenaConnection object with the connection parameters.
    :param run_params: Dictionary with additional connection parameters
    :param log_item: Log object to reflect the status of the execution
    :return: Nothing.
    """
    staging_dir = 's3://{0}'.format(conn.aws_bucket_name)
    if conn.aws_file_path:
        staging_dir = staging_dir + '/' + conn.aws_file_path

    cursor = connect(
        aws_access_key_id=conn.aws_access_key,
        aws_secret_access_key=run_params['aws_secret_access_key'],
        aws_session_token=run_params['aws_session_token'],
        s3_staging_dir=staging_dir,
        region_name=conn.aws_region_name)

    data_frame = pd.read_sql(
        'SELECT * FROM {0}'.format(run_params['table_name']),
        cursor)

    # Strip white space from all string columns and try to convert to
    # datetime just in case
    data_frame = process_object_column(data_frame)

    pandas.verify_data_frame(data_frame)

    col_names, col_types, is_key = pandas.store_temporary_dataframe(
        data_frame,
        workflow)

    upload_data = {
        'initial_column_names': col_names,
        'col_types': col_types,
        'src_is_key_column': is_key,
        'rename_column_names': col_names[:],
        'columns_to_upload': [True] * len(col_names),
        'keep_key_column': is_key[:]}

    if not workflow.has_data_frame():
        # Regular load operation
        pandas.store_workflow_table(workflow, upload_data)
        log_item.payload['col_names'] = col_names,
        log_item.payload['col_types'] = col_types,
        log_item.payload['column_unique'] = is_key
        log_item.payload['num_rows'] = workflow.nrows
        log_item.payload['num_cols'] = workflow.ncols
        log_item.save()
        return

    # Merge operation
    upload_data['dst_column_names'] = workflow.get_column_names()
    upload_data['dst_is_unique_column'] = workflow.get_column_unique()
    upload_data['dst_unique_col_names'] = [
        cname for idx, cname in enumerate(upload_data['dst_column_names'])
        if upload_data['dst_column_names'][idx]]
    upload_data['src_selected_key'] = run_params['merge_key']
    upload_data['dst_selected_key'] = run_params['merge_key']
    upload_data['how_merge'] = run_params['merge_method']

    dst_df = pandas.load_table(workflow.get_data_frame_table_name())
    src_df = pandas.load_table(workflow.get_data_frame_upload_table_name())

    try:
        pandas.perform_dataframe_upload_merge(
            workflow,
            dst_df,
            src_df,
            upload_data)
    except Exception as exc:
        # Nuke the temporary table
        sql.delete_table(workflow.get_data_frame_upload_table_name())
        raise Exception(_('Unable to perform merge operation: {0}').format(
            str(exc)))

    col_names, col_types, is_key = workflow.get_column_info()
    log_item.payload['col_names'] = col_names,
    log_item.payload['col_types'] = col_types,
    log_item.payload['column_unique'] = is_key
    log_item.payload['num_rows'] = workflow.nrows
    log_item.payload['num_cols'] = workflow.ncols
    log_item.save()
