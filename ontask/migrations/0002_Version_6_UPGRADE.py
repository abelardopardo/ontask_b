# -*- coding: utf-8 -*-

"""Migration to transfer data from tables in separated apps to OnTask app."""

from psycopg2 import sql

from django.db import connection as con, migrations

def copy_table_content(apps, schema_editor):
    __table_name_pairs = [
        ('action_action', 'ontask_action'),
        ('action_actioncolumnconditiontuple', 'ontask_actioncolumnconditiontuple'),
        ('action_condition', 'ontask_condition'),
        ('action_condition_columns', 'ontask_condition_columns'),
        ('core_ontaskuser', 'ontask_ontaskuser'),
        ('dataops_plugin', 'ontask_plugin'),
        ('dataops_sqlconnection', 'ontask_sqlconnection'),
        ('logs_log', 'ontask_log'),
        ('oauth_oauthusertoken', 'ontask_oauthusertoken'),
        ('profiles_profile', 'ontask_profile'),
        ('scheduler_scheduledaction', 'ontask_scheduledaction'),
        ('table_view', 'ontask_view'),
        ('table_view_columns', 'ontask_view_columns'),
        ('workflow_column', 'ontask_column'),
        ('workflow_workflow', 'ontask_workflow'),
        ('workflow_workflow_shared', 'ontask_workflow_shared'),
        ('workflow_workflow_lusers', 'ontask_workflow_lusers'),
        ('workflow_workflow_star', 'ontask_workflow_star'),
    ]

    __sql_rename_table = 'ALTER TABLE {0} RENAME TO {1}'
    __sql_rename_sequence = 'ALTER SEQUENCE {0} RENAME TO {1}'
    __sql_drop_table = 'DROP TABLE {0} CASCADE'
    __sql_get_count = 'SELECT COUNT(*) FROM {0}'

    with con.cursor() as cursor:
        table_names = [
            citem.name for citem in con.introspection.get_table_list(cursor)]
        cursor.execute(
            sql.SQL('SELECT relname FROM pg_class WHERE relkind = \'S\'')
        )
        sequence_names = [sitem[0] for sitem in cursor.fetchall()]

        # Loop over all the tables and rename table and sequence
        for start_name, final_name in __table_name_pairs:
            if start_name not in table_names:
                # There is no old table, nothing to do
                continue

            # Detect if the new table has already some information
            cursor.execute(sql.SQL(__sql_get_count.format(final_name)))
            nelems = cursor.fetchall()[0][0]
            if nelems != 0:
                # If table with final name is not empty, skip
                cursor.execute(sql.SQL(__sql_get_count.format(start_name)))
                old_nelems = cursor.fetchall()[0][0]
                if nelems != old_nelems:
                    raise Exception(
                        'Partial migration detected in {0}'.format(start_name))
                continue

            # Drop the final table to proceed with the rename
            cursor.execute(
                sql.SQL(__sql_drop_table.format(final_name))
            )

            cursor.execute(
                sql.SQL(__sql_rename_table).format(
                    sql.Identifier(start_name),
                    sql.Identifier(final_name))
            )

            if start_name + '_id_seq' in sequence_names:
                cursor.execute(
                    sql.SQL(__sql_rename_sequence).format(
                        sql.Identifier(start_name + '_id_seq'),
                        sql.Identifier(final_name + '_id_seq'))
                )


class Migration(migrations.Migration):
    dependencies = [
        ('ontask', '0001_oauth_initial'),
    ]

    operations = [
        migrations.RunPython(code=copy_table_content),
    ]
