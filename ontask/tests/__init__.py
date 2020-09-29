# -*- coding: utf-8 -*-

from future import standard_library

from ontask.tests.basic import (
    ElementHasFullOpacity, OnTaskBasicTestCase, OnTaskTestCase,
    OnTaskApiTestCase, OnTaskLiveTestCase, ScreenTests, user_info
)
from ontask.tests.fixture_classes import (
    AllKeyColumnsFixture, DerivedColumnFixture, EmptyWorkflowFixture,
    InitialDBFixture, InitialWorkflowFixture, LongSurveyFixture,
    PluginExecutionFixture, ScheduleActionsFixture, SimpleActionFixture,
    SimpleEmailActionFixture, SimpleTableFixture, SimpleWorkflowExportFixture,
    SimpleWorkflowFixture, SimpleWorkflowTwoActionsFixture,
    SymbolsInConditionNameFixture, TestEmptyKeyAfterMergeFixture,
    TestConditionEvaluationFixture, TestMergeFixture,
    TestPersonalisedSurveyFixture, TestRubricFixture, ThreeActionsFixture,
    WflowSymbolsFixture, WrongEmailFixture)

standard_library.install_aliases()

# Workflow elements used in various tests
wflow_name = 'wflow1'
wflow_desc = 'description text for workflow 1'
wflow_empty = 'The workflow does not have data'
