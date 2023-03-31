# -*- coding: utf-8 -*-

"""Tests redirection to home when no workflow is selected."""

from django.urls import reverse
from rest_framework import status

from ontask import tests


class BackToHome(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase
):
    """Test redirection to home page when no workflow is set."""

    def test(self):
        """Loop over all URLs and check they redirect appropriately."""
        redirect = [
            # Workflow
            reverse('workflow:operations'),
            # Column
            reverse('column:index'),
            reverse('column:column_move_bottom', kwargs={'pk': 1}),
            reverse('column:column_move_top', kwargs={'pk': 1}),
            # Action
            reverse('action:index'),
            reverse('action:timeline'),
            reverse('action:timeline', kwargs={'pk': 1}),
            reverse('action:edit', kwargs={'pk': 1}),
            reverse('action:export', kwargs={'pklist': '1'}),
            reverse('action:import'),
            reverse('action:item_filter'),
            reverse('action:run', kwargs={'pk': 1}),
            reverse('action:run_done'),
            reverse('action:zip_action', kwargs={'pk': 1}),
            reverse(
                'action:unselect_column_action',
                kwargs={'pk': 1, 'cpk': 1}),
            reverse('action:run_survey_row', kwargs={'pk': 1}),
            # Connection
            reverse('connection:sqlconns_index'),
            reverse('connection:athenaconns_index'),
            # Dataops
            reverse('dataops:uploadmerge'),
            reverse('dataops:transform'),
            reverse('dataops:model'),
            reverse('dataops:plugin_invoke', kwargs={'pk': 1}),
            reverse('dataops:rowupdate'),
            reverse('dataops:rowcreate'),
            reverse('dataops:csvupload_start'),
            reverse('dataops:excelupload_start'),
            reverse('dataops:googlesheetupload_start'),
            reverse('dataops:s3upload_start'),
            reverse('dataops:upload_s2'),
            reverse('dataops:upload_s3'),
            reverse('dataops:upload_s4'),
            reverse('dataops:sqlupload_start', kwargs={'pk': 1}),
            reverse('dataops:athenaupload_start', kwargs={'pk': 1}),
            # Logs
            reverse('logs:page_view', kwargs={'pk': 1}),
            # Table
            reverse('table:display_view', kwargs={'pk': 1}),
            reverse('table:stat_column', kwargs={'pk': 1}),
            reverse('table:stat_table'),
            reverse('table:stat_table_view', kwargs={'pk': 1}),
            reverse('table:csvdownload'),
            reverse('table:csvdownload_view', kwargs={'pk': 1}),
        ]

        bad_request = [
            # Workflow
            reverse('workflow:attribute_create'),
            reverse('workflow:attribute_edit', kwargs={'pk': 0}),
            reverse('workflow:attribute_delete', kwargs={'pk': 0}),
            reverse('workflow:share_create'),
            # Column
            reverse('column:index_ss'),
            reverse('column:create'),
            reverse('column:question_add', kwargs={'pk': 1}),
            reverse('column:formula_column_add'),
            reverse('column:random_column_add'),
            reverse('column:delete', kwargs={'pk': 1}),
            reverse('column:column_edit', kwargs={'pk': 1}),
            reverse('column:column_clone', kwargs={'pk': 1}),
            reverse('column:column_move'),
            reverse('column:column_restrict', kwargs={'pk': 1}),
            # Action
            reverse('action:create'),
            reverse('action:update', kwargs={'pk': 1}),
            reverse('action:clone', kwargs={'pk': 1}),
            reverse('action:delete', kwargs={'pk': 1}),
            reverse(
                'action:select_key_column_action',
                kwargs={'pk': 1, 'cpk': 1, 'key': 1}),
            reverse('action:select_column_action', kwargs={'pk': 1, 'cpk': 1}),
            reverse('action:shuffle_questions', kwargs={'pk': 1}),
            reverse(
                'action:edit_in_select_condition',
                kwargs={'pk': 1, 'condpk': 1}),
            reverse('action:edit_in_select_condition', kwargs={'pk': 1}),
            reverse('action:show_survey_table_ss', kwargs={'pk': 1}),
            reverse('action:preview', kwargs={'pk': 1, 'idx': 0}),
            reverse('action:preview_all_false', kwargs={'pk': 1, 'idx': 0}),
            reverse('action:showurl', kwargs={'pk': 1}),
            reverse('action:edit_description', kwargs={'pk': 1}),
            # Condition
            reverse('condition:create_filter', kwargs={'pk': 1}),
            reverse('condition:edit_filter', kwargs={'pk': 1}),
            reverse('condition:delete_filter', kwargs={'pk': 1}),
            reverse('condition:create_condition', kwargs={'pk': 1}),
            reverse('condition:edit_condition', kwargs={'pk': 1}),
            reverse('condition:delete_condition', kwargs={'pk': 1}),
            reverse('condition:clone_condition', kwargs={'pk': 1}),
            reverse(
                'condition:clone_condition',
                kwargs={'pk': 1, 'action_pk': 1}),
            # Connection
            reverse('connection:sqlconn_view', kwargs={'pk': 1}),
            reverse('connection:athenaconn_view', kwargs={'pk': 1}),
            # Dataops
            reverse('dataops:plugin_diagnose', kwargs={'pk': 1}),
            reverse('dataops:plugin_moreinfo', kwargs={'pk': 1}),
            # Logs
            reverse('logs:display_ss'),
            reverse('logs:modal_view', kwargs={'pk': 1}),
            # Table
            reverse('table:display_ss'),
            reverse('table:display_view_ss', kwargs={'pk': 1}),
            reverse('table:row_delete'),
            reverse('table:view_add'),
            reverse('table:stat_column_JSON', kwargs={'pk': 1}),
            reverse('table:view_edit', kwargs={'pk': 1}),
            reverse('table:view_clone', kwargs={'pk': 1}),
            reverse('table:view_delete', kwargs={'pk': 1}),
        ]

        self.client.login(email='instructor01@bogus.com', password='boguspwd')

        resp = self.client.get(reverse('home'))
        self.assertTrue(status.is_success(resp.status_code))

        for url_name in redirect:
            resp = self.client.get(url_name)
            self.assertEqual(
                resp.status_code,
                status.HTTP_302_FOUND,
                msg='URL name: {0}'.format(url_name))
            self.assertEqual(resp.url, reverse('home'))

        for url_name in bad_request:
            resp = self.client.get(url_name)
            self.assertEqual(resp.status_code, 400)
