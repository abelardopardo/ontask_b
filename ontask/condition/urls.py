# -*- coding: utf-8 -*-

"""URLs to manipulate columns."""
from django.urls import path

from ontask.condition import views, forms

app_name = 'condition'

urlpatterns = [
    #
    # FILTERS
    #
    path(
        '<int:pk>/create_filter/',
        views.ConditionCreateView.as_view(
            form_class=forms.FilterForm,
            template_name='condition/includes/partial_filter_addedit.html'),
        name='create_filter'),
    path(
        '<int:pk>/edit_filter/',
        views.FilterUpdateView.as_view(),
        name='edit_filter'),
    path(
        '<int:pk>/delete_filter/',
        views.FilterDeleteView.as_view(),
        name='delete_filter'),
    path(
        '<int:pk>/<int:view_id>/set_filter/',
        views.FilterSetView.as_view(),
        name='set_filter'),

    #
    # CONDITIONS
    #
    path(
        '<int:pk>/create_condition/',
        views.ConditionCreateView.as_view(
            form_class=forms.ConditionForm,
            template_name='condition/includes/partial_condition_addedit.html'),
        name='create_condition'),
    path(
        '<int:pk>/edit_condition/',
        views.ConditionUpdateView.as_view(),
        name='edit_condition'),
    path(
        '<int:pk>/delete_condition/',
        views.ConditionDeleteView.as_view(),
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
