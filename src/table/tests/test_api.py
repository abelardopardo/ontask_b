# -*- coding: utf-8 -*-


import os
import test

import pandas as pd
from django.conf import settings
from django.shortcuts import reverse
from rest_framework.authtoken.models import Token

from dataops.pandas import check_wf_df, detect_datetime_columns, load_table
from table.serializers import string_to_df
from table.serializers.pandas import df_to_string
from workflow.models import Workflow
from workflow.ops import workflow_delete_column


class TableApiBase(test.OnTaskApiTestCase):
    fixtures = ['simple_table']
    filename = os.path.join(
        settings.BASE_DIR(),
        'table',
        'fixtures',
        'simple_table.sql'
    )

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

    def setUp(self):
        super().setUp()
        # Get the token for authentication and set credentials in client
        token = Token.objects.get(user__email='instructor01@bogus.com')
        'Token ' + token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()


class TableApiCreate(TableApiBase):
    # Getting the table attached to the workflow

    def test_table_JSON_get(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(reverse('table:api_ops',
                                           kwargs={'wid': workflow.id}))

        # Transform the response into a data frame
        r_df = pd.DataFrame(response.data['data_frame'])
        r_df = detect_datetime_columns(r_df)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, df)

    # Getting the table attached to the workflow
    def test_table_pandas_get(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(reverse('table:api_pops',
                                           kwargs={'wid': workflow.id}))

        # Transform the response into a data frame
        r_df = string_to_df(response.data['data_frame'])

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, df)

    def test_table_try_JSON_overwrite(self):
        # Upload a table and try to overwrite an existing one (should fail)

        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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

    def test_table_try_pandas_overwrite(self):
        # Upload a table and try to overwrite an existing one (should fail)

        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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

    def test_table_json_create(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': test.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = Workflow.objects.get(id=response.data['id'])

        # Upload the table
        response = self.client.post(
            reverse('table:api_ops', kwargs={'wid': workflow.id}),
            {'data_frame': self.new_table},
            format='json')

        # Refresh wflow (has been updated)
        workflow = Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())
        # Transform new table into data frame
        r_df = pd.DataFrame(self.new_table)
        r_df = detect_datetime_columns(r_df)

        # Compare both elements
        self.compare_tables(r_df, df)

        # Check that the rest of the information is correct
        self.assertTrue(check_wf_df(workflow))

    def test_table_json_create_error(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': test.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = Workflow.objects.get(id=response.data['id'])

        # Upload the table
        response = self.client.post(
            reverse('table:api_ops', kwargs={'wid': workflow.id}),
            {'data_frame': self.incorrect_table_1},
            format='json')

        self.assertTrue(
            'The data has no column with unique values per row' in
            response.data
        )

    def test_table_pandas_create(self):
        # Create a second workflow
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': test.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Get the only workflow in the fixture
        workflow = Workflow.objects.get(id=response.data['id'])

        # Transform new table into a data frame
        r_df = pd.DataFrame(self.new_table)
        r_df = detect_datetime_columns(r_df)

        # Upload the table
        response = self.client.post(
            reverse('table:api_pops', kwargs={'wid': workflow.id}),
            {'data_frame': df_to_string(r_df)},
            format='json')

        # Refresh wflow (has been updated)
        workflow = Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, df)

        # Check that the rest of the
        # information is correct
        self.assertTrue(check_wf_df(workflow))

    def test_table_JSON_update(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)
        r_df = detect_datetime_columns(r_df)

        # Upload a new table
        response = self.client.put(
            reverse(
                'table:api_ops',
                kwargs={'wid': workflow.id}),
            {'data_frame': self.new_table},
            format='json')

        # Refresh wflow (has been updated)
        workflow = Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, df)

        # Check that the rest of the
        # information is correct
        workflow = Workflow.objects.get(id=workflow.id)
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_update(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)
        r_df = detect_datetime_columns(r_df)

        # Upload a new table
        response = self.client.put(
            reverse(
                'table:api_pops',
                kwargs={'wid': workflow.id}),
            {'data_frame': df_to_string(r_df)},
            format='json')

        # Refresh wflow (has been updated)
        workflow = Workflow.objects.get(id=workflow.id)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements
        self.compare_tables(r_df, df)

        # Check that the rest of the
        # information is correct
        workflow = Workflow.objects.get(id=workflow.id)
        self.assertTrue(check_wf_df(workflow))

    def test_table_JSON_flush(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Flush the data in the table
        response = self.client.delete(reverse(
            'table:api_ops',
            kwargs={'wid': workflow.id}))

        workflow = Workflow.objects.all()[0]
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_flush(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Flush the data in the table
        response = self.client.delete(
            reverse('table:api_pops', kwargs={'wid': workflow.id}))

        workflow = Workflow.objects.all()[0]
        self.assertTrue(check_wf_df(workflow))


class TableApiMerge(TableApiBase):

    # Getting the table through the merge API
    def test_table_pandas_JSON_get(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_merge', kwargs={'wid': workflow.id}))

        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(response.data['src_df'])
        r_df = detect_datetime_columns(r_df)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(r_df, df)
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_get(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.get(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}))

        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = string_to_df(response.data['src_df'])

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(r_df, df)
        self.assertTrue(check_wf_df(workflow))

    # Merge and create an empty dataset
    def test_table_JSON_merge_to_empty(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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

        # Check for df/wf consistency
        workflow = Workflow.objects.all()[0]
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_to_empty(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.new_table)

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": df_to_string(r_df),
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        self.assertEqual(response.data['detail'],
                         'Unable to perform merge operation: '
                         + 'Merge operation produced a result with no rows')

        # Check for df/wf consistency
        workflow = Workflow.objects.all()[0]
        self.assertTrue(check_wf_df(workflow))

    # Merge with inner values
    def test_table_JSON_merge_to_inner(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df,
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the updated object
        workflow = Workflow.objects.all()[0]

        # Result should have two rows
        self.assertEqual(workflow.nrows, 2)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_to_inner(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df)

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": df_to_string(r_df),
                "how": "inner",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the updated object
        workflow = Workflow.objects.all()[0]

        # Result should have two rows
        self.assertEqual(workflow.nrows, 2)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    # Merge with outer values
    def test_table_JSON_merge_to_outer(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_to_outer(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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
                "src_df": df_to_string(r_df),
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # No anomaly should be detected
        self.assertEqual(None, response.data.get('detail'))

        # Get the new workflow
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    # Merge with left values
    def test_table_JSON_merge_to_left(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

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
                "how": "left",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 3)

        df = load_table(workflow.get_data_frame_table_name())
        self.assertEqual(df[df['sid'] == 1]['newcol'].values[0],
                         self.src_df['newcol'][0])

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_to_left(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df)

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": df_to_string(r_df),
                "how": "left",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 3)

        df = load_table(workflow.get_data_frame_table_name())
        self.assertEqual(df[df['sid'] == 1]['newcol'].values[0],
                         self.src_df['newcol'][0])

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    # Merge with outer values but producing NaN everywhere
    def test_table_JSON_merge_to_outer_NaN(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Drop the column with booleans because the data type is lost
        workflow_delete_column(
            workflow,
            workflow.columns.get(name='registered')
        )

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df2)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())
        new_df = pd.merge(df, r_df, how="outer", left_on="sid", right_on="sid")

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_merge', kwargs={'wid': workflow.id}),
            {
                "src_df": self.src_df2,
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)
        self.assertEqual(workflow.ncols, 8)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(df, new_df)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))

    def test_table_pandas_merge_to_outer_NaN(self):
        # Get the only workflow in the fixture
        workflow = Workflow.objects.all()[0]

        age = workflow.columns.filter(name='age')[0]
        age.is_key = False
        age.save()

        email = workflow.columns.filter(name='email')[0]
        email.is_key = False
        email.save()

        # Drop the column with booleans because the data type is lost
        workflow_delete_column(
            workflow,
            workflow.columns.get(name='registered')
        )

        # Transform new table into string
        r_df = pd.DataFrame(self.src_df2)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())
        new_df = pd.merge(df, r_df, how="outer", left_on="sid", right_on="sid")

        # Get the data through the API
        response = self.client.put(
            reverse('table:api_pmerge', kwargs={'wid': workflow.id}),
            {
                "src_df": df_to_string(r_df),
                "how": "outer",
                "left_on": "sid",
                "right_on": "sid"
            },
            format='json')

        # Get the new workflow
        workflow = Workflow.objects.all()[0]

        # Result should have three rows as the initial DF
        self.assertEqual(workflow.nrows, 4)
        self.assertEqual(workflow.ncols, 8)

        # Load the df from the db
        df = load_table(workflow.get_data_frame_table_name())

        # Compare both elements and check wf df consistency
        self.compare_tables(df, new_df)

        # Check for df/wf consistency
        self.assertTrue(check_wf_df(workflow))
