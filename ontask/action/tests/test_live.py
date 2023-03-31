# -*- coding: utf-8 -*-

"""Test live execution of action operations."""
from time import sleep

from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ontask import models, tests
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX
from ontask.dataops import formula


class ActionActionRename(tests.SimpleActionFixture, tests.OnTaskLiveTestCase):
    """Test Action Rename."""

    action_name = 'simple action'

    # Test action rename
    def test(self):
        suffix = ' 2'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click on the action rename link
        self.open_action_operation(self.action_name, 'fa-pencil-alt')

        # Rename the action
        self.selenium.find_element_by_id('id_name').send_keys(suffix)
        # click on the Update button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('action-index')

        action_element = self.search_action(self.action_name + suffix)
        self.assertTrue(action_element)

        # End of session
        self.logout()


class ActionActionSendEmail(
    tests.SimpleActionFixture,
    tests.OnTaskLiveTestCase
):
    """Test Action Edit."""

    action_name = 'simple action'

    # Test send_email operation
    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click in the page to send email
        self.open_action_run(self.action_name)
        self.wait_for_id_and_spinner('email-action-request-data')

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


class ActionActionSave(tests.SimpleActionFixture, tests.OnTaskLiveTestCase):
    """Test Action Edit."""

    action_name = 'simple action'

    def test(self):
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
        self.create_condition(
            'fname',
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


class ActionJsonAction(tests.SimpleActionFixture, tests.OnTaskLiveTestCase):
    """Test Action Edit."""

    action_name = 'simple action'

    # Test operations with the filter
    def test(self):
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
        self.wait_for_id_and_spinner('action-index')

        action = models.Action.objects.get(name=action_name)
        self.assertTrue(action.text_content == content_txt)
        self.assertTrue(action.target_url == target_url)

        # End of session
        self.logout()


class ActionActionURL(tests.SimpleActionFixture, tests.OnTaskLiveTestCase):
    """Test Action Edit."""

    action_name = 'simple action'

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        self.open_action_operation('simple action', 'fa-link')

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

        self.open_action_operation('simple action', 'fa-link')
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


class ActionActionInDataEntry(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskLiveTestCase,
):
    """Class to test survey creation."""

    # Test operations with the filter
    def test(self):
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
        self.click_dropdown_option('select-key-column-name', 'email')
        # Table disappears (page is updating) -- Wait for spinner, and then
        # refresh
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        self.select_questions_tab()
        self.click_dropdown_option('column-selector', 'registered')
        self.wait_for_id_and_spinner('column-selected-table_previous')
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Done')
            )
        )
        # Submit the action
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_id_and_spinner('action-index')

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


class ActionActionRenameEffect(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskLiveTestCase,
):
    """Renaming columns.

    This test case is to check the effect of renaming columns, attributes and
    conditions. These name changes need to propagate throughout various
    elements attached to the workflow
    """

    # Test operations with the filter
    def test(self):
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
        self.edit_attribute(
            'attribute name',
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
        self.assertEqual(
            attributes['attribute name new'],
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


class ActionActionZip(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskLiveTestCase,
):
    """
    This test case is to check if the ZIP opeation is correct
    """

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Click in the page to send email
        self.open_action_operation(
            'Detecting age',
            'fa-file-archive',
            'zip-action-request-data')

        # The zip should include 2 files
        self.assertIn(
            'A ZIP with 2 files will be created',
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
        self.assertIn(
            'The two columns must be different',
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


class ActionAllKeyColumns(tests.AllKeyColumnsFixture, tests.OnTaskLiveTestCase):
    """Test the case of all key columns in a workflow."""

    action_name = 'Test1'

    # Test action rename
    def test(self):
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


class ActionSendReportActionCreate(
    tests.SimpleActionFixture,
    tests.OnTaskLiveTestCase,
):
    """Test sending a list of values."""

    action_name = 'Send to someone'
    action_text = 'Dear sir/madam\\nHere is the student list: '

    def test(self):
        workflow = models.Workflow.objects.get(name=self.wflow_name)
        view = workflow.views.all().first()

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
        # Close the modal
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[normalize-space()='Select']"
        ).click()
        self.wait_for_modal_close()

        # Create filter
        self.create_filter("The filter", [('another', 'equal', 'bbb')])

        # There should be 2 of three learners selected
        self.assertIn('2 learners of 3', self.selenium.page_source)

        # Add attachment
        self.create_attachment(view.name)

        # Click in the preview
        self.open_browse_preview(close=False)

        preview_body = self.selenium.find_element_by_id('preview-body').text
        self.assertIn('student01@bogus.com', preview_body)
        self.assertIn('student03@bogus.com', preview_body)
        self.assertEqual(
            self.selenium.find_element_by_xpath(
                '//*[@id="preview-variables"]').text,
            'Attachments: ' + view.name)

        # Close the preview
        self.cancel_modal()

        self.selenium.find_element_by_xpath(
            '//div[@id="action-preview-done"]/button[3]').click()
        self.wait_for_id_and_spinner('action-index')

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

        # Check that the email has the correct elements
        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert ('student01@bogus.com' in msg.body)
        assert ('student02@bogus.com' not in msg.body)
        assert ('student03@bogus.com' in msg.body)
        assert len(msg.attachments) == 1
        attachment = msg.attachments[0]
        assert attachment.get_content_type() == 'text/csv'
        assert attachment.get_content_disposition() == 'attachment'
        assert attachment.get_filename() == view.name + '.csv'

        # End of session
        self.logout()


class ActionJSONReportActionCreate(
    tests.SimpleActionFixture,
    tests.OnTaskLiveTestCase,
):
    """Test the JSON Report action."""

    action_name = 'JSON REPORT'
    action_text = '{ "student_list": {% ot_insert_report "email" %} }'

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        self.create_new_JSON_report_action(self.action_name, '')

        # insert the action text
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
        self.wait_for_id_and_spinner('action-index')

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


class ActionServeLongSurvey(tests.LongSurveyFixture, tests.OnTaskLiveTestCase):
    """Test the view to serve a survey."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'
    action_name = 'survey'

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Open action name
        self.open_action_run(self.action_name, is_action_in=True)

        pages = self.selenium.find_elements_by_xpath(
            '//li[contains(@class, "paginate_button")]')
        self.assertEqual(len(pages), 4)

        self.logout()


class ActionCreateRubric(tests.TestRubricFixture, tests.OnTaskLiveTestCase):
    """Test the view to serve a survey."""
    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'
    action_name = 'survey'

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        workflow = models.Workflow.objects.get(name=self.wflow_name)
        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

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
        self.click_dropdown_option('insert-criterion', 'Structure')
        self.wait_for_id_and_spinner('rubric-table_previous')

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
        self.wait_for_id_and_spinner('rubric-table_previous')

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
            self.wait_for_id_and_spinner('rubric-table_previous')

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
        self.wait_for_id_and_spinner('rubric-table_previous')

        # Close the action and back to table of actions
        self.selenium.find_element_by_xpath(
            '//div[@id="action-preview-done"]/button[3]').click()
        self.wait_for_id_and_spinner('action-index')

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


class ActionIndexSelector(
    tests.InitialWorkflowFixture,
    tests.OnTaskLiveTestCase,
):
    """Test the action selector in the main action page."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        self.login('instructor01@bogus.com')
        workflow = models.Workflow.objects.get(name=self.wflow_name)

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Loop over all the action types
        select = Select(
            self.selenium.find_element_by_id('action-show-display'))
        for atype in models.Action.AVAILABLE_ACTION_TYPES.keys():
            select.select_by_value(atype)
            sleep(0.5)
            self.assertEqual(
                workflow.actions.filter(action_type=atype).count(),
                len(self.selenium.find_elements_by_xpath(
                    '//*[@id="action-cards"]/'
                    'div[not(contains(@style,"display: none"))]')))

        # Select all of them
        select.select_by_value('')
        self.assertEqual(
            workflow.actions.count(),
            len(self.selenium.find_elements_by_xpath(
                '//*[@id="action-cards"]/'
                'div[not(contains(@style,"display: none"))]')))

        # End of session
        self.logout()
