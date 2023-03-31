# -*- coding: utf-8 -*-

"""Screen captures for scenario 1"""
import os

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ontask.tests.basic import ElementHasFullOpacity, ScreenTests


class Scenario1Captures(ScreenTests):

    workflow_name = 'Scenario 1'
    description = 'Scenario 1 in the documentation'

    def test(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Open Import page
        self.selenium.find_element(By.LINK_TEXT, 'Import workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
                                             'Import workflow')
        )

        #
        # Import workflow
        #
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            self.workflow_name
        )
        self.selenium.find_element(By.ID, 'id_wf_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                         'docs',
                         'Scenarios',
                         'scenario_01',
                         'scenario_01_wflow.gz')
        )

        # Click the import button
        self.selenium.find_element(
            By.XPATH,
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_page(element_id='workflow-index')

        # Select the workflow
        self.access_workflow_from_home_page(self.workflow_name)

        # Open the right action
        self.open_action_edit('Email students in SMED')

        # Picture of the editor
        self.body_ss('scenario_01_action_SMED.png')

        # Edit the filter
        self.select_filter_tab()
        self.selenium.find_element(By.CLASS_NAME, 'js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

        # Take picture of the modal
        self.modal_ss('scenario_01_action_filter.png')

        # Click in the cancel button
        self.cancel_modal()

        # Go to actions and open email
        self.go_to_actions()
        self.open_action_email('Email students in SMED')

        # Picture of the body
        self.body_ss('scenario_01_action_SMED_email.png')

        # End of session
        self.logout()
