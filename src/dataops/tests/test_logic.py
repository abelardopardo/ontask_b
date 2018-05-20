# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO

import numpy as np

import test
from dataops import pandas_db
from dataops.ops import perform_dataframe_upload_merge


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