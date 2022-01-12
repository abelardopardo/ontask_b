# -*- coding: utf-8 -*-

"""Test live execution of action operations."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ontask import tests
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX


class ConditionTestBasic(tests.SimpleActionFixture, tests.OnTaskLiveTestCase):
    """Test Filter/Condition Edit."""

    action_name = 'simple action'


class FilterLiveTest(ConditionTestBasic):
    """Test Filter Edit."""

    # Test operations with the filter
    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # click on EDIT action link
        self.open_action_edit(self.action_name)

        # Click in the add filter button
        self.select_filter_tab()
        self.selenium.find_element(By.CLASS_NAME, 'js-filter-create').click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )

        # Add the description
        self.selenium.find_element(
            By.ID, 'id_description_text').send_keys('fdesc')

        # Select the age filter
        sel = Select(self.selenium.find_element(
            By.NAME,
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
        sel = Select(self.selenium.find_element(
            By.NAME,
            'builder_rule_0_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 12.1
        self.selenium.find_element(
            By.NAME,
            'builder_rule_0_value_0').send_keys('12.1')

        # Click in the "update filter"
        self.selenium.find_element(
            By.XPATH,
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
        self.wait_for_spinner()

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('2 learners of 3', self.selenium.page_source)

        # Add a second clause to the filter
        # Click in the edit filter button
        self.selenium.find_element(By.CLASS_NAME, 'js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )

        # Click in the Add rule of the filter builder button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='builder_group_0']/div/div/button[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='builder_group_0']/div/div/button[1]")
            )
        )

        # Select the when filter
        sel = Select(self.selenium.find_element(
            By.NAME,
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
        sel = Select(self.selenium.find_element(
            By.NAME,
            'builder_rule_1_operator'))
        sel.select_by_value('less_or_equal')

        # Set the value to 2017-10-11T00:32:44
        self.selenium.find_element(
            By.NAME,
            'builder_rule_1_value_0').send_keys(
            '2017-10-11 00:32:44+1300')

        # Click in the "update filter"
        self.selenium.find_element(
            By.XPATH,
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
        self.wait_for_spinner()

        # Check that the filter is selecting 2 out of 3 rows
        self.assertIn('1 learner of 3', self.selenium.page_source)

        # End of session
        self.logout()


class ConditionLiveTest(ConditionTestBasic):
    """Test Condition Edit."""

    # Test operations with the conditions and the email preview
    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open workflow page
        self.access_workflow_from_home_page(self.wflow_name)

        # Edit the action
        self.open_action_edit(self.action_name)

        # Add condition
        self.select_condition_tab()
        self.create_condition(
            'c1',
            'cdesc1',
            [('age', 'less or equal', '12.1')])

        # Click in the add a second condition
        self.select_condition_tab()
        self.create_condition(
            'c2',
            'cdesc2',
            [('age', 'greater', '12.1')])

        # Action now has two complementary conditions, add the conditions to
        # the message
        self.select_text_tab()
        self.selenium.find_element(By.CLASS_NAME, 'note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote(
                   'editor.insertText',
                   "{% if c1 %}Low{% endif %}{% if c2 %}High{% endif %}")""")

        # Click the preview button
        self.open_browse_preview(close=False)

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element(
            By.CLASS_NAME,
            'js-action-preview-nxt').click()

        self.wait_for_modal_open(
            "//div[@id='modal-item']//div[@id='preview-body']"
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-action-preview-nxt')
            )
        )

        # First value should be high age
        self.assertIn('Low', self.selenium.page_source)

        # Click in the next button
        self.selenium.find_element(
            By.CLASS_NAME,
            'js-action-preview-nxt').click()

        self.wait_for_modal_open(
            "//div[@id='modal-item']//div[@id='preview-body']"
        )

        # First value should be high age
        self.assertIn('High', self.selenium.page_source)

        # Close the preview
        self.cancel_modal()

        # End of session
        self.logout()


class ConditionDetectAllFalseRows(ConditionTestBasic):
    """Test the detection of all false rows."""

    action_text = "Cond 1 = {{ cond 1 }}\\n" + \
                  "Cond 2 = {{ cond 2 }}\\n" + \
                  "{% if cond 1 %}Cond 1 is true{% endif %}\\n" + \
                  "{% if cond 2 %}Cond 2 is true{% endif %}\\n"

    def test(self):
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
        self.assertIn(
            'user has all conditions equal to FALSE',
            self.selenium.page_source)

        # insert the action text (not needed, but...)
        self.select_text_tab()
        self.selenium.find_element(By.CLASS_NAME, 'note-editable').click()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText',
            "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.open_browse_preview(1, close=False)

        # The preview should now flag that this user has all conditions equal
        # to False
        self.assertIn(
            'All conditions evaluate to FALSE',
            self.selenium.page_source)

        # Close the preview
        self.cancel_modal()

        # Create filter
        self.create_filter("The filter", [('another', 'equal', 'bbb')])

        # The action should NOT flag that a user has all conditions equal to
        # False
        self.assertNotIn(
            'user has all conditions equal to FALSE',
            self.selenium.page_source)

        # Remove the filter
        self.delete_filter()

        # Message show now appear
        # The action should NOT flag that a user has all conditions equal to
        # False
        self.assertIn(
            'user has all conditions equal to FALSE',
            self.selenium.page_source)

        # End of session
        self.logout()


class ConditionInActionIn(
    tests.TestPersonalisedSurveyFixture,
    tests.OnTaskLiveTestCase,
):
    """Class to test survey with conditions controlling questions."""

    def test(self):
        action_name = 'Survey'
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Goto the action page
        self.go_to_actions()

        # Open action in
        self.open_action_edit(action_name)

        # Select the condition tab
        self.select_condition_tab()

        # Create two conditions
        self.create_condition(
            'Text 1 is null', '',
            [('text1', 'is null', None)])
        self.create_condition(
            'Text 2 is null', '',
            [('text2', 'is null', None)])

        # Go back to the questions
        self.select_questions_tab()

        # Select conditions to both questions
        self.select_questions_condition('text1', 'Text 1 is null')
        self.select_questions_condition('text2', 'Text 2 is null')

        # Click the preview button
        self.open_preview()

        # Check there is a single field and click on next
        for __ in range(8):
            # There should be a single form field in the preview
            inputs = self.selenium.find_elements_by_xpath(
                "//div[@class='js-action-preview-form']//input"
            )
            self.assertEqual(len(inputs), 1)

            # Click in the next button
            self.selenium.find_element(
                By.CLASS_NAME,
                'js-action-preview-nxt').click()

            WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'js-action-preview-nxt')
                )
            )

        # Close the modal
        self.cancel_modal()

        # Done. Back to the table of actions
        self.selenium.find_element(By.LINK_TEXT, 'Done').click()
        self.wait_for_id_and_spinner('action-index')

        # Run the action
        self.open_action_run(action_name, True)

        # Click in the first element of the survey and wait for form
        self.selenium.find_element(By.LINK_TEXT, '1.0').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '2')
            )
        )

        # There should be only three fields here (csrf, key, field)
        inputs = self.selenium.find_elements_by_xpath(
            "//div[@id='action-row-datainput']//input"
        )
        self.assertEqual(len(inputs), 3)

        # Enter text in the third field
        inputs[2].clear()
        inputs[2].send_keys('text')

        # Click in the update button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='action-row-datainput']//form//button[@type = 'submit']"
        ).click()
        self.wait_for_id_and_spinner('actioninrun-data_previous')

        # Click in the same link
        self.selenium.find_element(By.LINK_TEXT, '1.0').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'action-row-datainput')
            )
        )

        # There should be a "No responses required message"
        self.assertIn(
            'No responses required at this time',
            self.selenium.page_source)

        # End of session
        self.logout()
