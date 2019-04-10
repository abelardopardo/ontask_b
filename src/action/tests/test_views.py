# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

import test
from action.models import Action, Column, Condition
from dataops import pandas_db
from dataops.formula_evaluation import has_variable
from workflow.models import Workflow


class ActionActionEdit(test.OnTaskLiveTestCase):
    action_name = 'simple action'
    fixtures = ['simple_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_action.sql'
    )

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    def setUp(self):
        super(ActionActionEdit, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super(ActionActionEdit, self).tearDown()

    # Test action rename
    def test_action_00_rename(self):
        suffix = ' 2'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click on the action rename link
        self.open_action_rename(self.action_name)

        # Rename the action
        self.selenium.find_element_by_id('id_name').send_keys(suffix)
        # click in the Update button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('action-table_previous')

        action_element = self.search_action(self.action_name + suffix)
        self.assertTrue(action_element)

        # End of session
        self.logout()

    # Test operations with the filter
    def test_action_01_filter(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # click in EDIT action link
        self.open_action_edit(self.action_name)

        # Click in the add filter button
        self.select_filter_tab()
        self.selenium.find_element_by_class_name('js-filter-create').click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )

        # Add the description
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
        self.assertEqual(len(filter_ops), 10)

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element_by_name(
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Preview button clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'js-action-preview')]"),
            )
        )
        # Spinner not visible
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('2 learners of 3', self.selenium.page_source)

        # Add a second clause to the filter
        # Click in the edit filter button
        self.select_filter_tab()
        self.selenium.find_element_by_class_name('js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )

        # Click in the Add rule of the filter builder button
        self.selenium.find_element_by_xpath(
            "//div[@id='builder_group_0']/div/div/button[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='builder_group_0']/div/div/button[1]")
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
        self.assertEqual(len(filter_ops), 10)

        # Set the operator to less or equal
        sel = Select(self.selenium.find_element_by_name(
            'builder_rule_1_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 2017-10-11T00:32:44
        self.selenium.find_element_by_name(
            'builder_rule_1_value_0').send_keys('2017-10-11T00:32:44+1300')

        # Click in the "update filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to reload
        # Preview button clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'js-action-preview')]"),
            )
        )
        # Spinner not visible
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('1 learner of 3', self.selenium.page_source)

        # End of session
        self.logout()

    # Test operations with the conditions and the email preview
    def test_action_02_condition(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open workflow page
        self.access_workflow_from_home_page(self.wflow_name)

        # Edit the action
        self.open_action_edit(self.action_name)

        # Add condition
        self.select_condition_tab()
        self.create_condition('c1',
                              'cdesc1',
                              [('age', 'less or equal', '12.1')])

        # Click in the add a second condition
        self.select_condition_tab()
        self.create_condition('c2',
                              'cdesc2',
                              [('age', 'greater', '12.1')])

        # Action now has two complementary conditions, add the conditions to
        # the message
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote(
                   'editor.insertText', 
                   "{% if c1 %}Low{% endif %}{% if c2 %}High{% endif %}")""")

        # Click the preview button
        self.open_browse_preview(close=False)

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element_by_class_name(
            'js-action-preview-nxt').click()

        self.wait_for_modal_open(
            "//div[@id='modal-item']//div[@id='preview-body']"
        )

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element_by_class_name(
            'js-action-preview-nxt').click()

        self.wait_for_modal_open(
            "//div[@id='modal-item']//div[@id='preview-body']"
        )

        # First value should be high age
        self.assertIn('High', self.selenium.page_source)

        # End of session
        self.logout()

    # Test send_email operation
    def test_action_03_send_email(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click in the page to send email
        self.open_action_run(self.action_name)
        self.wait_for_datatable('email-action-request-data')

        # Set the subject of the email
        self.selenium.find_element_by_id('id_subject').send_keys('Subject TXT')

        # Set the email column
        select = Select(self.selenium.find_element_by_id(
            'id_email_column'))
        select.select_by_value('email')

        # Tick the track email
        self.selenium.find_element_by_id('id_track_read').click()

        # Click the send button
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Send']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Action scheduled for execution')
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                "//div[@id='action-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Check that the email has been properly stored
        assert len(mail.outbox) == 3

        # Go to the table page
        self.go_to_table()

        # There should be a column for the email tracking
        # This column is now added by Celery which needs to be running
        # with the same DB configuration (which is not).
        # self.assertIn('EmailRead_1', self.selenium.page_source)

        # Make sure the workflow is consistent
        pandas_db.check_wf_df(Workflow.objects.get(name=self.wflow_name))

        # End of session
        self.logout()

    def test_action_04_save_action_with_buttons(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # click in the action page
        self.open_action_edit(self.action_name)

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

        # Create filter.
        self.select_filter_tab()
        self.create_filter('fdesc', [('age', 'less or equal', '12.1')])

        # Make sure the content has the correct text
        self.assertIn(
            "mark1",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "mark2");"""
        )

        # Modify the filter. Click in the edit filter button
        self.select_filter_tab()
        self.edit_filter(None, '', [])

        # Make sure the content has the correct text
        self.assertIn(
            "mark2",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the third mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "mark3");"""
        )

        # Click in the more ops and then the delete filter button
        self.select_filter_tab()
        self.delete_filter()

        self.assertIn(
            "mark3",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )
        # insert the first mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark1");"""
        )

        # Create condition. Click in the add condition button
        self.create_condition('fname',
                              'fdesc',
                              [('age', 'less or equal', '12.1')])

        self.select_text_tab()
        self.assertIn(
            "cmark1",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark2");"""
        )

        # Modify the condition. Click in the condition edit button
        self.edit_condition('fname', 'fname2', '', [])

        # Make sure the content has the correct text
        self.select_text_tab()
        self.assertIn(
            "cmark2",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # insert the third mark
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', "cmark3");"""
        )

        # Delete the condition
        self.select_condition_tab()
        self.delete_condition('fname2')

        # Make sure the content has the correct text
        self.select_text_tab()
        self.assertIn(
            "cmark3",
            self.selenium.execute_script(
                """return $("#id_content").summernote('code')"""
            )
        )

        # End of session
        self.logout()

    # Test operations with the filter
    def test_action_05_JSON_action(self):
        action_name = 'JSON action'
        content_txt = '{ "name": 3 }'
        target_url = 'https://bogus.com'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Create new action
        self.create_new_json_action(action_name)

        # Introduce text and then the URL
        self.select_json_text_tab()
        self.selenium.find_element_by_id('id_content').send_keys(content_txt)
        self.selenium.find_element_by_id('id_target_url').send_keys(target_url)

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_datatable('action-table_previous')

        action = Action.objects.get(name=action_name)
        self.assertTrue(action.content == content_txt)
        self.assertTrue(action.target_url == target_url)

        # End of session
        self.logout()


class ActionActionInCreate(test.OnTaskLiveTestCase):
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
        test.delete_all_tables()
        super(ActionActionInCreate, self).tearDown()

    # Test operations with the filter
    def test_action_01_data_entry(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Create new action
        self.create_new_survey_action('new action in', '')

        # Click in the add rule button (the filter is initially empty)
        self.create_filter('', [('registered', None, False)])
        self.wait_close_modal_refresh_table('column-selected-table_previous')

        # Check that the filter is working properly
        self.assertIn('1 learner of 3', self.selenium.page_source)

        # Select email column as key column
        self.select_parameters_tab()
        self.click_dropdown_option("//div[@id='select-key-column-name']",
                                   'email')
        # Table disappears (page is updating) -- Wait for spinner, and then
        # refresh
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        self.select_questions_tab()
        self.click_dropdown_option(
            "//div[@id='column-selector']",
            'registered'
        )
        self.wait_for_datatable('column-selected-table_previous')

        # Submit the action
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_datatable('action-table_previous')

        # Run the action
        self.open_action_run('new action in', True)

        # Enter data for the remaining user
        self.selenium.find_element_by_link_text("student02@bogus.com").click()
        # Mark as registered
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        # Submit form
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[1]"
        ).click()
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'actioninrun-data_previous'))
        )
        self.assertIn('No matching records found', self.selenium.page_source)
        self.selenium.find_element_by_link_text('Back').click()

        # End of session
        self.logout()


class ActionActionRenameEffect(test.OnTaskLiveTestCase):
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
        test.delete_all_tables()
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
        Action.objects.get(name='Check registration', workflow=workflow)
        action_out = Action.objects.get(
            name='Detecting age',
            workflow=workflow
        )
        condition = Condition.objects.get(name='Registered', action=action_out)
        filter_obj = action_out.get_filter()

        # pre-conditions
        # Column name is the correct one
        self.assertEqual(column.name, 'registered')
        # Condition name is the correct one
        self.assertEqual(condition.name, 'Registered')
        # Attribute name is the correct one
        self.assertEqual(attributes['attribute name'], 'attribute value')
        # Column name is present in condition formula
        self.assertTrue(has_variable(condition.formula, 'registered'))
        # Column name is present in action_out text
        self.assertTrue('{{ registered }}' in action_out.content)
        # Attribute name is present in action_out text
        self.assertTrue('{{ attribute name }}' in action_out.content)
        # Column name is present in action-in filter
        self.assertTrue(has_variable(filter_obj.formula, 'age'))

        # Login
        self.login('instructor01@bogus.com')

        # Go to the details page
        self.access_workflow_from_home_page(self.wflow_name)

        # Click the button to rename the "registered" column
        self.go_to_details()
        self.open_column_edit('registered')

        # Introduce the new column name and submit
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("registered new")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        self.wait_close_modal_refresh_table('column-table_previous')

        # Click the button to rename the "age" column
        self.open_column_edit('age')

        # Introduce the new column name and submit
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("age new")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        self.wait_close_modal_refresh_table('column-table_previous')

        # Go to the attribute page
        self.go_to_attribute_page()

        # Change the name of the attribute and submit
        self.edit_attribute('attribute name',
                            'attribute name new',
                            'attribute value')

        # Go to the actions and select the edit button of the action out
        self.go_to_actions()
        self.open_action_edit('Detecting age')

        # Click the button to edit a condition and change its name
        self.edit_condition('Registered', 'Registered new', None, [])

        # Refresh variables
        workflow = Workflow.objects.get(pk=workflow.id)
        column = Column.objects.get(pk=column.id)
        attributes = workflow.attributes
        action_out = Action.objects.get(pk=action_out.id)
        condition = Condition.objects.get(pk=condition.id)
        filter_obj = action_out.get_filter()

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
        self.assertTrue('{{ attribute name new }}' in action_out.content)
        # Column age is present in action-in filter
        self.assertFalse(has_variable(filter_obj.formula, 'age'))
        self.assertTrue(has_variable(filter_obj.formula, 'age new'))

        # End of session
        self.logout()


class ActionActionZip(test.OnTaskLiveTestCase):
    """
    This test case is to check if the ZIP opeation is correct
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
        super(ActionActionZip, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super(ActionActionZip, self).tearDown()

    # Test operations with the filter
    def test_action_01_zip(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click in the page to send email
        self.open_action_zip('Detecting age')

        # The zip should include 2 files
        self.assertIn('A ZIP with 2 files will be created',
                      self.selenium.page_source)

        # Set column 1
        select = Select(self.selenium.find_element_by_id(
            'id_participant_column'))
        select.select_by_value('age')

        # Set column 2
        select = Select(self.selenium.find_element_by_id(
            'id_user_fname_column'))
        select.select_by_value('age')

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Next']").click()
        self.wait_for_page(element_id='zip-action-request-data')

        # Anomaly detected
        self.assertIn('The two columns must be different',
                      self.selenium.page_source)

        # Set column 2
        select = Select(self.selenium.find_element_by_id(
            'id_user_fname_column'))
        select.select_by_value('email')

        # Choose the Moodle option
        self.selenium.find_element_by_id('id_zip_for_moodle').click()

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Next']").click()
        self.wait_for_page(element_id='zip-action-request-data')

        # Anomaly detected
        self.assertIn(
            'Values in column must have format "Participant [number]"',
            self.selenium.page_source)

        # Unselect the Moodle option
        self.selenium.find_element_by_id('id_zip_for_moodle').click()

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Next']").click()
        self.wait_for_page(element_id='zip-action-done')

        # End of session
        self.logout()

class ActionActionDetectAllFalseRows(test.OnTaskLiveTestCase):
    action_name = 'simple action'
    fixtures = ['simple_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_action.sql'
    )

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    action_text = "Cond 1 = {{ cond 1 }}\\n" + \
                  "Cond 2 = {{ cond 2 }}\\n" + \
                  "{% if cond 1 %}Cond 1 is true{% endif %}\\n" + \
                  "{% if cond 2 %}Cond 2 is true{% endif %}\\n"

    def setUp(self):
        super(ActionActionDetectAllFalseRows, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super(ActionActionDetectAllFalseRows, self).tearDown()

    # Test action rename
    def test_action_detect_all_false_rows(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Create a new action
        self.create_new_personalized_text_action("action out", '')

        # Create three conditions
        self.select_condition_tab()
        self.create_condition("cond 1", '', [('another', 'equal', 'bbb')])
        self.create_condition("cond 2", '', [('age', 'greater', '12.1')])

        # The action should now flag that one user has all conditions equal to
        # False
        self.assertIn('user has all conditions equal to FALSE',
                      self.selenium.page_source)

        # insert the action text (not needed, but...)
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', 
            "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.open_browse_preview(1, close=False)

        # The preview should now flag that this user has all conditions equal to
        # False
        self.assertIn('All conditions evaluate to FALSE',
                      self.selenium.page_source)

        # Close the preview
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/div/div[2]/button[2]"
        ).click()
        # Close modal (wail until the modal-open element disappears)
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Create filter
        self.create_filter("The filter", [('another', 'equal', 'bbb')])

        # The action should NOT flag that a user has all conditions equal to
        # False
        self.assertNotIn('user has all conditions equal to FALSE',
                         self.selenium.page_source)

        # Remove the filter
        self.delete_filter()

        # Message show now appear
        # The action should NOT flag that a user has all conditions equal to
        # False
        self.assertIn('user has all conditions equal to FALSE',
                         self.selenium.page_source)

        # End of session
        self.logout()
