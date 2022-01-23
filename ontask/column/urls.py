# -*- coding: utf-8 -*-

"""URLs to manipulate columns."""
from django.urls import path

from ontask.column import forms, views

app_name = 'column'

urlpatterns = [
    # Column table manipulation
    path('', views.ColumnIndexView.as_view(), name='index'),
    path('index_ss/', views.ColumnIndexSSView.as_view(), name='index_ss'),

    # Column manipulation
    path('create/', views.ColumnCreateView.as_view(), name='create'),
    path(
        '<int:pk>/question_add/',
        views.ColumnQuestionAddView.as_view(),
        name='question_add'),
    path(
        '<int:pk>/todoitem_add/',
        views.ColumnTODOAddView.as_view(),
        name='todoitem_add'),
    path(
        '<int:pk>/criterion_create/',
        views.ColumnCriterionCreateView.as_view(),
        name='criterion_create'),
    path(
        '<int:pk>/criterion_delete',
        views.ColumnCriterionDeleteView.as_view(),
        name='criterion_delete'),

    path(
        'formula_column_add',
        views.ColumnFormulaAddView.as_view(),
        name='formula_column_add'),
    path(
        'random_column_add/',
        views.ColumnRandomAddView.as_view(),
        name='random_column_add'),
    path('<int:pk>/delete/', views.ColumnDeleteView.as_view(), name='delete'),
    path(
        '<int:pk>/column_edit/',
        views.ColumnEditView.as_view(
            form_class=forms.ColumnRenameForm,
            template_name='column/includes/partial_add_edit.html'),
        name='column_edit'),
    path(
        '<int:pk>/question_edit/',
        views.ColumnEditView.as_view(
            form_class=forms.QuestionForm,
            template_name='column/includes/partial_question_add_edit.html'),
        name='question_edit'),
    path(
        '<int:pk>/todoitem_edit/',
        views.ColumnEditView.as_view(
            form_class=forms.ColumnRenameForm,
            template_name='column/includes/partial_add_edit.html'),
        name='todoitem_edit'),
    path(
        '<int:pk>/criterion_edit/',
        views.ColumnCriterionEditView.as_view(),
        name='criterion_edit'),
    path(
        '<int:pk>/<int:cpk>/criterion_insert/',
        views.ColumnCriterionInsertView.as_view(),
        name='criterion_insert'),
    path(
        '<int:pk>/column_clone/',
        views.ColumnCloneView.as_view(),
        name='column_clone'),

    # Column movement
    path('column_move/', views.ColumnMoveView.as_view(), name='column_move'),
    path(
        '<int:pk>/column_move_top/',
        views.ColumnMoveTopView.as_view(),
        name='column_move_top'),
    path(
        '<int:pk>/column_move_bottom/',
        views.ColumnMoveBottomView.as_view(),
        name='column_move_bottom'),
    path(
        '<int:pk>/column_restrict/',
        views.ColumnRestrictValuesView.as_view(),
        name='column_restrict'),

    # Column selection
    path('select/', views.ColumnSelectView.as_view(), name='select'),
]
