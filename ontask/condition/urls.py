# -*- coding: utf-8 -*-

"""URLs to manipulate columns."""
from django.urls import path

from ontask.condition import views

app_name = 'condition'

urlpatterns = [
    #
    # FILTERS
    #
    path(
        '<int:pk>/create_filter/',
        views.FilterCreateView.as_view(),
        name='create_filter'),
    path('<int:pk>/edit_filter/', views.edit_filter, name='edit_filter'),
    path('<int:pk>/delete_filter/', views.delete_filter, name='delete_filter'),
    path(
        '<int:pk>/<int:view_id>/set_filter/',
        views.set_filter,
        name='set_filter'),

    #
    # CONDITIONS
    #
    path(
        '<int:pk>/create_condition/',
        views.ConditionCreateView.as_view(),
        name='create_condition'),
    path(
        '<int:pk>/edit_condition/',
        views.edit_condition,
        name='edit_condition'),
    path(
        '<int:pk>/delete_condition/',
        views.delete_condition,
        name='delete_condition'),

    # Clone the condition within the same action
    path(
        '<int:pk>/clone_condition/',
        views.clone_condition,
        name='clone_condition'),
    # To clone a condition from a different action
    path(
        '<int:pk>/<int:action_pk>/clone_condition/',
        views.clone_condition,
        name='clone_condition'),
]
