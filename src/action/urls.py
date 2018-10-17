# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf.urls import url

from . import views_action, views_condition, views_out

app_name = 'action'

urlpatterns = [
    #
    # Action CRUD
    #
    # List them all
    url(r'^$', views_action.action_index, name='index'),

    # Create an action of type 0: in, 1: Out
    url(r'^create/$',
        views_action.ActionCreateView.as_view(), name='create'),

    # Edit action Out
    url(r'^(?P<pk>\d+)/edit/$', views_action.edit_action, name='edit'),

    # Save action out content
    url(r'^(?P<pk>\d+)/action_out_save_content/$',
        views_action.action_out_save_content,
        name='action_out_save_content'),

    # Action export ask
    url(r'^(?P<pk>\d+)/export_ask/$',
        views_action.export_ask,
        name='export_ask'),

    # Action export done
    url(r'^(?P<pk>\d+)/export_done/$',
        views_action.export_done,
        name='export_done'),

    # Action export done
    url(r'^(?P<pk>\d+)/export_download/$',
        views_action.export_download,
        name='export_download'),

    # Action import
    url(r'^import/$', views_action.action_import, name='import'),

    # Update an action
    url(r'^(?P<pk>\d+)/update/$',
        views_action.ActionUpdateView.as_view(),
        name='update'),

    # Clone the action
    url(r'^(?P<pk>\d+)/clone/$', views_action.clone, name='clone'),

    # Nuke the action
    url(r'^(?P<pk>\d+)/delete/$', views_action.delete_action, name='delete'),

    # Run EMAIL action
    url(r'^(?P<pk>\d+)/run_email/$',
        views_out.run_email_action,
        name='run_email_action'),

    # Run ZIP action
    url(r'^(?P<pk>\d+)/run_zip/$',
        views_out.run_zip_action,
        name='run_zip_action'),

    # Run JSON action
    url(r'^(?P<pk>\d+)/run_json/$',
        views_out.run_json_action,
        name='run_json_action'),

    # Run action IN
    url(r'^(?P<pk>\d+)/run_action_in/$',
        views_action.run_action_in,
        name='run_action_in'),

    #
    # Personalised text and JSON action steps
    #
    url(r'^item_filter/$',
        views_out.run_action_item_filter,
        name='item_filter'),
    url(r'^email_done/$', views_out.run_email_action_done, name='email_done'),
    url(r'^zip_done/$', views_out.run_zip_action_done, name='zip_done'),
    url(r'^zip_export/$', views_out.action_zip_export, name='zip_export'),
    url(r'^json_done/$', views_out.json_done, name='json_done'),

    #
    # ACTION IN EDIT PAGE
    #
    # Select key column for action in
    url(r'^(?P<apk>\d+)/(?P<cpk>\d+)/(?P<key>\d+)/select_column_action/$',
        views_action.select_column_action,
        name='select_key_column_action'),

    # Select column for action in
    url(r'^(?P<apk>\d+)/(?P<cpk>\d+)/select_column_action/$',
        views_action.select_column_action,
        name='select_column_action'),

    # Unselect column for action in
    url(r'^(?P<apk>\d+)/(?P<cpk>\d+)/unselect_column_action/$',
        views_action.unselect_column_action,
        name='unselect_column_action'),

    # Toggle shuffle action-in
    url(r'^(?P<pk>\d+)/shuffle_questions/$',
        views_action.shuffle_questions,
        name='shuffle_questions'),

    #
    # RUN SURVEY
    #
    # Server side update of the run survey page for action in
    url(r'^(?P<pk>\d+)/run_survey_ss/$',
        views_action.run_survey_ss,
        name='run_survey_ss'),

    # Run action in a row. Can be executed by the instructor or the
    # learner!!
    url(r'^(?P<pk>\d+)/run_survey_row/$',
        views_action.run_survey_row,
        name='run_survey_row'),

    # Say thanks
    url(r'thanks/$', views_action.thanks, name='thanks'),

    #
    # Preview action out
    #
    url(r'^(?P<pk>\d+)/(?P<idx>\d+)/preview/$',
        views_out.preview_response,
        name='preview'),

    # Allow url on/off toggle
    url(r'^(?P<pk>\d+)/showurl/$', views_action.showurl, name='showurl'),

    #
    # Serve the personalised content
    #
    url(r'^(?P<action_id>\d+)/serve/$', views_action.serve, name='serve'),

    #
    # DESCRIPTION
    #
    url(r'^(?P<pk>\d+)/edit_description/$',
        views_action.edit_description,
        name='edit_description'),

    #
    # FILTERS
    #
    url(r'^(?P<pk>\d+)/create_filter/$',
        views_condition.FilterCreateView.as_view(),
        name='create_filter'),

    url(r'^(?P<pk>\d+)/edit_filter/$',
        views_condition.edit_filter,
        name='edit_filter'),

    url(r'^(?P<pk>\d+)/delete_filter/$',
        views_condition.delete_filter,
        name='delete_filter'),

    #
    # CONDITIONS
    #
    url(r'^(?P<pk>\d+)/create_condition/$',
        views_condition.ConditionCreateView.as_view(),
        name='create_condition'),

    url(r'^(?P<pk>\d+)/edit_condition/$',
        views_condition.edit_condition,
        name='edit_condition'),

    url(r'^(?P<pk>\d+)/delete_condition/$',
        views_condition.delete_condition,
        name='delete_condition'),

    # Clone the condition
    url(r'^(?P<pk>\d+)/clone_condition/$',
        views_condition.clone,
        name='clone_condition'),

]
