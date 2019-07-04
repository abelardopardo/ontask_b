# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import json
import os
import test

import pandas as pd
from django.conf import settings
from django.db import IntegrityError

from ontask.table.serializers import (
    DataFrameJSONMergeSerializer, ViewSerializer,
)
from ontask.table.serializers.pandas import (
    DataFramePandasSerializer, df_to_string,
)


class TableTestSerializers(test.OnTaskTestCase):
    """Test stat views."""

    fixtures = ['simple_table']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'table',
        'fixtures',
        'simple_table.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_serializer_view(self):
        """Test the view serialization."""
        # Try to create a view with a name that already exists.
        try:
            views = ViewSerializer(
                data=[{
                    "columns": [
                        {"name": "email"},
                        {"name": "one"},
                        {"name": "registered"},
                        {"name": "when"}],
                    "name": "simple view",
                    "description_text": "",
                    "formula": {
                        "not": False,
                        "rules": [],
                        "valid": True,
                        "condition": "AND"},
                }],
                many=True,
                context={
                    'workflow': self.workflow,
                    'columns': self.workflow.columns.all()
                },
            )
            self.assertTrue(views.is_valid())
            views.save()
        except IntegrityError as exc:
            self.assertTrue('duplicate key value violates' in str(exc))
        else:
            raise Exception('Incorrect serializer operation.')

        # Try to create a view with a different name
        views = ViewSerializer(
            data=[{
                "columns": [
                    {"name": "email"},
                    {"name": "one"},
                    {"name": "registered"},
                    {"name": "when"}],
                "name": "simple view 2",
                "description_text": "",
                "formula": {
                    "not": False,
                    "rules": [],
                    "valid": True,
                    "condition": "AND"},
            }],
            many=True,
            context={
                'workflow': self.workflow,
                'columns': self.workflow.columns.all()
            },
        )
        self.assertTrue(views.is_valid())
        views.save()

        self.assertEqual(self.workflow.views.count(), 2)

    def test_serializer_pandas(self):
        """Test the data frame serialization."""

        df = pd.DataFrame(
            {
                'key': ['k1', 'k2'],
                't1': ['t1', 't2'],
                'i2': [5, 6],
                'f3': [7.0, 8.0],
                'b4': [True, False],
                'd5': [
                    '2018-10-11 21:12:04+10:30',
                    '2018-10-12 21:12:04+10:30'],
            })

        df_str = df_to_string(df)

        new_df = DataFramePandasSerializer(
            data={'data_frame': df_str},
            many=False,
        )
        self.assertTrue(new_df.is_valid())
        new_df = new_df.validated_data['data_frame']

        self.assertTrue(df.equals(new_df))

    def test_serializer_json(self):
        """Test the data frame serialization with a json object"""

        df = pd.DataFrame(
            {
                'key': ['k1', 'k2'],
                't1': ['t1', 't2'],
                'i2': [5, 6],
                'f3': [7.0, 8.0],
                'b4': [True, False],
                'd5': [
                    '2018-10-11 21:12:04+00:00',
                    '2018-10-12 21:12:04+00:00'],
            })
        df['d5'] = pd.to_datetime(df['d5'], infer_datetime_format=True)

        new_df = DataFrameJSONMergeSerializer(
            data={
                'how': 'inner',
                'left_on': 'sid',
                'right_on': 'key',
                'src_df': json.loads(df.to_json(date_format='iso')),
            },
            many=False,
        )
        self.assertTrue(new_df.is_valid())
        new_df = new_df.validated_data['src_df']
        # new_df['d5'] = pd.to_datetime(new_df['d5'], infer_datetime_format=True)
        # new_df['d5'].dt.tz_convert()
        self.assertTrue(
            all(list(df[col]) == list(new_df[col])
                for col in new_df.columns))
