# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

import time
from django.conf import settings
from django.shortcuts import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

import test
from dataops import pandas_db
from dataops.formula_evaluation import has_variable
from workflow.models import Workflow
from action.models import Action, Column, Condition

class ActionActionEdit(test.OntaskLiveTestCase):
    fixtures = ['simple_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_action_df.sql'
    )

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    def setUp(self):
        super(ActionActionEdit, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(ActionActionEdit, self).tearDown()

    # Test operations with the filter
    def test_action_01_filter(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text(self.wflow_name)
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'wflow-name')))

        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        self.assertIn('New Action', self.selenium.page_source)

        # click in the action page
        self.selenium.find_element_by_link_text('Edit').click()
        # Wait for the action page
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='filter-set']/h4/div/button")
            )
        )

        # Click in the add filter button
        self.selenium.find_element_by_xpath(
            "//div[@id='filter-set']/h4/div/button"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create action filter')
        )

        # Add the name and description
        self.selenium.find_element_by_id('id_name').send_keys('fname')
        self.selenium.find_element_by_id(
            'id_description_text').send_keys('fdesc')

        # Select the age filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        sel.select_by_value('age')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # There should only be eight operands
        filter_ops = self.selenium.find_elements_by_xpath(
            "//select[@name='builder_rule_0_operator']/option"
        )
        self.assertEqual(len(filter_ops), 8)

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('Selects 2 out of 3 rows', self.selenium.page_source)

        # Add a second clause to the filter
        # Click in the edit filter button
        self.selenium.find_element_by_class_name('js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Edit filter')
        )

        # Click in the Add rule of the filter builder button
        self.selenium.find_element_by_xpath(
            "//dl[@id='builder_group_0']/dt/div/button[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//dl[@id='builder_group_0']/dt/div/button[1]")
            )
        )

        # Select the when filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_1_filter'))
        sel.select_by_value('when')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_1_operator']")
            )
        )

        # There should only be eight operands
        filter_ops = self.selenium.find_elements_by_xpath(
            "//select[@name='builder_rule_1_operator']/option"
        )
        self.assertEqual(len(filter_ops), 8)

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_1_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 2017-10-11T00:32:44
        self.selenium.find_element_by_name(
            'builder_rule_1_value_0').send_keys('2017-10-11T00:32:44')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh
        # WebDriverWait(self.selenium, 10).until(
        #     EC.element_to_be_clickable(
        #         (By.CLASS_NAME, 'js-filter-edit')
        #     )
        # )
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('Selects 1 out of 3 rows', self.selenium.page_source)

        # End of session
        self.logout()

    # Test operations with the conditions and the email preview
    def test_action_02_condition(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text(self.wflow_name)
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'wflow-name')))

        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-create-action')
            )
        )
        self.assertIn('New Action', self.selenium.page_source)

        # click in the action page
        self.selenium.find_element_by_link_text('Edit').click()
        # Wait for the action page
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='filter-set']/h4/div/button")
            )
        )

        # Click in the add condition button
        self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/h4/button"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add the name and description
        self.selenium.find_element_by_id('id_name').send_keys('c1')
        self.selenium.find_element_by_id(
            'id_description_text').send_keys('cdesc1')

        # Select the age filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        sel.select_by_value('age')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Click in the add a second condition
        self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/h4/button"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add the name and description
        self.selenium.find_element_by_id('id_name').send_keys('c2')
        self.selenium.find_element_by_id(
            'id_description_text').send_keys('cdesc2')

        # Select the age filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        sel.select_by_value('age')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('greater')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Action now has two complementary conditions, add the conditions to
        # the message
        self.selenium.execute_script(
            """$('#id_content').summernote(
                   'editor.insertText', 
                   "{% if c1 %}Low{% endif %}{% if c2 %}High{% endif %}")""")

        # Save the action
        self.selenium.find_element_by_xpath(
            "//div[@id='html-editor']/form/div[3]/button[2]"
        ).click()
        # This is a pure javascript submission, no other way to catch it
        time.sleep(5)
        # with self.wait_for_page_load(timeout=10):
        #     self.selenium.find_element_by_link_text('Details')

        # Click the preview button
        self.selenium.find_element_by_xpath(
            "//div[@id='html-editor']/form/div[3]/button[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-action-preview-nxt')
            )
        )

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element_by_class_name(
            'js-action-preview-nxt').click()

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element_by_class_name(
            'js-action-preview-nxt').click()

        # First value should be high age
        self.assertIn('High', self.selenium.page_source)

        # End of session
        self.logout()

    # Test send_email operation
    def test_action_03_send_email(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text(self.wflow_name)
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Workflow Details')
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'success'))
        )

        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        self.assertIn('New Action', self.selenium.page_source)

        # Click in the page to send email
        self.selenium.find_element_by_link_text('Email').click()

        # Set the subject of the email
        self.selenium.find_element_by_id('id_subject').send_keys('Subject TXT')
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-header'),
                'Send emails')
        )

        # Set the email column
        select = Select(self.selenium.find_element_by_id(
            'id_email_column'))
        select.select_by_value('email')

        # Tick the track email
        self.selenium.find_element_by_id('id_track_read').click()

        # Tick add column
        self.selenium.find_element_by_id('id_add_column').click()

        # Click the send button
        self.selenium.find_element_by_class_name('btn-success').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-header'),
                'Email action')
        )

        # There should be a message on that page
        self.assertIn('Emails successfully sent', self.selenium.page_source)

        # Go to the table page
        self.open(reverse('table:display'))
        # Wait for
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-workflow-column-add')
            )
        )

        # There should be a column for the email tracking
        self.assertIn('EmailRead_1', self.selenium.page_source)

        # Make sure the workflow is consistent
        pandas_db.check_wf_df(Workflow.objects.get(name=self.wflow_name))

        # End of session
        self.logout()

    def test_action_04_save_action_with_buttons(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text(self.wflow_name)
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'wflow-name')))

        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        self.assertIn('New Action', self.selenium.page_source)

        # click in the action page
        self.selenium.find_element_by_link_text('Edit').click()
        # Wait for the action page
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='filter-set']/h4/div/button")
            )
        )

        # Make sure the content has the correct text
        self.assertEqual(
            "{% comment %}Your action content here{% endcomment %}",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the first mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "mark1");"""
        )

        # Create filter. Click in the add filter button
        self.selenium.find_element_by_xpath(
            "//div[@id='filter-set']/h4/div/button"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create action filter')
        )

        # Add the name and description
        self.selenium.find_element_by_id('id_name').send_keys('fname')
        self.selenium.find_element_by_id(
            'id_description_text').send_keys('fdesc')

        # Select the age filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        sel.select_by_value('age')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-filter-edit')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "mark1",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "mark2");"""
        )

        # Modify the filter. Click in the edit filter button
        self.selenium.find_element_by_class_name('js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Edit filter')
        )

        # Modify its name
        self.selenium.find_element_by_id('id_name').send_keys('2')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-filter-edit')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "mark2",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the third mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "mark3");"""
        )

        # Click in the more ops and then the delete filter button
        self.selenium.find_element_by_xpath(
            "//div[@id='filter-set']/h4/div/button[2]"
        ).click()
        self.selenium.find_element_by_class_name('js-filter-delete').click()
        # Wait for the screen to delete the filter
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Confirm filter deletion')
        )

        # Click in the "delete filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "mark3",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )
        # insert the first mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark1");"""
        )

        # Create condition. Click in the add condition button
        self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/h4/button"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add the name and description
        self.selenium.find_element_by_id('id_name').send_keys('fname')
        self.selenium.find_element_by_id(
            'id_description_text').send_keys('fdesc')

        # Select the age filter
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        sel.select_by_value('age')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "create condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh (FLAKY)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "cmark1",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark2");"""
        )

        # Modify the filter. Click in the edit filter button
        self.selenium.find_element_by_class_name('js-condition-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Edit condition')
        )

        # Modify its name
        self.selenium.find_element_by_id('id_name').send_keys('2')

        # Click in the "update condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "cmark2",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the third mark
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark3");"""
        )

        # Click in the delete condition button
        self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/h4/div/button[2]"
        ).click()
        self.selenium.find_element_by_class_name('js-condition-delete').click()
        # Wait for the screen to delete the condition
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Confirm condition deletion')
        )

        # Click in the "delete condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Make sure the content has the correct text
        self.assertIn(
            "cmark3",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # End of session
        self.logout()


class ActionActionInCreate(test.OntaskLiveTestCase):
    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_workflow_two_actions.sql'
    )

    wflow_name = 'wflow2'
    wflow_desc = 'Simple workflow structure with two type of actions'
    wflow_empty = 'The workflow does not have data'

    def setUp(self):
        super(ActionActionInCreate, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(ActionActionInCreate, self).tearDown()

    # Test operations with the filter
    def test_action_01_data_entry(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # Select the workflow
        self.selenium.find_element_by_link_text("wflow2").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'success'))
        )

        # Open the actions page
        self.selenium.find_element_by_link_text("Actions").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'success'))
        )

        # Create new action
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()

        # Introduce information about the action in the form
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("new action in")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        # Introducting the information in the action editor
        self.selenium.find_element_by_xpath(
            "//dl[@id='builder_group_0']/dt/div[1]/button[1]"
        ).click()
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text("registered")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_4").click()
        # Submit the action
        self.selenium.find_element_by_xpath(
            "(//button[@name='Submit'])[2]").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-action-showurl'))
        )

        # Run the action
        self.selenium.find_element_by_link_text('Run').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, "student2@bogus.com")
            )
        )
        # Enter data for the remaining user
        self.selenium.find_element_by_link_text("student2@bogus.com").click()
        # Mark as registered
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        # Submit form
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[2]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[@id='actioninrun-data']/tbody")
            )
        )
        self.assertIn('No matching records found', self.selenium.page_source)
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()

        # End of session
        self.logout()


class ActionActionRenameEffect(test.OntaskLiveTestCase):
    """This test case is to check the effect of renaming columns, attributes
       and conditions. These name changes need to propagate throughout various
       elements attached to the workflow
    """

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_workflow_two_actions.sql'
    )

    wflow_name = 'wflow2'

    def setUp(self):
        super(ActionActionRenameEffect, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(ActionActionRenameEffect, self).tearDown()

    # Test operations with the filter
    def test_action_01_rename_column_condition_attribute(self):
        # First get objects for future checks
        workflow = Workflow.objects.get(name=self.wflow_name)
        column = Column.objects.get(
            name='registered',
            workflow=workflow
        )
        attributes = workflow.attributes
        action_in = Action.objects.get(
            name='Check registration',
            workflow=workflow
        )
        action_out = Action.objects.get(
            name='Detecting age',
            workflow=workflow
        )
        condition = Condition.objects.get(
            name='Registered',
            action=action_out,
        )

        # pre-conditions
        # Column name is the correct one
        self.assertEqual(column.name, 'registered')
        # Condition name is the correct one
        self.assertEqual(condition.name, 'Registered')
        # Attribute name is the correct one
        self.assertEqual(attributes['attribute name'],
                         'attribute value')
        # Column name is present in condition formula
        self.assertTrue(has_variable(condition.formula,
                                     'registered'))
        # Column name is present in action_out text
        self.assertTrue('{{ registered }}' in action_out.content)
        # Attribute name is present in action_out text
        self.assertTrue('{{ attribute name }}' in action_out.content)
        # Column name is present in action-in filter
        self.assertTrue(has_variable(action_in.filter,
                                     'registered'))

        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # Select the workflow
        self.selenium.find_element_by_link_text("wflow2").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'success'))
        )

        # Click the button to rename the "registered" column
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[5]/td[4]/button/span"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'), 'Edit column')
        )
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Introduce the new column name and submit
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("registered new")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Click in the more ops button and then attribute
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]"
        ).click()
        self.selenium.find_element_by_link_text("Attributes").click()

        # Change the name of the attribute and submit
        self.selenium.find_element_by_id("id_attribute name").click()
        self.selenium.find_element_by_id("id_attribute name").clear()
        self.selenium.find_element_by_id(
            "id_attribute name"
        ).send_keys("attribute name new")
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]"
        ).click()

        # Go to the actions and select the edit button of the action out
        self.selenium.find_element_by_link_text("Actions").click()
        self.selenium.find_element_by_xpath(
            "//table[@id='action-table']/tbody/tr[2]/td[5]/div/a"
        ).click()

        # Click the button to edit a condition and change its name
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[6]"
        ).click()
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("Registered new")
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]"
        ).click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Refresh variables
        workflow = Workflow.objects.get(pk=workflow.id)
        column = Column.objects.get(pk=column.id)
        attributes = workflow.attributes
        action_in = Action.objects.get(pk=action_in.id)
        action_out = Action.objects.get(pk=action_out.id)
        condition = Condition.objects.get(pk=condition.id)

        # Post conditions
        # Column name is the correct one
        self.assertEqual(column.name, 'registered new')
        # Condition name is the correct one
        self.assertEqual(condition.name, 'Registered new')
        # Attribute name is the correct one
        self.assertEqual(attributes['attribute name new'],
                         'attribute value')
        # Column name is present in condition formula
        self.assertFalse(has_variable(condition.formula,
                                     'registered'))
        self.assertTrue(has_variable(condition.formula,
                                     'registered new'))
        # Column name is present in action_out text
        self.assertTrue('{{ registered new }}' in action_out.content)
        # Attribute name is present in action_out text
        #self.assertTrue('{{ attribute name new }}' in action_out.content)
        # Column name is present in action-in filter
        self.assertFalse(has_variable(action_in.filter,
                                     'registered'))
        self.assertTrue(has_variable(action_in.filter,
                                     'registered new'))

        # End of session
        self.logout()
