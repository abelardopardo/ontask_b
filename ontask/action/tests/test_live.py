# -*- coding: utf-8 -*-

"""Test live execution of action operations."""
import os

from django.conf import settings
from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ontask import models, tests
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX
from ontask.dataops import formula


class ActionActionEdit(tests.OnTaskLiveTestCase):
    """Test Action Edit."""

    action_name = 'simple action'
    fixtures = ['simple_action']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_action.sql')

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    # Test action rename
    def test_rename(self):
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
        # click on the Update button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('action-table_previous')

        action_element = self.search_action(self.action_name + suffix)
        self.assertTrue(action_element)

        # End of session
        self.logout()

    # Test send_email operation
    def test_send_email(self):
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
            'id_item_column'))
        select.select_by_visible_text('email')

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

        # End of session
        self.logout()

    def test_save_action_with_buttons(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # click on the action page
        self.open_action_edit(self.action_name)

        # insert the first mark
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "mark1");"""
        )

        # Create filter.
        self.select_filter_tab()
        self.create_filter('fdesc', [('age', 'less or equal', '12.1')])

        # Make sure the content has the correct text
        self.assertIn(
            "mark1",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "mark2");"""
        )

        # Modify the filter. Click in the edit filter button
        self.select_filter_tab()
        self.edit_filter(None, '', [])

        # Make sure the content has the correct text
        self.assertIn(
            "mark2",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote('code')"""
            )
        )

        # insert the third mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "mark3");"""
        )

        # Click in the more ops and then the delete filter button
        self.select_filter_tab()
        self.delete_filter()

        self.assertIn(
            "mark3",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote('code')"""
            )
        )
        # insert the first mark
        self.select_text_tab()
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "cmark1");"""
        )

        # Create condition. Click in the add condition button
        self.create_condition('fname',
            'fdesc',
            [('age', 'less or equal', '12.1')])

        self.select_text_tab()
        self.assertIn(
            "cmark1",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote('code')"""
            )
        )

        # insert the second mark
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "cmark2");"""
        )

        # Modify the condition. Click in the condition edit button
        self.edit_condition('fname', 'fname2', '', [])

        # Make sure the content has the correct text
        self.select_text_tab()
        self.assertIn(
            "cmark2",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote("code")"""
            )
        )

        # insert the third mark
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "cmark3");"""
        )

        # Delete the condition
        self.select_condition_tab()
        self.delete_condition('fname2')

        # Make sure the content has the correct text
        self.select_text_tab()
        self.assertIn(
            "cmark3",
            self.selenium.execute_script(
                """return $("#id_text_content").summernote('code')"""
            )
        )

        # End of session
        self.logout()

    # Test operations with the filter
    def test_json_action(self):
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
        self.selenium.find_element_by_id(
            'id_text_content').send_keys(content_txt)
        self.selenium.find_element_by_id('id_target_url').send_keys(target_url)

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_datatable('action-table_previous')

        action = models.Action.objects.get(name=action_name)
        self.assertTrue(action.text_content == content_txt)
        self.assertTrue(action.target_url == target_url)

        # End of session
        self.logout()

    def test_action_url(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        self.open_action_url('simple action', txt='URL Off')

        # Assert the content in the modal
        self.assertIn(
            'This URL provides access to the content personalised',
            self.selenium.page_source)

        # Enable the URL
        self.selenium.find_element_by_id('id_serve_enabled').click()

        # Click OK
        self.selenium.find_element_by_css_selector(
            'div.modal-footer > button.btn.btn-outline-primary'
        ).click()

        # close modal
        self.wait_for_modal_close()

        # Assert that the action has the value changed
        action = models.Action.objects.get(name='simple action')
        self.assertEqual(action.serve_enabled, True)

        self.open_action_url('simple action')
        # Disable the URL
        self.selenium.find_element_by_id('id_serve_enabled').click()
        # Click OK
        self.selenium.find_element_by_css_selector(
            'div.modal-footer > button.btn.btn-outline-primary'
        ).click()

        # close modal
        self.wait_for_modal_close()

        # Assert that the action has the value changed
        action.refresh_from_db()
        self.assertEqual(action.serve_enabled, False)

        # End of session
        self.logout()


class ActionActionInCreate(tests.OnTaskLiveTestCase):
    """Class to test survey creation."""

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow_two_actions.sql')

    wflow_name = 'wflow2'
    wflow_desc = 'Simple workflow structure with two type of actions'
    wflow_empty = 'The workflow does not have data'

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
        self.create_filter('', [('registered', 'equal', 'false')])
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
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Done')
            )
        )
        # Submit the action
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_datatable('action-table_previous')

        # Run the action
        self.open_action_run('new action in', True)

        # Enter data for the remaining user
        self.selenium.find_element_by_link_text("student02@bogus.com").click()
        # Mark as registered
        self.selenium.find_element_by_id(
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '1').click()

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


class ActionActionRenameEffect(tests.OnTaskLiveTestCase):
    """This test case is to check the effect of renaming columns, attributes
       and conditions. These name changes need to propagate throughout various
       elements attached to the workflow
    """

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow_two_actions.sql')

    wflow_name = 'wflow2'

    # Test operations with the filter
    def test_rename_column_condition_attribute(self):
        # First get objects for future checks
        workflow = models.Workflow.objects.get(name=self.wflow_name)
        column = workflow.columns.get(name='registered')
        attributes = workflow.attributes
        models.Action.objects.get(name='Check registration', workflow=workflow)
        action_out = models.Action.objects.get(
            name='Detecting age',
            workflow=workflow
        )
        condition = models.Condition.objects.get(
            name='Registered',
            action=action_out)

        # pre-conditions
        # Column name is the correct one
        self.assertEqual(column.name, 'registered')
        # Condition name is the correct one
        self.assertEqual(condition.name, 'Registered')
        # Attribute name is the correct one
        self.assertEqual(attributes['attribute name'], 'attribute value')
        # Column name is present in condition formula
        self.assertTrue(formula.has_variable(condition.formula, 'registered'))
        # Column name is present in action_out text
        self.assertTrue('{{ registered }}' in action_out.text_content)
        # Attribute name is present in action_out text
        self.assertTrue('{{ attribute name }}' in action_out.text_content)
        # Column name is present in action-in filter
        self.assertTrue(
            formula.has_variable(action_out.get_filter_formula(), 'age'))

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
        workflow = models.Workflow.objects.prefetch_related('columns').get(
            id=workflow.id
        )
        column = workflow.columns.get(id=column.id)
        attributes = workflow.attributes
        action_out = models.Action.objects.get(id=action_out.id)
        condition = models.Condition.objects.get(id=condition.id)
        filter_formula = action_out.get_filter_formula()

        # Post conditions
        # Column name is the correct one
        self.assertEqual(column.name, 'registered new')
        # Condition name is the correct one
        self.assertEqual(condition.name, 'Registered new')
        # Attribute name is the correct one
        self.assertEqual(attributes['attribute name new'],
            'attribute value')
        # Column name is present in condition formula
        self.assertFalse(formula.has_variable(
            condition.formula,
            'registered'))
        self.assertTrue(formula.has_variable(
            condition.formula,
            'registered new'))
        # Column name is present in action_out text
        self.assertTrue('{{ registered new }}' in action_out.text_content)
        # Attribute name is present in action_out text
        self.assertTrue('{{ attribute name new }}' in action_out.text_content)
        # Column age is present in action-in filter
        self.assertFalse(formula.has_variable(filter_formula, 'age'))
        self.assertTrue(formula.has_variable(filter_formula, 'age new'))

        # End of session
        self.logout()


class ActionActionZip(tests.OnTaskLiveTestCase):
    """
    This test case is to check if the ZIP opeation is correct
    """

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow_two_actions.sql')

    wflow_name = 'wflow2'

    def test_action_01_zip(self):
        """Test ZIP action."""
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
            'id_item_column'))
        select.select_by_visible_text('age')

        # Set column 2
        select = Select(self.selenium.find_element_by_id(
            'id_user_fname_column'))
        select.select_by_visible_text('age')

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Send']").click()
        self.wait_for_page(element_id='zip-action-request-data')

        # Anomaly detected
        self.assertIn('The two columns must be different',
            self.selenium.page_source)

        # Set column 2
        select = Select(self.selenium.find_element_by_id(
            'id_user_fname_column'))
        select.select_by_visible_text('email')

        # Choose the Moodle option
        self.selenium.find_element_by_id('id_zip_for_moodle').click()

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Send']").click()
        self.wait_for_page(element_id='zip-action-request-data')

        # Anomaly detected
        self.assertIn(
            'Values in column must have format "Participant [number]"',
            self.selenium.page_source)

        # Unselect the Moodle option
        self.selenium.find_element_by_id('id_zip_for_moodle').click()

        # Click the next
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Send']").click()
        self.wait_for_page(element_id='zip-action-done')

        # End of session
        self.logout()


class ActionAllKeyColumns(tests.OnTaskLiveTestCase):
    """Test the case of all key columns in a workflow."""

    action_name = 'Test1'
    fixtures = ['all_key_columns']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'all_key_columns.sql')

    wflow_name = 'all key columns'

    # Test action rename
    def test_action_insert_column_value(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Click in the page to send email
        self.open_action_edit(self.action_name)

        # There should be four elements (all key column) in the drop-down
        self.assertEqual(
            len(self.selenium.find_elements_by_xpath(
                '//div[@id="column-selector"]/div/button')),
            4)

        # End of session
        self.logout()


class ActionSendListActionCreate(tests.OnTaskLiveTestCase):
    """Test sending a list of values."""

    fixtures = ['simple_action']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_action.sql')

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'

    action_name = 'Send to someone'
    action_text = 'Dear sir/madam\\nHere is the student list: '

    def test_email_report_create_edit(self):
        """Send list action after creating and editing."""
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        self.create_new_email_report_action(self.action_name, '')

        # insert the action text
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "note-editable")]')
            )
        )
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText',
             "{0}");""".format(self.action_text)
        )

        # Open the column selection and select two columns
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Insert Table']").click()
        self.wait_for_modal_open()
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[3]"
        ).click()
        # self.selenium.find_element_by_css_selector("div.modal-body").click()
        # Close the modal
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[normalize-space()='Select']"
        ).click()
        self.wait_for_modal_close()

        # Create filter
        self.create_filter("The filter", [('another', 'equal', 'bbb')])

        # There should be 2 of three learners selected
        self.assertIn('2 learners of 3', self.selenium.page_source)

        # Click in the preview
        self.open_browse_preview(close=False)

        self.assertIn('student01@bogus.com', self.selenium.page_source)
        self.assertIn('student03@bogus.com', self.selenium.page_source)

        # Close the preview
        self.cancel_modal()

        self.selenium.find_element_by_xpath(
            '//div[@id="action-preview-done"]/button[3]').click()
        self.wait_for_datatable('action-table_previous')

        # Run the action
        self.open_action_run(self.action_name)

        self.selenium.find_element_by_id('id_email_to').send_keys(
            'recipient@bogus.com')
        self.selenium.find_element_by_id('id_subject').send_keys(
            'Send Report Email Subject')
        self.selenium.find_element_by_id('id_cc_email').send_keys(
            'tutor1@example.com tutor2@example.com')
        self.selenium.find_element_by_id('id_bcc_email').send_keys(
            'coursecoordinator@bogus.com')
        # Click in the next button to go to the filter email screen
        self.selenium.find_element_by_xpath(
            '//button[@name="Submit"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//body/div/h1'),
                'Action scheduled for execution')
        )

        # Check that the email has been properly stored
        assert len(mail.outbox) == 1
        assert('student01@bogus.com' in mail.outbox[0].body)
        assert('student03@bogus.com' in mail.outbox[0].body)

        # End of session
        self.logout()


class ActionJSONReportActionCreate(tests.OnTaskLiveTestCase):
    """Test the JSON Report action."""

    fixtures = ['simple_action']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple_action.sql')

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'

    action_name = 'JSON REPORT'
    action_text = '{ "student_list": {% ot_insert_column_list "email" %} }'

    def test_json_report_create_edit(self):
        """Create and edit a list action."""
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        self.create_new_JSON_report_action(self.action_name, '')

        # insert the action text
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'id_text_content'))
        )
        self.selenium.find_element_by_id('id_text_content').send_keys(
            self.action_text)

        # Create filter
        self.create_filter("The filter", [('another', 'equal', 'bbb')])

        # There should be 2 of three learners selected
        self.assertIn('2 learners of 3', self.selenium.page_source)

        # Click in the preview
        self.open_browse_preview(close=False)

        self.assertIn(
            '"student01@bogus.com", "student03@bogus.com"',
            self.selenium.page_source)

        # Close the preview
        self.cancel_modal()

        self.selenium.find_element_by_xpath(
            '//div[@id="action-preview-done"]/button[3]').click()
        self.wait_for_datatable('action-table_previous')

        # Run the action
        self.open_action_run(self.action_name)

        self.selenium.find_element_by_id('id_token').send_keys(
            'bogus_token')
        # Click in the submit
        self.selenium.find_element_by_xpath(
            '//button[@name="Submit"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//body/div/h1'),
                'Action scheduled for execution')
        )

        # End of session
        self.logout()


class ActionServeLongSurvey(tests.OnTaskLiveTestCase):
    """Test the view to serve a survey."""
    fixtures = ['long_survey']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'long_survey.sql')

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'Test survey run pages'
    action_name = 'survey'

    def test_serve_long_survey(self):
        """Test the serve_action view with a long number of entries."""
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.workflow_name)

        # Goto the action page
        self.go_to_actions()

        # Open action name
        self.open_action_run(self.action_name, is_action_in=True)

        pages = self.selenium.find_elements_by_xpath(
            '//li[contains(@class, "paginate_button")]')
        self.assertEqual(len(pages), 4)

        self.logout()


class ActionCreateRubric(tests.OnTaskLiveTestCase):
    """Test the view to serve a survey."""
    fixtures = ['test_rubric']
    filename = os.path.join(settings.ONTASK_FIXTURE_DIR, 'test_rubric.sql')

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'test rubric'
    action_name = 'survey'

    def test_create_rubric_action(self):
        """Test the creation of a rubric action."""
        # Login
        self.login('instructor01@bogus.com')

        workflow = models.Workflow.objects.get(name=self.workflow_name)
        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.workflow_name)

        # Create new action
        self.create_new_rubric_action(self.action_name)

        # insert the text
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "note-editable")]')
            )
        )
        self.selenium.find_element_by_class_name('note-editable').click()
        self.selenium.find_element_by_class_name('note-editable').send_keys(
            'Dear {{ GivenName }}\n'
            + 'Here are some suggestions based on the project rubric.\n'
            + '{% ot_insert_rubric_feedback %}\n'
            + 'Regards\n'
            + 'Chris Doe\n'
            + 'Course Coordinator')

        self.select_rubric_tab()
        self.click_dropdown_option(
            '//div[@id="insert-criterion"]',
            'Structure')
        self.wait_for_datatable('rubric-table_previous')

        # Insert an extra criterion
        self.selenium.find_element_by_class_name(
            'js-workflow-criterion-add').click()
        self.wait_for_modal_open()
        self.selenium.find_element_by_id('id_name').send_keys('CRIT 2')
        element = self.selenium.find_element_by_id('id_description_text')
        element.click()
        element.clear()
        element.send_keys('CRIT 2 description text')
        # click on the Add criterion
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[@type="submit"]'
        ).click()
        self.wait_for_modal_close()
        self.wait_for_datatable('rubric-table_previous')

        column = models.Column.objects.get(name='Structure')
        loas = column.categories[:]
        for index in range(2 * len(column.categories)):
            items = self.selenium.find_elements_by_class_name(
                'js-rubric-cell-edit')
            items[index].click()
            self.wait_for_modal_open()
            self.selenium.find_element_by_id('id_description_text').send_keys(
                'DESC {0}'.format(index))
            self.selenium.find_element_by_id('id_feedback_text').send_keys(
                'FEEDBACK {0}'.format(index))
            # click on the DONE button
            self.selenium.find_element_by_xpath(
                '//div[@id="modal-item"]//button[@type="submit"]'
            ).click()
            self.wait_for_modal_close()
            self.wait_for_datatable('rubric-table_previous')

        # Loop over the number of rows
        self.open_browse_preview(workflow.nrows)

        # Change the LOAS
        self.selenium.find_element_by_class_name('js-rubric-loas-edit').click()
        self.wait_for_modal_open()
        elem = self.selenium.find_element_by_id('id_levels_of_attainment')
        elem.clear()
        elem.send_keys(', '.join([loa + '2' for loa in loas]))
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[@type="submit"]'
        ).click()
        self.wait_for_modal_close()
        self.wait_for_datatable('rubric-table_previous')

        # Close the action and back to table of actions
        self.selenium.find_element_by_xpath(
            '//div[@id="action-preview-done"]/button[3]').click()
        self.wait_for_datatable('action-table_previous')

        # Assertions
        action = workflow.actions.get(name=self.action_name)
        self.assertEqual(action.column_condition_pair.count(), 2)
        self.assertEqual(action.rubric_cells.count(), 6)
        for idx, rubric_cell in enumerate(action.rubric_cells.all()):
            self.assertEqual(
                rubric_cell.description_text,
                'DESC {0}'.format(idx))
            self.assertEqual(
                rubric_cell.feedback_text,
                'FEEDBACK {0}'.format(idx))

        column.refresh_from_db()
        self.assertEqual(column.categories, [loa + '2' for loa in loas])
