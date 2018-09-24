# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO
import datetime

import numpy as np
import pandas as pd

import test
from dataops import pandas_db
from dataops.formula_evaluation import evaluate_top_node, evaluate_node_sql
from dataops.ops import perform_dataframe_upload_merge
from dataops.pandas_db import get_filter_query


class DataopsMatrixManipulation(test.OntaskTestCase):
    table_name = 'TEST_TABLE'

    pk = '999'

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

    def parse_data_frames(self):
        # Parse the two CSV strings and return as data frames
        df_dst = pandas_db.load_df_from_csvfile(
            StringIO.StringIO(self.csv1),
            0,
            0)
        df_src = pandas_db.load_df_from_csvfile(
            StringIO.StringIO(self.csv2),
            0,
            0
        )

        # Fix the merge_info fields.
        self.merge_info['initial_column_names'] = list(df_src.columns)
        self.merge_info['rename_column_names'] = list(df_src.columns)
        self.merge_info['columns_to_upload'] = list(df_src.columns)

        return df_dst, df_src

    def df_update_inner(self):
        df_dst, df_src = self.parse_data_frames()

        self.merge_info['how_merge'] = 'inner'

        result = perform_dataframe_upload_merge(self.pk,
                                                df_dst,
                                                df_src,
                                                self.merge_info)

        # Result must be correct (None)
        self.assertEquals(result, None)

        result_df = pandas_db.load_from_db(self.pk)

    def df_equivalent_after_sql(self):
        # Parse the CSV
        df_source = pandas_db.load_df_from_csvfile(
            StringIO.StringIO(self.csv1),
            0,
            0)

        # Store the DF in the DB
        pandas_db.store_table(df_source, self.table_name)

        # Load it from the DB
        df_dst = pandas_db.load_table(self.table_name)

        # Columns have to have the same values (None and NaN are
        # different)
        for x in df_source.columns:
            np.testing.assert_array_equal(
                np.array(df_source[x], dtype=unicode),
                np.array(df_dst[x], dtype=unicode)
            )


class FormulaEvaluation(test.OntaskTestCase):
    skel = {
        u'condition': u'AND',
        u'not': False,
        u'rules': [{
            u'field': u'variable',
            u'id': u'variable',
            u'input': u'{0}',  # Number/Text/
            u'operator': u'{1}',  # Operator
            u'type': u'{2}',  # Data type: integer, double, text, ...
            u'value': u'{3}'}],  # The constant
        u'valid': True
    }
    test_table = 'TEST_TABLE'

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
        self.assertTrue(
            evaluate_top_node(
                self.set_skel(input_value,
                              op_value.format(''),
                              type_value,
                              value1),
                {'variable': value2}
            )
        )
        self.assertFalse(
            evaluate_top_node(
                self.set_skel(input_value,
                              op_value.format(''),
                              type_value,
                              value1),
                {'variable': value3}
            )
        )
        if op_value.find('{0}') != -1:
            self.assertFalse(
                evaluate_top_node(
                    self.set_skel(input_value,
                                  op_value.format('not_'),
                                  type_value,
                                  value1),
                    {'variable': value2}
                )
            )
            self.assertTrue(
                evaluate_top_node(
                    self.set_skel(input_value,
                                  op_value.format('not_'),
                                  type_value,
                                  value1),
                    {'variable': value3}
                )
            )

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
        query, fields = get_filter_query(self.test_table, None, self.skel)
        result = pd.read_sql_query(query, pandas_db.engine, params=fields)
        self.assertEqual(len(result), 1)


    def test_eval_node(self):
        #
        # EQUAL
        #
        self.do_operand('number', '{0}equal', 'integer', '0', 0, 3)
        self.do_operand('number', '{0}equal', 'double', '0.3', 0.3, 3.2)
        self.do_operand('text', '{0}equal', 'string', 'aaa', 'aaa', 'abb')
        self.do_operand('text', '{0}equal', 'boolean', '1', True, False)
        self.do_operand('text', '{0}equal', 'boolean', '0', False, True)
        self.do_operand('text',
                        '{0}equal',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 3),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))

        #
        # BEGINS WITH
        #
        self.do_operand('text',
                        '{0}begins_with',
                        'string', 'ab', 'abcd', 'acd')

        #
        # CONTAINS
        #
        self.do_operand('text',
                        '{0}contains',
                        'string', 'bc', 'abcd', 'acd')

        #
        # ENDS WITH
        #
        self.do_operand('text',
                        '{0}ends_with',
                        'string', 'cd', 'abcd', 'abc')

        #
        # IS EMPTY
        #
        self.do_operand('text',
                        'is_{0}empty',
                        'string', None, None, 'aaa')

        #
        # LESS
        #
        self.do_operand('number', 'less', 'integer', '1', 0, 3)
        self.do_operand('number', 'less', 'double', '1.2', 0.2, 3.2)
        self.do_operand('text',
                        'less',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 2),
                        datetime.datetime(2018, 9, 15, 0, 3, 4))

        #
        # LESS OR EQUAL
        #
        self.do_operand('number', 'less_or_equal', 'integer', '1', 0, 3)
        self.do_operand('number', 'less_or_equal', 'integer', '1', 1, 3)
        self.do_operand('number', 'less_or_equal', 'double', '1.2', 0.2, 3.2)
        self.do_operand('number', 'less_or_equal', 'double', '1.2', 1.2, 3.2)
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

        #
        # GREATER
        #
        self.do_operand('number', 'greater', 'integer', '1', 3, 0, )
        self.do_operand('number', 'greater', 'double', '1.2', 3.2, 0.2)
        self.do_operand('text',
                        'greater',
                        'datetime',
                        '2018-09-15T00:03:03',
                        datetime.datetime(2018, 9, 15, 0, 3, 4),
                        datetime.datetime(2018, 9, 15, 0, 3, 2))

        #
        # GREATER OR EQUAL
        #
        self.do_operand('number', 'greater_or_equal', 'integer', '1', 3, 0)
        self.do_operand('number', 'greater_or_equal', 'integer', '1', 1, 0)
        self.do_operand('number', 'greater_or_equal', 'double', '1.2', 3.2, 0.2)
        self.do_operand('number', 'greater_or_equal', 'double', '1.2', 1.2, 0.2)
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

        #
        # In Between (needs special function)
        #
        self.do_operand('number', '{0}between', 'integer', ['1', '4'], 2, 5)
        self.do_operand('number',
                        '{0}between',
                        'double',
                        ['1.0',
                         '4.0'],
                        2.0,
                        5.0)
        self.do_operand('text',
                        '{0}between',
                        'datetime',
                        ['2018-09-15T00:03:03', '2018-09-15T00:04:03'],
                        datetime.datetime(2018, 9, 15, 0, 3, 30),
                        datetime.datetime(2018, 9, 15, 0, 4, 30))

    def test_eval_sql(self):

        # Create the dataframe with the variables
        df = pd.DataFrame(
            [(1, 2.0, True, 'xxx', datetime.datetime(2018, 01, 01, 00, 00,
                                                     00)),
             (None, None, None, None, None)],
            columns=['v_integer',
                     'v_double',
                     'v_boolean',
                     'v_string',
                     'v_datetime'])

        # Store the data frame
        pandas_db.store_table(df, 'TEST_TABLE')

        #
        # EQUAL
        #
        self.do_sql_operand('number', '{0}equal', 'integer', '1')
        self.do_sql_operand('number', '{0}equal', 'double', '2.0')
        self.do_sql_operand('number', '{0}equal', 'boolean', '1')
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
        self.do_sql_operand('number', 'is_{0}empty', 'integer', None)
        self.do_sql_operand('number', 'is_{0}empty', 'double', None)
        self.do_sql_operand('text', 'is_{0}empty', 'string', None)
        self.do_sql_operand('text', 'is_{0}empty', 'boolean', None)
        self.do_sql_operand('text', 'is_{0}empty', 'datetime', None)

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
