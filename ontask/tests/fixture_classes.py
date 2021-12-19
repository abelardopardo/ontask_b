# -*- coding: utf-8 -*-

"""Classes to use fixtures."""
import os

from django.conf import settings


class AllKeyColumnsFixture:
    wflow_name = 'all key columns'
    fixtures = ['all_key_columns']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'all_key_columns.sql')


class DerivedColumnFixture:
    wflow_name = 'combine columns'
    fixtures = ['derived_column']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'derived_column.sql')


class EmptyWorkflowFixture:
    wflow_name = 'wflow1'
    fixtures = ['empty_wflow']


class InitialDBFixture:
    fixtures = ['initial_db']


class InitialWorkflowFixture:
    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )
    wflow_name = 'BIOL1011'


class LongSurveyFixture:
    wflow_name = 'Test survey run pages'
    fixtures = ['long_survey']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'long_survey.sql')


class PluginExecutionFixture:
    wflow_name = 'Plugin test'
    fixtures = ['plugin_execution']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'plugin_execution.sql')


class ScheduleActionsFixture:
    wflow_name = 'wflow2'
    fixtures = ['schedule_actions']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'schedule_actions.sql')


class SimpleActionFixture:
    wflow_name = 'wflow1'
    fixtures = ['simple_action']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_action.sql')


class SimpleEmailActionFixture:
    wflow_name = 'wflow1'
    fixtures = ['simple_email_action']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_email_action.sql')


class SimpleTableFixture:
    wflow_name = 'wflow1'
    fixtures = ['simple_table']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_table.sql')


class SimpleWorkflowFixture:
    wflow_name = 'wflow1'
    fixtures = ['simple_workflow']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_workflow.sql')


class SimpleWorkflowExportFixture:
    wflow_name = 'wflow1'
    fixtures = ['simple_workflow_export']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow_export.sql')


class SimpleWorkflowTwoActionsFixture:
    wflow_name = 'wflow2'
    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow_two_actions.sql')


class SymbolsInConditionNameFixture:
    wflow_name = 'Issue 128'
    fixtures = ['symbols_in_condition_name']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'symbols_in_condition_name.sql')


class TestConditionEvaluationFixture:
    wflow_name = 'Testing Eval Conditions'
    fixtures = ['test_condition_evaluation']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_condition_evaluation.sql')


class TestEmptyKeyAfterMergeFixture:
    wflow_name = 'Test Empty Key after Merge'
    fixtures = ['test_empty_key_after_merge']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_empty_key_after_merge.sql')


class TestMergeFixture:
    wflow_name = 'Testing Merge'
    fixtures = ['test_merge']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'test_merge.sql')
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')


class TestPersonalisedSurveyFixture:
    wflow_name = 'Test personalized survey'
    fixtures = ['test_personalized_survey']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_personalized_survey.sql')


class TestRubricFixture:
    wflow_name = 'test rubric'
    fixtures = ['test_rubric']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'test_rubric.sql')


class ThreeActionsFixture:
    wflow_name = 'wflow1'
    fixtures = ['three_actions']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'three_actions.sql')


class ViewAsFilterFixture:
    wflow_name = 'View as filter'
    fixtures = ['view_as_filters']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'view_as_filters.sql')


class WflowSymbolsFixture:
    wflow_name = 'wflow1'
    fixtures = ['wflow_symbols']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'wflow_symbols.sql')


class WrongEmailFixture:
    wflow_name = 'wflow1'
    fixtures = ['wrong_email']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'wrong_email.sql')
