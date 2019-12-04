# -*- coding: utf-8 -*-


import os
from test import ScreenTests

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ontask.dataops.pandas import destroy_db_engine


class Scenario2Captures(ScreenTests):

    workflow_name = 'Scenario 2'
    description = 'Scenario 2 in the documentation'

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
        self.selenium.find_element_by_id('id_wf_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                         'docs_src',
                         'Scenarios',
                         'scenario_02',
                         'scenario_02_wflow.gz')
        )

        # Click the import button
        self.selenium.find_element_by_xpath(
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_page(element_id='workflow-index')

        # Select the workflow
        self.access_workflow_from_home_page(self.workflow_name)

        # Open the right action
        self.open_action_edit('Welcome email')

        # Picture of the editor
        self.body_ss('scenario_02_text_all_conditions.png')

        # Edit the condition
        self.select_condition_tab()
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
        destroy_db_engine()
