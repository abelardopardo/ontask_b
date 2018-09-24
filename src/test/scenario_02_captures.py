# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db
from test import ElementHasFullOpacity, ScreenTests


class Scenario2Captures(ScreenTests):

    workflow_name = 'Scenario 2'
    description = 'Scenario 2 in the documentation'

    def setUp(self):
        super(Scenario2Captures, self).setUp()
        test.create_users()

    def test(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Open Import page
        self.selenium.find_element_by_link_text('Import workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Import workflow')
        )

        #
        # Import workflow
        #
        self.selenium.find_element_by_id('id_name').send_keys(
            self.workflow_name
        )
        self.selenium.find_element_by_id('id_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                         '..',
                         'docs_src',
                         'Scenarios',
                         'scenario_02',
                         'scenario_02_wflow.gz')
        )

        # Click the import button
        self.selenium.find_element_by_xpath(
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_datatable('workflow-table_previous')

        # Select the workflow
        self.access_workflow_from_home_page(self.workflow_name)

        # Go to actions
        self.go_to_actions()

        # Open the right action
        self.open_action_edit('Welcome email')

        # Picture of the editor
        self.body_ss('scenario_02_text_all_conditions.png')

        # Edit the condition
        self.open_condition('Student in FASS')

        # Take picture of the modal
        self.modal_ss('scenario_02_condition_FASS.png')

        # Click in the cancel button
        self.cancel_modal()

        # Click the preview
        self.open_preview()

        # Picture of the body
        self.modal_ss('scenario_02_preview.png')

        # Close the modal
        self.cancel_modal()

        # Go back to actions
        self.go_to_actions()

        # Open the email action
        self.open_action_email('Welcome email')

        # Capture the email
        self.body_ss('scenario_02_action_email.png')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
