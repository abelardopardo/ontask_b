# -*- coding: utf-8 -*-

"""Test the table API.s"""

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
import pandas as pd
from rest_framework import status
from rest_framework.authtoken.models import Token

from ontask import models, tests
from ontask.column.services import delete_column
from ontask.dataops import pandas
from ontask.table import serializers


class TableApiBase(tests.OnTaskApiTestCase, tests.SimpleTableFixture):
    """Basic function and data for testing the API."""

    new_table = {
        "email": ["student04@bogus.com",
                  "student05@bogus.com",
                  "student06@bogus.com"
                  ],
        "sid": [4, 5, 6],
        "age": [122.0, 122.1, 132.2],
        "another": ["bbbb", "aaab", "bbbb"],
        "name": ["Felipe Lotas", "Aitor Tilla", "Carmelo Coton"],
        "one": ["aaaa", "bbbb", "aaaa"],
        "registered": [True, False, True],
        "when": ["2017-10-12T00:33:44+11:00",
                 "2017-10-12T00:32:44+11:00",
                 "2017-10-12T00:32:44+11:00"
                 ]
    }

    incorrect_table_1 = {
        "email": {
            "0": "student1@bogus.com",
            "1": "student2@bogus.com",
            "2": "student3@bogus.com",
            "3": "student1@bogus.com"
        },
        "Another column": {
            "0": 6.93333333333333,
            "1": 9.1,
            "2": 9.1,
            "3": 5.03333333333333
        },
        "Quiz": {
            "0": 1,
            "1": 0,
            "2": 3,
            "3": 0
        }
    }

    src_df = {
        "sid": [1, 2, 4],
        "newcol": ['v1', 'v2', 'v3']
    }

    src_df2 = {
        "sid": [5],
        "forcenas": ['value']
    }

    user_name = 'instructor01@bogus.com'

    def setUp(self):
        super().setUp()
        # Get the token for authentication and set credentials in client
        token = Token.objects.get(user__email=self.user_name)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.user = get_user_model().objects.get(email=self.user_name)


class TableApiJSONGet(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_ops', kwargs={'wid': workflow.id}))

        # Transform the response into a data frame
        r_df = pd.DataFrame(response.data['data_frame'])
        r_df = pandas.detect_datetime_columns(r_df)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiPandasGet(TableApiBase):
    """Test the api to create a table."""

    # Getting the table attached to the workflow
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_pops', kwargs={'wid': workflow.id}))

        # Transform the response into a data frame
        r_df = serializers.string_to_df(response.data['data_frame'])

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiJSONOverwrite(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Upload a table and try to overwrite an existing one (should fail)

        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Override the table
        response = self.client.post(
            reverse(
                'table:api_ops',
                kwargs={'wid': workflow.id}),
            self.new_table,
            format='json')

        # Check that the right message is returned
        self.assertIn(
            'Post request requires workflow without a table',
            response.data['detail'])


class TableApiPandasOverwrite(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Upload a table and try to overwrite an existing one (should fail)

        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Override the table
        response = self.client.post(
            reverse(
                'table:api_pops',
                kwargs={'wid': workflow.id}),
            self.new_table,
            format='json')

        # Check that the right message is returned
        self.assertIn(
            'Post request requires workflow without a table',
            response.data['detail'])


class TableApiJSONCreate(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': tests.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.get(id=response.data['id'])

        # Upload the table
        self.client.post(
            reverse('table:api_ops', kwargs={'wid': workflow.id}),
            {'data_frame': self.new_table},
            format='json')

        # Refresh wflow (has been updated)
        workflow = models.Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())
        # Transform new table into data frame
        r_df = pd.DataFrame(self.new_table)
        r_df = pandas.detect_datetime_columns(r_df)

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiJSONCreateError(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': tests.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.get(id=response.data['id'])

        # Upload the table
        response = self.client.post(
            reverse('table:api_ops', kwargs={'wid': workflow.id}),
            {'data_frame': self.incorrect_table_1},
            format='json')

        self.assertTrue(
            'The data has no column with unique values per row' in
            response.data
        )


class TableApiPandasCreate(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': tests.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.get(id=response.data['id'])

        # Transform new table into a data frame
        r_df = pd.DataFrame(self.new_table)
        r_df = pandas.detect_datetime_columns(r_df)

        # Upload the table
        self.client.post(
            reverse('table:api_pops', kwargs={'wid': workflow.id}),
            {'data_frame': serializers.df_to_string(r_df)},
            format='json')

        # Refresh wflow (has been updated)
        workflow = models.Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiJSONUpdate(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)
        r_df = pandas.detect_datetime_columns(r_df)

        # Upload a new table
        self.client.put(
            reverse(
                'table:api_ops',
                kwargs={'wid': workflow.id}),
            {'data_frame': self.new_table},
            format='json')

        # Refresh wflow (has been updated)
        workflow = models.Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiPandasUpdate(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)
        r_df = pandas.detect_datetime_columns(r_df)

        # Upload a new table
        self.client.put(
            reverse(
                'table:api_pops',
                kwargs={'wid': workflow.id}),
            {'data_frame': serializers.df_to_string(r_df)},
            format='json')

        # Refresh wflow (has been updated)
        workflow = models.Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, dframe)


class TableApiJSONFlush(TableApiBase):
    """Test the api to create a table."""

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Flush the data in the table
        self.client.delete(reverse(
            'table:api_ops',
            kwargs={'wid': workflow.id}))


class TableApiPandasFlush(TableApiBase):
    """Test the api to create a table."""

    def test_table_pandas_flush(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Flush the data in the table
        self.client.delete(
            reverse('table:api_pops', kwargs={'wid': workflow.id}))


class TableApiMergePandasJSONGet(TableApiBase):

    # Getting the table through the merge API
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_merge', kwargs={'wid': workflow.id}))

        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(response.data['src_df'])
        r_df = pandas.detect_datetime_columns(r_df)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(r_df, dframe)


class TableApiMergePandasGet(TableApiBase):

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}))

        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = serializers.string_to_df(response.data['src_df'])

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(r_df, dframe)


class TableApiJSONMergeToEmpty(TableApiBase):

    # Merge and create an empty dataset
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.new_table,
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        self.assertEqual(
            response.data['detail'],
            'Unable to perform merge operation: '
            + 'Merge operation produced a result with no rows')


class TableApiPandasMergeToEmpty(TableApiBase):

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": serializers.df_to_string(r_df),
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        self.assertEqual(
            response.data['detail'],
            'Unable to perform merge operation: '
            + 'Merge operation produced a result with no rows')


class TableApiJSONMergeInner(TableApiBase):

    # Merge with inner values
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df,
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the updated object
        workflow = models.Workflow.objects.all()[0]

        # Result should have two rows
        self.assertEqual(workflow.nrows, 2)


class TableApiPandasMergeInner(TableApiBase):

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df)

        # Get the data through the API
        self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": serializers.df_to_string(r_df),
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the updated object
        workflow = models.Workflow.objects.all()[0]

        # Result should have two rows
        self.assertEqual(workflow.nrows, 2)


class TableApiJSONMergeOuter(TableApiBase):

    def test(self):
        """Merge with outer values."""
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df,
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # No anomaly should be detected
        self.assertEqual(None, response.data.get('detail'))

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)


class TableApiPandasMergeOuter(TableApiBase):

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df)

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": serializers.df_to_string(r_df),
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # No anomaly should be detected
        self.assertEqual(None, response.data.get('detail'))

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)


class TableApiJSONMergeLeft(TableApiBase):

    # Merge with left values
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Get the data through the API
        self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df,
                "how": "left",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 3)

        dframe = pandas.load_table(workflow.get_data_frame_table_name())
        self.assertEqual(
            dframe[dframe['sid'] == 1]['newcol'].values[0],
            self.src_df['newcol'][0])


class TableApiPandasMergeLeft(TableApiBase):

    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df)

        # Get the data through the API
        self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": serializers.df_to_string(r_df),
                "how": "left",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 3)

        dframe = pandas.load_table(workflow.get_data_frame_table_name())
        self.assertEqual(
            dframe[dframe['sid'] == 1]['newcol'].values[0],
            self.src_df['newcol'][0])


class TableApiJSONMergeOuterNaN(TableApiBase):

    # Merge with outer values but producing NaN everywhere
    def test(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Drop the column with booleans because the data type is lost
        delete_column(
            self.user,
            workflow,
            workflow.columns.get(name='registered'))

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df2)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())
        new_df = pd.merge(
            dframe,
            r_df,
            how="outer",
            left_on="sid",
            right_on="sid")

        # Get the data through the API
        self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df2,
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)
        self.assertEqual(workflow.ncols, 8)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(dframe, new_df)


class TableApiJSONMergeOuterNaNSerializer(TableApiBase):

    def test_table_pandas_merge_to_outer_NaN(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Drop the column with booleans because the data type is lost
        delete_column(
            self.user,
            workflow,
            workflow.columns.get(name='registered'))

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df2)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())
        new_df = pd.merge(
            dframe,
            r_df,
            how="outer",
            left_on="sid",
            right_on="sid")

        # Get the data through the API
        self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": serializers.df_to_string(r_df),
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = models.Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)
        self.assertEqual(workflow.ncols, 8)

        # Load the df from the db
        dframe = pandas.load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(dframe, new_df)


class TableApiJSONMergeDatetimes(TableApiBase):

    # Merge a single row with non-localised date/time fields.
    def test_table_JSON_merge_datetimes(self):
        # Get the only workflow in the fixture
        workflow = models.Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid",
                "src_df": {
                    "sid": {"0": 4},
                    "email": {"0": "student04@bogus.com"},
                    "age": {"0": 14},
                    "tstamp1": {"0": ""},
                    "tstamp2": {"0": "2019-05-10 20:40:48.269638"},
                    "tstamp3": {"0": "2019-06-03 15:28:59.787917"},
                    "tstamp4": {"0": "2019-06-03 15:28:59.787917+09:30"},
                },
            },
            format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        workflow = models.Workflow.objects.all()[0]
        dst_df = pandas.load_table(workflow.get_data_frame_table_name())

        self.assertEqual(workflow.nrows, 4)

        self.assertEqual(
            workflow.columns.get(name='tstamp2').data_type,
            'datetime')

        self.assertTrue(all(
            elem.tzinfo is not None and elem.tzinfo.utcoffset(elem) is not None
            for elem in dst_df['tstamp2'].dropna()))

        self.assertEqual(
            workflow.columns.get(name='tstamp3').data_type,
            'datetime')

        self.assertTrue(all(
            elem.tzinfo is not None and elem.tzinfo.utcoffset(elem) is not None
            for elem in dst_df['tstamp3'].dropna()))

        self.assertEqual(
            workflow.columns.get(name='tstamp4').data_type,
            'datetime')

        self.assertTrue(all(
            elem.tzinfo is not None and elem.tzinfo.utcoffset(elem) is not None
            for elem in dst_df['tstamp4'].dropna()))
