# -*- coding: utf-8 -*-


import io
import datetime
import os

import pandas as pd

import test
from django.conf import settings
from dataops import pandas_db
from dataops.formula_evaluation import evaluate, NodeEvaluation
from dataops.ops import perform_dataframe_upload_merge
from dataops.pandas_db import get_filter_query, load_from_db
from workflow.models import Workflow


class DataopsMatrixManipulation(test.OnTaskTestCase):
    fixtures = ['test_merge']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'test_merge.sql'
    )

    table_name = 'DUMP_BOGUS_TABLE'

    csv1 = """key,text1,text2,double1,double2,bool1,bool2,date1,date2
              1.0,"d1_t1_1",,111.0,,True,,1/1/18 01:00:00,
              2.0,"d2_t1_2",,112.0,,False,,1/1/18 02:00:00,
              3.0,"",d1_t2_3,,123.0,,False,,1/2/18 03:00:00
              4.0,,d1_t2_4,,124.0,,True,,1/2/18 04:00:00
              5.0,"d1_t1_5",,115.0,,False,,1/1/18 05:00:00,
              6.0,"d1_t1_6",,116.0,,True,,1/1/18 06:00:00,
              7.0,,d1_t2_7,,126.0,,True,,1/2/18 07:00:00
              8.0,,d1_t2_8,,127.0,,False,,1/2/18 08:00:00"""

    csv2 = """key,text2,text3,double2,double3,bool2,bool3,date2,date3
              5.0,,d2_t3_5,,235.0,,FALSE,,2/3/18
              6.0,d2_t2_6,,216.0,,TRUE,,2/2/18 06:00,
              7.0,,d2_t3_7,,237.0,,TRUE,,2/3/18 07:00
              8.0,d2_t2_8,,218.0,,FALSE,,2/2/18 08:00,
              9.0,,d2_t3_9,,239.0,,TRUE,,2/3/18 09:00
              10.0,d2_t2_10,,2110.0,,FALSE,,2/2/18 10:00,
              11.0,,d2_t3_11,,2311.0,,FALSE,,2/3/18 11:00
              12.0,d2_t2_12,,2112.0,,TRUE,,2/2/18 12:00,"""

    merge_info = {
        'initial_column_names': None,
        'rename_column_names': None,
        'columns_to_upload': None,
        'src_selected_key': 'key',
        'dst_selected_key': 'key',
        'how_merge': None
    }

    def __init__(self, *args, **kwargs):
        super(DataopsMatrixManipulation, self).__init__(*args, **kwargs)
        self.workflow = None

    def setUp(self):
        super(DataopsMatrixManipulation, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsMatrixManipulation, self).tearDown()

    def parse_data_frames(self):
        # Parse the two CSV strings and return as data frames

        if self.workflow:
            # Get the workflow data frame
            df_dst = load_from_db(self.workflow.id)
        else:
            df_dst = pandas_db.load_df_from_csvfile(
                io.StringIO(self.csv1),
                0,
                0
            )

        df_src = pandas_db.load_df_from_csvfile(io.StringIO(self.csv2),
                                                0,
                                                0)

        # Fix the merge_info fields.
        self.merge_info['initial_column_names'] = list(df_src.columns)
        self.merge_info['rename_column_names'] = list(df_src.columns)
        self.merge_info['columns_to_upload'] = list(df_src.columns)

        return df_dst, df_src

    def test_df_equivalent_after_sql(self):

        # Parse the CSV
        df_source = pandas_db.load_df_from_csvfile(io.StringIO(self.csv1),
                                                   0,
                                                   0)

        # Store the DF in the DB
        pandas_db.store_table(df_source, self.table_name)

        # Load it from the DB
        df_dst = pandas_db.load_table(self.table_name)

        # Data frames mut be identical
        assert df_source.equals(df_dst)

    def test_merge_inner(self):

        # Get the workflow
        self.workflow = Workflow.objects.all()[0]

        # Parse the source data frame
        df_dst, df_src = self.parse_data_frames()

        self.merge_info['how_merge'] = 'inner'

        result = perform_dataframe_upload_merge(self.workflow,
                                                df_dst,
                                                df_src,
                                                self.merge_info)

        # Load again the workflow data frame
        df_dst = load_from_db(self.workflow.id)

        # Result must be correct (None)
        self.assertEquals(result, None)


class FormulaEvaluation(test.OnTaskTestCase):
    skel = {
        'condition': 'AND',
        'not': False,
        'rules': [{
            'field': 'variable',
            'id': 'variable',
            'input': '{0}',  # Number/Text/
            'operator': '{1}',  # Operator
            'type': '{2}',  # Data type: integer, double, text, ...
            'value': '{3}'}],  # The constant
        'valid': True
    }
    test_table = 'TEST_TABLE'
    test_columns = ['v_integer',
                    'v_double',
                    'v_boolean',
                    'v_string',
                    'v_datetime']

    def set_skel(self, input_value, op_value, type_value, value, vname=None):
        if vname:
            self.skel['rules'][0]['field'] = vname
            self.skel['rules'][0]['id'] = vname
        self.skel['rules'][0]['input'] = input_value
        self.skel['rules'][0]['operator'] = op_value
        self.skel['rules'][0]['type'] = type_value
        self.skel['rules'][0]['value'] = value
        return self.skel

    def do_operand(self,
                   input_value,
                   op_value,
                   type_value,
                   value1,
                   value2,
                   value3):

        result1 = evaluate(
            self.set_skel(input_value,
                          op_value.format(''),
                          type_value,
                          value1),
            NodeEvaluation.EVAL_EXP,
            {'variable': value2}
        )
        result2 = evaluate(
            self.set_skel(input_value,
                          op_value.format(''),
                          type_value,
                          value1),
            NodeEvaluation.EVAL_EXP,
            {'variable': value3}
        )

        if op_value.endswith('null') or value2 is not None:
            # If value2 is not None, expect regular results
            self.assertTrue(result1)
        else:
            # If value2 is None, then all formulas should be false
            self.assertFalse(result1)

        self.assertFalse(result2)

        if op_value.find('{0}') != -1:
            result1 = evaluate(
                self.set_skel(input_value,
                              op_value.format('not_'),
                              type_value,
                              value1),
                NodeEvaluation.EVAL_EXP,
                {'variable': value2}
            )
            result2 = evaluate(
                self.set_skel(input_value,
                              op_value.format('not_'),
                              type_value,
                              value1),
                NodeEvaluation.EVAL_EXP,
                {'variable': value3}
            )

            self.assertFalse(result1)
            if op_value.endswith('null') or value3 is not None:
                # If value2 is not None, expect regular results
                self.assertTrue(result2)
            else:
                # If value2 is None, then all formulas should be false
                self.assertFalse(result2)

    def do_sql_operand(self,
                       input_value,
                       op_value,
                       type_value,
                       value):
        self.set_skel(
            input_value,
            op_value.format(''),
            type_value,
            value, 'v_' + type_value
        )
        query, fields = get_filter_query(self.test_table,
                                         self.test_columns,
                                         self.skel)
        result = pd.read_sql_query(query, pandas_db.engine, params=fields)
        self.assertEqual(len(result), 1)

    def test_eval_node(self):
        #
        # EQUAL
        #
        self.do_operand('number', '{0}equal', 'integer', '0', 0, 3)
        self.do_operand('number', '{0}equal', 'integer', '0', 0, None)
        self.do_operand('number', '{0}equal', 'double', '0.3', 0.3, 3.2)
        self.do_operand('number', '{0}equal', 'double', '0.3', 0.3, None)
        self.do_operand('text', '{0}equal', 'string', 'aaa', 'aaa', 'abb')
        self.do_operand('text', '{0}equal', 'string', 'aaa', 'aaa', 'None')
        self.do_operand('text', '{0}equal', 'boolean', 1, True, False)
        self.do_operand('text', '{0}equal', 'boolean', 1, None, None)
        self.do_operand('text', '{0}equal', 'boolean', 0, False, True)
        self.do_operand('text', '{0}equal', 'boolean', 0, None, None)
        self.do_operand('text',
                        '{0}equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 3),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))
        self.do_operand('text',
                        '{0}equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        None,
                        None)

        #
        # BEGINS WITH
        #
        self.do_operand('text',
                        '{0}begins_with',
                        'string', 'ab', 'abcd', 'acd')
        self.do_operand('text',
                        '{0}begins_with',
                        'string', 'ab', None, None)

        #
        # CONTAINS
        #
        self.do_operand('text',
                        '{0}contains',
                        'string', 'bc', 'abcd', 'acd')
        self.do_operand('text',
                        '{0}contains',
                        'string', 'bc', None, None)

        #
        # ENDS WITH
        #
        self.do_operand('text',
                        '{0}ends_with',
                        'string', 'cd', 'abcd', 'abc')
        self.do_operand('text',
                        '{0}ends_with',
                        'string', 'cd', None, None)

        #
        # IS EMPTY
        #
        self.do_operand('text', 'is_{0}empty', 'string', None, '', 'aaa')
        self.do_operand('text', 'is_{0}empty', 'string', None, None, None)

        #
        # LESS
        #
        self.do_operand('number', 'less', 'integer', '1', 0, 3)
        self.do_operand('number', 'less', 'integer', '1', None, None)
        self.do_operand('number', 'less', 'double', '1.2', 0.2, 3.2)
        self.do_operand('number', 'less', 'double', '1.2', None, None)
        self.do_operand('text',
                        'less',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 2),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))
        self.do_operand('text',
                        'less',
                        'datetime',
                        '2018-09-15T00:03:03',
                        None,
                        None)

        #
        # LESS OR EQUAL
        #
        self.do_operand('number', 'less_or_equal', 'integer', '1', 0, 3)
        self.do_operand('number', 'less_or_equal', 'integer', '1', 1, 3)
        self.do_operand('number', 'less_or_equal', 'integer', '1', None, None)
        self.do_operand('number', 'less_or_equal', 'double', '1.2', 0.2, 3.2)
        self.do_operand('number', 'less_or_equal', 'double', '1.2', 1.2, 3.2)
        self.do_operand('number', 'less_or_equal', 'double', '1.2', None, None)
        self.do_operand('text',
                        'less_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 2),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))
        self.do_operand('text',
                        'less_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 3),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))
        self.do_operand('text',
                        'less_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        None,
                        None)

        #
        # GREATER
        #
        self.do_operand('number', 'greater', 'integer', '1', 3, 0)
        self.do_operand('number', 'greater', 'integer', '1', None, None)
        self.do_operand('number', 'greater', 'double', '1.2', 3.2, 0.2)
        self.do_operand('number', 'greater', 'double', '1.2', None, None)
        self.do_operand('text',
                        'greater',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 4),
                        datetime.datetime(2018, 9, 15, 0, 3, 2))
        self.do_operand('text',
                        'greater',
                        'datetime',
                        '2018-09-15T00:03:03',
                        None,
                        None)

        #
        # GREATER OR EQUAL
        #
        self.do_operand('number', 'greater_or_equal', 'integer', '1', 3, 0)
        self.do_operand('number', 'greater_or_equal', 'integer', '1', 1, 0)
        self.do_operand('number',
                        'greater_or_equal',
                        'integer',
                        '1',
                        None,
                        None)
        self.do_operand('number', 'greater_or_equal', 'double', '1.2', 3.2, 0.2)
        self.do_operand('number', 'greater_or_equal', 'double', '1.2', 1.2, 0.2)
        self.do_operand('number',
                        'greater_or_equal',
                        'double',
                        '1.2',
                        None,
                        None)
        self.do_operand('text',
                        'greater_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 4),
                        datetime.datetime(2018, 9, 15, 0, 3, 2))
        self.do_operand('text',
                        'greater_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 3),
                        datetime.datetime(2018, 9, 15, 0, 3, 2))
        self.do_operand('text',
                        'greater_or_equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        None,
                        None)

        #
        # In Between (needs special function)
        #
        self.do_operand('number', '{0}between', 'integer', ['1', '4'], 2, 5)
        self.do_operand('number',
                        '{0}between',
                        'integer',
                        ['1', '4'],
                        None,
                        None)
        self.do_operand('number',
                        '{0}between',
                        'double',
                        ['1.0',
                         '4.0'],
                        2.0,
                        5.0)
        self.do_operand('number',
                        '{0}between',
                        'double',
                        ['1.0',
                         '4.0'],
                        None,
                        None)
        self.do_operand('text',
                        '{0}between',
                        'datetime',
                        ['2018-09-15T00:03:03', '2018-09-15T00:04:03'],
                        datetime.datetime(2018, 9, 15, 0, 3, 30),
                        datetime.datetime(2018, 9, 15, 0, 4, 30))
        self.do_operand('text',
                        '{0}between',
                        'datetime',
                        ['2018-09-15T00:03:03', '2018-09-15T00:04:03'],
                        None,
                        None)

        #
        # IS NULL
        #
        self.do_operand('number', 'is_{0}null', 'integer', None, None, 1)
        self.do_operand('number', 'is_{0}null', 'double', None, None, 1.0)
        self.do_operand('text', 'is_{0}null', 'string', None, None, 'aaa')
        self.do_operand('text', 'is_{0}null', 'boolean', None, None, True)
        self.do_operand('text', 'is_{0}null', 'boolean', None, None, False)
        self.do_operand('text',
                        'is_{0}null',
                        'datetime',
                        None,
                        None,
                        datetime.datetime(2018, 9, 15, 0, 3, 4))

    def test_eval_sql(self):

        # Create the dataframe with the variables
        df = pd.DataFrame(
            [(1, 2.0, True, 'xxx', datetime.datetime(2018, 1, 1, 0, 0, 0)),
             (None, None, None, None, None)],
            columns=self.test_columns)

        # Store the data frame
        pandas_db.store_table(df, 'TEST_TABLE')

        #
        # EQUAL
        #
        self.do_sql_operand('number', '{0}equal', 'integer', '1')
        self.do_sql_operand('number', '{0}equal', 'double', '2.0')
        self.do_sql_operand('number', '{0}equal', 'boolean', 1)
        self.do_sql_operand('text', '{0}equal', 'string', 'xxx')
        self.do_sql_operand('text',
                            '{0}equal',
                            'datetime',
                            '2018-01-01T00:00:00')

        #
        # BEGINS WITH
        #
        self.do_sql_operand('text',
                            '{0}begins_with',
                            'string',
                            'x')

        #
        # CONTAINS
        #
        self.do_sql_operand('text',
                            '{0}contains',
                            'string',
                            'xx')
        #
        # ENDS WITH
        #
        self.do_sql_operand('text',
                            '{0}ends_with',
                            'string',
                            'xx')

        #
        # IS EMPTY
        #
        self.do_sql_operand('text', 'is_{0}empty', 'string', None)

        #
        # IS NULL
        #
        self.do_sql_operand('number', 'is_{0}null', 'integer', None)
        self.do_sql_operand('number', 'is_{0}null', 'double', None)
        self.do_sql_operand('number', 'is_{0}null', 'boolean', None)
        self.do_sql_operand('text', 'is_{0}null', 'string', None)
        self.do_sql_operand('text', 'is_{0}null', 'datetime', None)

        #
        # LESS
        #
        self.do_sql_operand('number', 'less', 'integer', '2')
        self.do_sql_operand('number', 'less', 'double', '3.2')
        self.do_sql_operand('text',
                            'less',
                            'datetime',
                            '2018-01-02T00:00:00')

        #
        # LESS OR EQUAL
        #
        self.do_sql_operand('number', 'less_or_equal', 'integer', '1')
        self.do_sql_operand('number', 'less_or_equal', 'double', '2.0')
        self.do_sql_operand('text',
                            'less_or_equal',
                            'datetime',
                            '2018-01-01T00:00:00')

        #
        # GREATER
        #
        self.do_sql_operand('number', 'greater', 'integer', '0')
        self.do_sql_operand('number', 'greater', 'double', '1.2')
        self.do_sql_operand('text',
                            'greater',
                            'datetime',
                            '2017-01-01T00:00:00')

        #
        # GREATER OR EQUAL
        #
        self.do_sql_operand('number', 'greater_or_equal', 'integer', '1')
        self.do_sql_operand('number', 'greater_or_equal', 'double', '2.0')
        self.do_sql_operand('text',
                            'greater_or_equal',
                            'datetime',
                            '2018-01-01T00:00:00')

        #
        # BETWEEN
        #
        self.do_sql_operand('number', '{0}between', 'integer', ['0', '2'])
        self.do_sql_operand('number', '{0}between', 'double', ['1.2', '2.2'])
        self.do_sql_operand('text',
                            '{0}between',
                            'datetime', ['2017-01-01T00:00:00',
                                         '2018-09-13T00:00:00'])
