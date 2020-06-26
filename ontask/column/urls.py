# -*- coding: utf-8 -*-

"""URLs to manipulate columns."""
from django.urls import path

from ontask.column import views

app_name = 'column'

urlpatterns = [
    # Column table manipulation
    path('', views.index, name='index'),
    path('index_ss/', views.index_ss, name='index_ss'),

    # Column manipulation
    path('create/', views.create, name='create'),
    path('<int:pk>/question_add/', views.question_add, name='question_add'),
    path('<int:pk>/todoitem_add/', views.todoitem_add, name='todoitem_add'),
    path(
        '<int:pk>/criterion_create/',
        views.criterion_create,
        name='criterion_create'),
    path(
        '<int:pk>/criterion_remove',
        views.criterion_remove,
        name='criterion_remove'),

    path(
        'formula_column_add',
        views.formula_column_add,
        name='formula_column_add'),
    path(
        'random_column_add/',
        views.random_column_add,
        name='random_column_add'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/column_edit/', views.column_edit, name='column_edit'),
    path(
        '<int:pk>/question_edit/',
        views.column_edit,
        name='question_edit'),
    path(
        '<int:pk>/todoitem_edit/',
        views.column_edit,
        name='todoitem_edit'),
    path(
        '<int:pk>/criterion_edit/',
        views.criterion_edit,
        name='criterion_edit'),
    path(
        '<int:pk>/<int:cpk>/criterion_insert/',
        views.criterion_insert,
        name='criterion_insert'),
    path(
        '<int:pk>/column_clone/',
        views.column_clone,
        name='column_clone'),

    # Column movement
    path('column_move/', views.column_move, name='column_move'),
    path(
        '<int:pk>/column_move_top/',
        views.column_move_top,
        name='column_move_top'),
    path(
        '<int:pk>/column_move_bottom/',
        views.column_move_bottom,
        name='column_move_bottom'),
    path(
        '<int:pk>/column_restrict/',
        views.column_restrict_values,
        name='column_restrict'),

    # Column selection
    path('select/', views.column_selection, name='select'),
]
