# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""
import json

import pandas as pd

from ontask import tests
from ontask.table import serializers


class TableTestSerializersBasic(tests.SimpleTableFixture, tests.OnTaskTestCase):
    """Test stat views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class TableTestSerializersView(TableTestSerializersBasic):
    """Test stat views."""

    # Test the view serialization.
    def test(self):
        try:
            views = serializers.ViewSerializer(
                data=[{
                    "columns": [
                        {"name": "email"},
                        {"name": "one"},
                        {"name": "registered"},
                        {"name": "when"}],
                    "name": "simple view",
                    "description_text": "",
                }],
                many=True,
                context={
                    'workflow': self.workflow,
                    'columns': self.workflow.columns.all()
                },
            )
            self.assertTrue(views.is_valid())
            serializers.ViewSerializer.create_view(
                views.validated_data[0],
                views.context)
        except Exception as exc:
            self.assertTrue(
                'View with name simple view already exists' in str(exc))
        else:
            raise Exception('Incorrect serializer operation.')

        # Try to create a view with a different name
        views = serializers.ViewSerializer(
            data=[{
                "columns": [
                    {"name": "email"},
                    {"name": "one"},
                    {"name": "registered"},
                    {"name": "when"}],
                "name": "simple view 2",
                "description_text": "",
            }],
            many=True,
            context={
                'workflow': self.workflow,
                'columns': self.workflow.columns.all()
            },
        )
        self.assertTrue(views.is_valid())
        serializers.ViewSerializer.create_view(
            views.validated_data[0],
            views.context)

        self.assertEqual(self.workflow.views.count(), 2)


class TableTestSerializersPandas(TableTestSerializersBasic):
    """Test stat views."""

    # Test the data frame serialization
    def test(self):
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

        df_str = serializers.df_to_string(df)

        new_df = serializers.DataFramePandasSerializer(
            data={'data_frame': df_str},
            many=False,
        )
        self.assertTrue(new_df.is_valid())
        new_df = new_df.validated_data['data_frame']

        self.assertTrue(df.equals(new_df))


class TableTestSerializersJSON(TableTestSerializersBasic):
    """Test stat views."""

    # Test the data frame serialization with a json object
    def test(self):
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

        new_df = serializers.DataFrameJSONMergeSerializer(
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
        self.assertTrue(
            all(list(df[col]) == list(new_df[col])
                for col in new_df.columns))
