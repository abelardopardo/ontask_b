# -*- coding: utf-8 -*-


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


class Scenario3Captures(ScreenTests):

    workflow_name = 'Scenario 3'
    description = 'Scenario 3 in the documentation'

    def setUp(self):
        super(Scenario3Captures, self).setUp()
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
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
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
                         'scenario_03',
                         'scenario_03_wflow.gz')
        )

        # Click the import button
        self.selenium.find_element_by_xpath(
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_page(element_id='workflow-index')

        # Select the workflow
        self.access_workflow_from_home_page(self.workflow_name)

        # Open the right action
        self.open_action_edit('Send email with suggestions')

        # Picture of the editor
        self.body_ss('scenario_03_text.png')

        # Open the modal with the filter
        self.select_filter_tab()
        self.open_filter()

        # Take picture of the filter
        self.modal_ss('scenario_03_filter.png')

        # Click in the cancel button
        self.cancel_modal()

        # Edit condition 1
        self.select_condition_tab()
        self.open_condition('Bottom third')

        # Take picture of the modal
        self.modal_ss('scenario_03_condition_one.png')

        # Click in the cancel button
        self.cancel_modal()

        # Edit condition 2
        self.open_condition('Middle underperforming')

        # Take picture of the modal
        self.modal_ss('scenario_03_condition_two.png')

        # Click in the cancel button
        self.cancel_modal()

        # Go back to actions
        self.go_to_actions()

        # Open the email action
        self.open_action_email('Send email with suggestions')

        # Capture the email
        self.body_ss('scenario_03_email.png')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
