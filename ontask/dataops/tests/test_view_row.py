"""Test the views to update or create new rews."""

from django.urls import reverse
from rest_framework import status

from ontask import tests
from ontask.dataops import sql, views


class DataopsViewsRowBasic(
    tests.TestConditionEvaluationFixture,
    tests.OnTaskTestCase,
):
    """Test the views to create and update the row values."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class DataopsViewsRowCreate(DataopsViewsRowBasic):

    def test(self):
        nrows = self.workflow.nrows

        # Row create (GET)
        resp = self.get_response('dataops:rowcreate')
        self.assertTrue(status.is_success(resp.status_code))

        # Row create POST
        resp = self.get_response(
            'dataops:rowcreate',
            method='POST',
            req_params={
                '___ontask___upload_0': '8',
                '___ontask___upload_1': 'text1',
                '___ontask___upload_2': 'text2',
                '___ontask___upload_3': '12.1',
                '___ontask___upload_4': '12.2',
                '___ontask___upload_5': 'on',
                '___ontask___upload_6': '',
                '___ontask___upload_7': '06/07/2019 19:32',
                '___ontask___upload_8': '06/05/2019 19:23'})
        self.assertTrue(status.is_success(resp.status_code))

        # Update the workflow
        self.workflow.refresh_from_db()
        self.assertEqual(nrows, self.workflow.nrows)

        # Row create POST
        resp = self.get_response(
            'dataops:rowcreate',
            method='POST',
            req_params={
                '___ontask___upload_0': '9',
                '___ontask___upload_1': 'text add 1',
                '___ontask___upload_2': 'text add 2',
                '___ontask___upload_3': '22',
                '___ontask___upload_4': '23',
                '___ontask___upload_5': 'on',
                '___ontask___upload_7': '06/07/2019 19:32',
                '___ontask___upload_8': '06/05/2019 19:23'})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        # Update the workflow
        self.workflow.refresh_from_db()
        self.assertEqual(nrows + 1, self.workflow.nrows)

        row_val = sql.get_row(
            self.workflow.get_data_frame_table_name(),
            key_name='key',
            key_value=9)
        self.assertEqual(row_val['text1'], 'text add 1')
        self.assertEqual(row_val['text2'], 'text add 2')
        self.assertEqual(row_val['double1'], 22)
        self.assertEqual(row_val['double2'], 23)


class DataopsViewsRowEdit(DataopsViewsRowBasic):

    def test(self):
        # Row edit (GET)
        resp = self.get_response(
            'dataops:rowupdate',
            req_params={'k': 'key', 'v': '8'})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('Edit learner data' in str(resp.content))

        # Get the GET URL with the paramegters
        request = self.factory.get(
            reverse('dataops:rowupdate'),
            {'k': 'key', 'v': '8'})

        request = self.factory.post(
            request.get_full_path(),
            {
                '___ontask___upload_0': '8',
                '___ontask___upload_1': 'NEW TEXT 1',
                '___ontask___upload_2': 'NEW TEXT 2',
                '___ontask___upload_3': '111',
                '___ontask___upload_4': '222',
                '___ontask___upload_5': 'on',
                '___ontask___upload_6': '',
                '___ontask___upload_7': '06/07/2019 19:32',
                '___ontask___upload_8': '06/05/2019 19:23'}
        )
        request = self.add_middleware(request)
        resp = views.RowUpdateView.as_view()(request)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        row_val = sql.get_row(
            self.workflow.get_data_frame_table_name(),
            key_name='key',
            key_value=8)

        self.assertEqual(row_val['text1'], 'NEW TEXT 1')
        self.assertEqual(row_val['text2'], 'NEW TEXT 2')
        self.assertEqual(row_val['double1'], 111)
        self.assertEqual(row_val['double2'], 222)
