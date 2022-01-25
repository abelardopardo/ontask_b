# -*- coding: utf-8 -*-

"""Access the DB directly through psycopg2 and django connection."""
from ontask.dataops.sql.column_queries import (
    COLUMN_NAME_SIZE, add_column_to_db, copy_column_in_db, db_rename_column,
    df_drop_column, get_df_column_types, get_text_column_hash,
    is_column_in_table, is_column_unique, get_column_distinct_values,
    is_unique_column)
from ontask.dataops.sql.row_queries import (
    delete_row, get_num_rows, get_row, get_rows, increase_row_integer,
    insert_row, select_ids_all_false, update_row)
from ontask.dataops.sql.table_queries import (
    clone_table, delete_table, get_select_query_txt, rename_table,
    search_table)
