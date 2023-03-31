# -*- coding: utf-8 -*-

"""Screen captures for scenario 4"""
import os
from time import sleep

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ontask import models
from ontask.tests.basic import ElementHasFullOpacity, ScreenTests


class TutorialCaptures(ScreenTests):
    workflow_name = 'BIOL1011'
    description = 'Course on Cell Biology'

    script1 = 'Dear {{ GivenName }}\n'
    script2 = \
        '{% if Program is FASS %}Some suggestions for FASS{% endif %}\n'
    script3 = \
        '{% if Program is FSCI %}Some suggestions for FSCI{% endif %}\n' + \
        '{% if Program is FEIT %}Some suggestions for FEIT{% endif %}\n' + \
        '{% if Program is SMED %}Sme suggestions for SMED{% endif %}\n' + \
        'Kind regards\n' + \
        'Jane Doe'

    def test(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        question_values = 'DNA duplication, Mitosis, Kreb\'s cycle, None'

        # Login
        self.login('instructor01@bogus.com')

        #
        # Create the workflow
        #
        self.create_new_workflow(self.workflow_name, self.description)

        # Go to CSV upload/merge
        self.selenium.find_element_by_xpath(
            '//tbody/tr[1]/td[1]/a[1]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form')
            )
        )

        # Set the file name
        self.selenium.find_element_by_id('id_data_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                'docs',
                'Dataset',
                'all_data.csv')
        )

        self.body_ss('tutorial_csv_upload_learner_information.png')

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            '//button[@name="Submit"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, '//body/div/h1'),
                'Select Columns')
        )

        # Uncheck two elements
        element = self.search_table_row_by_string('workflow-table',
            2,
            'Surname')
        element.find_element_by_xpath('td[5]/input').click()
        element = self.search_table_row_by_string('workflow-table',
            2,
            'GivenName')
        element.find_element_by_xpath('td[5]/input').click()

        self.body_ss('tutorial_csv_upload_confirm.png')

        # Click on the Next button
        self.selenium.find_element_by_xpath(
            '//button[@name="Submit"]'
        ).click()
        self.wait_for_id_and_spinner('table-data_paginate')

        # Take picture of the table
        self.body_ss('tutorial_initial_table.png')

        # Take picture of the top-bar menu
        self.element_ss('//nav[contains(@class, "fixed-top")]',
            'tutorial_top_menu_bar.png')

        # Go back to details
        self.go_to_details()
        self.body_ss('tutorial_details_1.png')

        # Go back to details
        self.go_to_workflow_operations()
        self.body_ss('tutorial_workflow_operations.png')

        # Create a new view
        self.go_to_table()

        # Button to dropdown the Views and create one
        self.click_dropdown_option_num_and_wait('select-view-name', 1)

        # Insert data to create the view
        element = self.selenium.find_element_by_id('id_name')
        element.click()
        element.clear()
        element.send_keys('Subset 1')
        element = self.selenium.find_element_by_id('id_description_text')
        element.click()
        element.clear()
        element.send_keys(
            'View only student email, program and enrolment type')

        # Focus on the column area
        self.selenium.find_element_by_xpath(
            '//*[@placeholder="Click here to search"]').click()
        options = self.selenium.find_element_by_xpath(
            '//*[@id="div_id_columns"]//div[@class="sol-selection"]'
        )
        for cname in ['email', 'Program', 'Enrolment Type']:
            options.find_element_by_xpath(
                'div/label/div[normalize-space()="{0}"]'.format(cname)
            ).click()

        self.selenium.find_element_by_css_selector('div.modal-header').click()

        self.modal_ss('tutorial_table_view_create.png')

        # Save the view
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Add view"]'
        ).click()
        self.wait_close_modal_refresh_table('table-data_previous')

        # Take picture of the table
        self.body_ss('tutorial_table_view.png')

        # select the statistics of one of the learners
        element = self.search_table_row_by_string('table-data',
            2,
            'ckrn7263@bogus.com')
        element = element.find_element_by_xpath('td[1]/div/button[2]')
        self.selenium.execute_script(element.get_attribute('onclick'))
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//div[@class="text-center"]/a[normalize-space()="Back"]')
            )
        )

        # Picture of the statistics.
        self.body_ss('tutorial_row_statistics.png')

        # Go to the actions page
        self.go_to_actions()
        self.body_ss('tutorial_action_index.png')

        # Go to the import action page
        self.selenium.find_element_by_link_text('Import actions').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@name="Submit"]')))
        self.body_ss('tutorial_action_import.png')
        self.go_to_actions()

        #
        # Merge data from Moodle
        #
        self.go_to_upload_merge()
        self.selenium.find_element_by_link_text('CSV').click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )
        self.selenium.find_element_by_id('id_data_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                'docs',
                'Dataset',
                'moodle_grades.csv')
        )

        # Picture of the body
        self.body_ss('tutorial_moodle_merge_step1.png')

        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            '//button[@type="Submit"]'
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@id="id_make_key_2"]')
            )
        )

        # Uncheck all the columns
        self.selenium.find_element_by_id('checkAll').click()

        # Check the columns to select and maintain email as unique
        for k_num in [0, 1, 2]:
            self.selenium.find_element_by_id(
                'id_upload_{0}'.format(k_num)
            ).click()
        self.selenium.find_element_by_id('id_new_name_2').clear()
        self.selenium.find_element_by_id('id_new_name_2').send_keys('email')
        # self.selenium.find_element_by_id('id_make_key_2').click()

        # Picture of the body
        self.body_ss('tutorial_moodle_merge_step2.png')

        # Click the NEXT button
        self.selenium.find_element_by_xpath('//button[@type="Submit"]').click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//select[@id="id_dst_key"]')
            )
        )

        # Dataops/Merge CSV Merge Step 3
        Select(self.selenium.find_element_by_id(
            'id_dst_key'
        )).select_by_visible_text('email')
        Select(self.selenium.find_element_by_id(
            'id_src_key'
        )).select_by_visible_text('email')
        Select(self.selenium.find_element_by_id(
            'id_how_merge'
        )).select_by_value('right')

        # Picture of the body
        self.body_ss('tutorial_moodle_merge_step3.png')

        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            '//button[@type="Submit"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//body/div/h1'), 'Review and confirm')
        )

        # Picture of the body
        self.body_ss('tutorial_moodle_merge_step4.png')

        # Click on Finish
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Finish"]'
        ).click()
        self.wait_for_id_and_spinner('table-data_previous')

        #
        # Create PERSONALISED ACTION.
        #
        self.go_to_actions()
        self.selenium.find_element_by_class_name('js-create-action').click()
        self.wait_for_modal_open()

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys('Program advice')
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(models.Action.PERSONALIZED_TEXT)
        desc.send_keys('')

        self.modal_ss('tutorial_personalized_text_create.png')

        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, 'action-out-editor')
            )
        )
        self.wait_for_spinner()

        # Action editor
        self.body_ss('tutorial_personalized_text_editor.png')

        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.find_element_by_class_name('note-editable').send_keys(
            self.script1
        )

        # Take picture of the html editor
        self.element_ss('//div[@id="html-editor"]',
            'tutorial_personalized_text_editor_with_column.png')

        # Create the first condition
        self.select_condition_tab()
        self.create_condition(
            'Program is FASS',
            '',
            [('Program', 'equal', 'FASS')]
        )
        self.open_condition('Program is FASS')

        self.modal_ss('tutorial_condition_program_FASS.png')

        self.cancel_modal()

        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.find_element_by_class_name('note-editable').send_keys(
            self.script2
        )

        # Take picture of the html editor
        self.element_ss('//div[@id="html-editor"]',
            'tutorial_personalized_text_condition_inserted.png')

        # Create the remaining conditions
        self.select_condition_tab()
        self.create_condition('Program is FSCI',
            '',
            [('Program', 'equal', 'FSCI')]
        )
        self.create_condition('Program is FEIT',
            '',
            [('Program', 'equal', 'FEIT')]
        )
        self.create_condition('Program is SMED',
            '',
            [('Program', 'equal', 'SMED')]
        )

        # Insert additional sentences for each program
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.find_element_by_class_name('note-editable').send_keys(
            self.script3
        )

        # Take picture of the html editor
        self.element_ss('//div[@id="html-editor"]',
            'tutorial_personalized_text_condition_inserted2.png')

        # Open the filter condition
        self.select_filter_tab()
        self.create_filter('Full time attendance',
            [('Attendance', 'equal', 'Full Time')])
        # Open it again for the picture
        self.open_filter()
        self.modal_ss('tutorial_personalized_text_filter.png')

        # Close the modal
        self.cancel_modal()

        # Action editor
        self.body_ss('tutorial_personalized_text_editor2.png')

        # Open the preview
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Preview"]'
        ).click()
        # Wail until the data-dismiss element appears in the modal
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//div[@id="modal-item"]//button[@data-dismiss="modal"]')
            )
        )
        self.modal_ss('tutorial_personalized_text_preview.png')

        self.cancel_modal()

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Close"]'
        ).click()
        self.wait_for_id_and_spinner('action-index')

        # Click in the email button
        self.open_action_run('Program advice')

        # Set the various fields in the form to send the email
        self.selenium.find_element_by_id('id_subject').send_keys(
            'Connecting your program with this course'
        )
        select = Select(self.selenium.find_element_by_id(
            'id_item_column'))
        select.select_by_visible_text('email')
        self.selenium.find_element_by_id('id_cc_email').send_keys(
            'tutor1@example.com tutor2@example.com'
        )
        self.selenium.find_element_by_id('id_bcc_email').send_keys(
            'coursecoordinator@bogus.com'
        )
        self.selenium.find_element_by_id('id_confirm_items').click()

        # Screen shot of the body
        self.body_ss('action_personalized_text_email.png')

        # Click in the preview
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Preview"]'
        ).click()
        self.wait_for_modal_open('//div[@id="preview-body"]')

        self.modal_ss('tutorial_email_preview.png')

        self.cancel_modal()

        # Click in the next button to go to the filter email screen
        self.selenium.find_element_by_xpath(
            '//button[@name="Submit"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//body/div/h1'),
                'Select items to exclude from action')
        )

        # Select two emails to exclude from the send.
        self.selenium.find_element_by_css_selector(
            'div.sol-input-container > input[type="text"]'
        ).click()
        self.selenium.find_element_by_name('exclude_values').click()
        self.selenium.find_element_by_xpath(
            '(//input[@name="exclude_values"])[2]'
        ).click()
        self.selenium.find_element_by_xpath(
            '(//input[@name="exclude_values"])[3]'
        ).click()

        self.body_ss('tutorial_exclude_action_items.png')

        # Cancel email and go back to action index
        self.selenium.find_element_by_link_text('Cancel').click()
        self.wait_for_id_and_spinner('action-index')

        # Click in the URL link
        self.open_action_operation('Program advice', 'fa-link')

        # Capture the modal with the URL
        self.modal_ss('tutorial_personalzed_text_URL.png')

        # Cancel the modal
        self.cancel_modal()

        #
        # Download ZIP (for Moodle)
        #
        self.open_action_operation(
            'Program advice',
            'fa-file-archive',
            'zip-action-request-data')

        # Select the key column
        select = Select(self.selenium.find_element_by_id(
            'id_item_column')
        )
        select.select_by_visible_text('Identifier')
        select = Select(self.selenium.find_element_by_id(
            'id_user_fname_column')
        )
        select.select_by_visible_text('Full name')
        self.selenium.find_element_by_id('id_file_suffix').send_keys(
            'feedback.html'
        )
        self.selenium.find_element_by_id('id_zip_for_moodle').click()

        self.body_ss('tutorial_action_zip.png')

        # Click in the Cancel button
        self.selenium.find_element_by_link_text('Cancel').click()

        #
        # Create new personalized JSON Action
        #
        self.selenium.find_element_by_class_name('js-create-action').click()
        self.wait_for_modal_open()

        # Select the options to create a personalized JSON and then close the
        # screen
        self.selenium.find_element_by_id('id_name').send_keys(
            'Send JSON to remote server'
        )
        desc = self.selenium.find_element_by_id(
            'id_description_text'
        )
        desc.send_keys(
            'Send a JSON object to a remote server (outside this platform)'
        )
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(models.Action.PERSONALIZED_JSON)
        desc.send_keys('')

        self.modal_ss('tutorial_personalized_json_create.png')

        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.ID, 'action-out-editor')
            )
        )
        self.wait_for_spinner()

        self.create_condition('Less than 50 in the midterm',
            '',
            [('Total', 'less', '50')])
        self.create_condition('More or equal to 50 in midterm',
            '',
            [('Total', 'greater or equal', '50')])

        self.select_json_text_tab()
        self.selenium.find_element_by_id('id_text_content').send_keys(
            """{
  "sid": {{ SID }},
  "midterm_total": {{ Total }},
  "msg":
     {% if Less than 50 in the midterm %}"Message number 1"{% endif %}
    {% if More or equal to 50 in midterm %}"Message number 2"{% endif %}
}"""
        )

        self.selenium.find_element_by_id('id_target_url').send_keys(
            'http://127.0.0.1'
        )

        # Action editor
        self.body_ss('tutorial_personalized_json_editor.png')

        # Open the preview
        self.open_preview()
        self.modal_ss('tutorial_personalized_json_preview.png')

        self.cancel_modal()

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Close"]'
        ).click()
        self.wait_for_id_and_spinner('action-index')

        #
        # Click on the create action SURVEY
        #
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys('Survey 1')
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(models.Action.SURVEY)
        desc.send_keys('Survey description for the learners')

        self.modal_ss('tutorial_survey_create.png')

        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="action-in-editor"]')
            )
        )
        self.wait_for_spinner()

        # Show the editor
        self.body_ss('tutorial_survey_editor.png')

        # Click on the Add Column button
        self.select_questions_tab()
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Create question"]'
        ).click()
        self.wait_for_modal_open()

        # Set the fields
        self.selenium.find_element_by_id('id_name').send_keys('Survey Q1')
        self.selenium.find_element_by_id(
            'id_description_text'
        ).send_keys(
            'What was the most challenging topic for you this week?'
        )
        select = Select(self.selenium.find_element_by_id(
            'id_data_type'))
        select.select_by_visible_text('string')
        self.selenium.find_element_by_id(
            'id_raw_categories'
        ).send_keys(question_values)

        self.modal_ss('tutorial_survey_column_creation.png')

        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[normalize-space()="Add question"]'
        ).click()

        self.wait_close_modal_refresh_table('column-selected-table_previous')

        # Create the second column
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Create question"]'
        ).click()
        self.wait_for_modal_open()

        # Set the fields
        self.selenium.find_element_by_id('id_name').send_keys('Survey Q2')
        self.selenium.find_element_by_id(
            'id_description_text'
        ).send_keys(
            'What was your dedication to the course this week?'
        )
        select = Select(self.selenium.find_element_by_id(
            'id_data_type'))
        select.select_by_value('string')
        self.selenium.find_element_by_id(
            'id_raw_categories'
        ).send_keys(
            'less than 2 hours,'
            'between 2 and 4 hours,'
            'between 4 and 6 hours,'
            'more than 6 hours')

        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[normalize-space()="Add question"]'
        ).click()

        self.wait_close_modal_refresh_table('column-selected-table_previous')

        # Click in the key-select
        self.select_parameters_tab()

        # Select email column as key column
        self.click_dropdown_option('select-key-column-name', 'email')

        # Table disappears (page is updating) -- Wait for spinner, and then
        # refresh
        self.wait_for_spinner()

        # Show the editor
        self.select_questions_tab()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'insert-questions'))
        )
        self.select_parameters_tab()
        self.select_questions_tab()
        sleep(1)
        self.body_ss('tutorial_survey_editor2.png')

        # Click the preview button
        self.open_preview()
        self.modal_ss('tutorial_survey_preview.png')

        self.cancel_modal()

        # Save action and back to action index
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_id_and_spinner('action-index')

        #
        # Create an new action combining existing data with survey data
        #
        self.create_new_personalized_text_action('More Strategies', '')

        # Create the conditions for those that failed the exam
        self.select_condition_tab()
        topics = [x.strip() for x in question_values.split(',')]
        for topic in topics:
            self.create_condition(
                topic[0:4].strip() + ' - Fail',
                '',
                [('Survey Q1', 'equal', topic),
                 ('Total', 'less', 50)]
            )
        # Create the conditions for those that passed the exam
        for topic in topics:
            self.create_condition(
                topic[0:4].strip() + ' - Passed',
                '',
                [('Survey Q1', 'equal', topic),
                 ('Total', 'greater or equal', 50)]
            )

        # Action editor
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.find_element_by_class_name('note-editable').send_keys(
            'Dear {{ GivenName }}\n' +
            'Here are some suggestions.\n'
        )

        # Add the text for those that failed
        for topic in topics:
            self.selenium.find_element_by_class_name('note-editable').send_keys(
                ('{{% if {0} - Fail %}} Tips about {0} ' +
                 'for those that failed.{{% endif %}}\n').format(
                    topic[0:4].strip())
            )

        # Add the text for those that passed
        for topic in topics:
            self.selenium.find_element_by_class_name('note-editable').send_keys(
                ('{{% if {0} - Passed %}}Tips about {0} ' +
                 'for those that passed.{{% endif %}}\n').format(
                    topic[0:4].strip())
            )

        self.selenium.find_element_by_class_name('note-editable').send_keys(
            'Kind regards -- Jane Doe'
        )

        # Create the filter
        self.select_filter_tab()
        self.create_filter('Complete data',
            [('Survey Q1', 'is not null', None),
             ('Total', 'is not null', None)])

        # Open to take the picture
        self.open_filter()
        self.modal_ss('tutorial_personalized_text_and_survey_filter.png')
        self.cancel_modal()

        # Action editor
        self.select_text_tab()
        self.body_ss('tutorial_personalized_text_and_survey.png')

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Close"]'
        ).click()
        self.wait_for_id_and_spinner('action-index')

        # End of session
        self.logout()
