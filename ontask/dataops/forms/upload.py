# -*- coding: utf-8 -*-

"""Forms to perform the first step of data upload in several formats.

The currently supported formats are:

- CSV file

- Excel file (with sheet name)

- GoogleSheet file (with a URL)

- AWS S3 Bucket file

- SQL connection to a remote DB
"""
from builtins import str
from io import TextIOWrapper
import json
from typing import Dict, Optional

from django import forms
from django.utils.translation import gettext_lazy as _
import pandas as pd

from ontask import OnTaskDataFrameNoKey, models, settings
from ontask.core import RestrictedFileField
from ontask.dataops import pandas, services

URL_FIELD_SIZE = 1024


class UploadBasic(forms.Form):
    """Basic class to use for inheritance."""

    def __init__(self, *args, **kwargs):
        """Store the workflow for further processing."""
        self.data_frame: Optional[pd.DataFrame] = None
        self.frame_info = None
        self.workflow = kwargs.pop(str('workflow'), None)
        super().__init__(*args, **kwargs)

    def validate_data_frame(self):
        """Check that the dataframe can be properly stored.

        :return: The cleaned data
        """
        try:
            # Verify the data frame
            pandas.verify_data_frame(self.data_frame)
        except OnTaskDataFrameNoKey as exc:
            self.add_error(None, str(exc))
            return

        # Store the data frame in the DB.
        try:
            # Get frame info with three lists: names, types and is_key
            self.frame_info = pandas.store_temporary_dataframe(
                self.data_frame,
                self.workflow)
        except Exception as exc:
            self.add_error(
                None,
                _('Unable to process file ({0}).').format(str(exc)))


# Step 1 of the CSV upload
class UploadCSVFileForm(UploadBasic):
    """Form to read a csv file.

    It also allows to specify the number of lines to
    skip at the top and the bottom of the file. This functionality is offered
    by the underlyng function read_csv in Pandas
    """

    data_file = RestrictedFileField(
        max_upload_size=int(settings.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(settings.CONTENT_TYPES)),
        allow_empty_file=False,
        label='',
        help_text=_(
            'File in CSV format (typically produced by a statistics'
            + ' package or Excel)'))

    skip_lines_at_top = forms.IntegerField(
        label=_('Lines to skip at the top'),
        help_text=_(
            'Number of lines to skip at the top when reading the file'),
        initial=0,
        required=False)

    skip_lines_at_bottom = forms.IntegerField(
        label=_('Lines to skip at the bottom'),
        help_text=_(
            'Number of lines to skip at the bottom when reading the file'),
        initial=0,
        required=False)

    def clean(self) -> Dict:
        """Check that the integers are positive.

        :return: The cleaned data
        """
        # The form must be multipart
        if not self.is_multipart():
            self.add_error(
                None,
                _('CSV upload form is not multiform'),
            )
            return {}

        form_data = super().clean()

        if form_data['skip_lines_at_top'] < 0:
            self.add_error(
                'skip_lines_at_top',
                _('This number has to be zero or positive'),
            )
            return form_data

        if form_data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                _('This number has to be zero or positive'),
            )
            return form_data

        # Process CSV file using pandas read_csv
        try:
            self.data_frame = services.load_df_from_csvfile(
                TextIOWrapper(
                    self.files['data_file'].file,
                    encoding=self.data.encoding),
                self.cleaned_data['skip_lines_at_top'],
                self.cleaned_data['skip_lines_at_bottom'])
        except Exception as exc:
            self.add_error(
                None,
                _('File could not be processed ({0})').format(str(exc)))
            return form_data

        # Check the validity of the data frame
        self.validate_data_frame()

        return form_data


# Step 1 of the Excel upload
class UploadExcelFileForm(UploadBasic):
    """Form to read an Excel file."""

    data_file = RestrictedFileField(
        max_upload_size=int(settings.MAX_UPLOAD_SIZE),
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.'
            + 'spreadsheetml.sheet',
        ],
        allow_empty_file=False,
        label='',
        help_text=_('File in Excel format (.xls or .xlsx)'))

    sheet = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        required=True,
        initial='',
        help_text=_('Sheet within the excelsheet to upload'))

    def clean(self) -> Dict:
        """Check that the data can be loaded from the file.

        :return: The cleaned data
        """
        form_data = super().clean()

        # # Process Excel file using pandas read_excel
        try:
            self.data_frame = services.load_df_from_excelfile(
                self.files['data_file'],
                form_data['sheet'])
        except Exception as exc:
            self.add_error(
                None,
                _('File could not be processed: {0}').format(str(exc)))
            return form_data

        # Check the validity of the data frame
        self.validate_data_frame()

        return form_data


# Step 1 of the GoogleSheet upload
class UploadGoogleSheetForm(UploadBasic):
    """Form to read a Google Sheet file through a URL.

    It also allows to specify the number of lines to skip at the top and the
    bottom of the file. This functionality is offered by the underlyng
    function read_csv in Pandas
    """

    google_url = forms.CharField(
        max_length=URL_FIELD_SIZE,
        strip=True,
        required=True,
        label=_('URL'),
        help_text=_('URL to access the Google Spreadsheet in CSV format'))

    skip_lines_at_top = forms.IntegerField(
        label=_('Lines to skip at the top'),
        help_text=_(
            'Number of lines to skip at the top when reading the file'),
        initial=0,
        required=False)

    skip_lines_at_bottom = forms.IntegerField(
        label=_('Lines to skip at the bottom'),
        help_text=_(
            'Number of lines to skip at the bottom when reading the file'),
        initial=0,
        required=False)

    def clean(self) -> Dict:
        """Check that the data can be loaded from the URL.

        :return: The cleaned data
        """
        form_data = super().clean()

        if form_data['skip_lines_at_top'] < 0:
            self.add_error(
                'skip_lines_at_top',
                _('This number has to be zero or positive'))
            return form_data

        if form_data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                _('This number has to be zero or positive'))
            return form_data

        try:
            self.data_frame = services.load_df_from_googlesheet(
                form_data['google_url'],
                self.cleaned_data['skip_lines_at_top'],
                self.cleaned_data['skip_lines_at_bottom'])
        except Exception as exc:
            self.add_error(
                None,
                _('File could not be processed: {0}').format(str(exc)))
            return form_data

        # Check the validity of the data frame
        self.validate_data_frame()

        return form_data


# Step 1 of the S3 CSV upload
class UploadS3FileForm(UploadBasic):
    """Form to read a csv file from a S3 bucket.

    It requires entering the access key as well as the secret access key. It
    also allows to specify the number of lines to skip at the top and the
    bottom of the file. This functionality is offered by the underlyng
    function read_csv in Pandas
    """

    aws_access_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        required=False,
        initial='',
        help_text=_('AWS S3 Bucket access key'))

    aws_secret_access_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        required=False,
        initial='',
        help_text=_('AWS S3 Bucket secret access key'))

    aws_bucket_name = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        required=True,
        initial='',
        help_text=_('AWS S3 Bucket name'))

    aws_file_key = forms.CharField(
        max_length=models.CHAR_FIELD_MID_SIZE,
        required=True,
        initial='',
        help_text=_('AWS S3 Bucket file path'))

    skip_lines_at_top = forms.IntegerField(
        label=_('Lines to skip at the top'),
        help_text=_(
            'Number of lines to skip at the top when reading the file'),
        initial=0,
        required=False)

    skip_lines_at_bottom = forms.IntegerField(
        label=_('Lines to skip at the bottom'),
        help_text=_(
            'Number of lines to skip at the bottom when reading the file'),
        initial=0,
        required=False)

    def clean(self) -> Dict:
        """Check that the integers are positive.

        :return: The cleaned data
        """
        resp_data = super().clean()

        if resp_data['skip_lines_at_top'] < 0:
            self.add_error(
                'skip_lines_at_top',
                _('This number has to be zero or positive'),
            )
            return resp_data

        if resp_data['skip_lines_at_bottom'] < 0:
            self.add_error(
                'skip_lines_at_bottom',
                _('This number has to be zero or positive'),
            )
            return resp_data

        # Process S3 file using pandas read_excel
        try:
            self.data_frame = services.load_df_from_s3(
                self.cleaned_data['aws_access_key'],
                self.cleaned_data['aws_secret_access_key'],
                self.cleaned_data['aws_bucket_name'],
                self.cleaned_data['aws_file_key'],
                self.cleaned_data['skip_lines_at_top'],
                self.cleaned_data['skip_lines_at_bottom'])
        except Exception as exc:
            self.add_error(
                None,
                _('S3 bucket file could not be processed: {0}').format(
                    str(exc)),
            )
            return resp_data

        # Check the validity of the data frame
        self.validate_data_frame()

        return resp_data
