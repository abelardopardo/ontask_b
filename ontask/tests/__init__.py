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
    ViewAsFilterFixture, WflowSymbolsFixture, WrongEmailFixture)

standard_library.install_aliases()

# Workflow elements used in various tests
WORKFLOW_NAME = 'wflow1'
WORKFLOW_DESC = 'description text for workflow 1'
