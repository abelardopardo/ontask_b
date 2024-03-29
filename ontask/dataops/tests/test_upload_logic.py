"""Test the upload operation."""
import os

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from ontask import tests


class DataopsUploadBasic(tests.EmptyWorkflowFixture, tests.OnTaskTestCase):
    """Test the upload code."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class DataopsCSVUpload(DataopsUploadBasic):
    """Test the upload code."""

    def test(self):
        # Get the regular form
        resp = self.get_response('dataops:csvupload_start')
        self.assertTrue(status.is_success(resp.status_code))

        # POST the data
        filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple.csv')
        with open(filename) as fp:
            resp = self.get_response(
                'dataops:csvupload_start',
                method='POST',
                req_params={
                    'data_file': fp,
                    'skip_lines_at_top': 0,
                    'skip_lines_at_bottom': 0})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('dataops:upload_s2'))


class DataopsExcelUpload(DataopsUploadBasic):
    """Test the Excel upload code."""

    def test(self):
        # Get the regular form
        resp = self.get_response('dataops:excel_upload_start')
        self.assertTrue(status.is_success(resp.status_code))

        # POST the data
        filename = os.path.join(
            settings.ONTASK_FIXTURE_DIR,
            'excel_upload.xlsx')
        with open(filename, 'rb') as fp:
            resp = self.get_response(
                'dataops:excel_upload_start',
                method='POST',
                req_params={'data_file': fp, 'sheet': 'results'})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('dataops:upload_s2'))


class DataopsGoogleUpload(DataopsUploadBasic):
    """Test the Google upload code."""

    def test(self):
        # Get the regular form
        resp = self.get_response('dataops:googlesheetupload_start')
        self.assertTrue(status.is_success(resp.status_code))

        # POST the data
        filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple.csv')
        resp = self.get_response(
            'dataops:googlesheetupload_start',
            method='POST',
            req_params={
                'google_url': 'file://' + filename,
                'skip_lines_at_top': 0,
                'skip_lines_at_bottom': 0})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('dataops:upload_s2'))


class DataopsS3Upload(DataopsUploadBasic):
    """Test the S3 upload code."""

    def test(self):
        # Get the regular form
        resp = self.get_response('dataops:s3upload_start')
        self.assertTrue(status.is_success(resp.status_code))

        # POST the data
        filepath = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple.csv')
        resp = self.get_response(
            'dataops:s3upload_start',
            method='POST',
            req_params={
                'aws_bucket_name': filepath.split('/')[1],
                'aws_file_key': '/'.join(filepath.split('/')[2:]),
                'skip_lines_at_top': 0,
                'skip_lines_at_bottom': 0,
                'domain': 'file:/'})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('dataops:upload_s2'))
