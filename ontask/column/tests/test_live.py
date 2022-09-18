"""Test live execution of operations related to columns."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from ontask import models, tests
from ontask.core.checks import check_workflow


class ColumnTestCreateDelete(
    tests.SimpleWorkflowFixture,
    tests.OnTaskLiveTestCase,
):
    """Testing column creation/deletion"""

    def test(self):
        new_cols = [
            ('newc1', 'string', 'male,female', ''),
            ('newc2', 'boolean', '', 'True'),
            ('newc3', 'integer', '', ''),
            ('newc4', 'integer', '0, 10, 20, 30', '0'),
            ('newc5', 'integer', '0, 0.5, 1, 1.5, 2', '0'),
            ('newc6', 'datetime', '', '2017-10-11 00:00:00.000+11:00'),
        ]

        # Login
        self.login('instructor01@bogus.com')

        # Go to the details page
        self.access_workflow_from_home_page(tests.WORKFLOW_NAME)

        # Go to column details
        self.go_to_details()

        # Edit the age column
        self.open_column_edit('age')

        # Untick the is_key option
        is_key = self.selenium.find_element(By.ID, 'id_is_key')
        self.assertTrue(is_key.is_selected())
        is_key.click()
        # Click on the Submit button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='modal-item']/div/div/form/div/button[@type='submit']"
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # First column must be age, number
        self.assert_column_name_type('age', 'Number', 1)

        # ADD COLUMNS
        idx = 5
        for cname, ctype, clist, cinit in new_cols:
            # ADD A NEW COLUMN
            self.add_column(cname, ctype, clist, cinit, idx)
            idx += 1
        check_workflow(models.Workflow.objects.get(id=1))

        # CHECK THAT THE COLUMNS HAVE BEEN CREATED (starting in the sixth)
        idx = 5
        for cname, ctype, _, _ in new_cols:
            if ctype == 'integer' or ctype == 'double':
                ctype = 'Number'
            elif ctype == 'string':
                ctype = 'Text'
            elif ctype == 'boolean':
                ctype = 'True/False'
            elif ctype == 'datetime':
                ctype = 'Date and time'

            self.assert_column_name_type(cname, ctype, idx)
            idx += 1

        # DELETE THE COLUMNS
        for cname, _, _, _ in new_cols:
            self.delete_column(cname)

        # Sixth column must be one string
        self.assert_column_name_type('one', 'Text', 6)

        # End of session
        self.logout()


class ColumnTestRename(tests.SimpleWorkflowFixture, tests.OnTaskLiveTestCase):
    """Testing column rename"""

    def test(self):
        categories = 'aaa, bbb, ccc'
        action_name = 'simple action'
        action_desc = 'action description text'

        # Login
        self.login('instructor01@bogus.com')

        # Open the workflow
        self.access_workflow_from_home_page(tests.WORKFLOW_NAME)

        # Go to the details page
        self.go_to_details()

        # Edit the another column and change the name
        self.open_column_edit('another')

        # Change the name of the column
        self.selenium.find_element(By.ID, 'id_name').send_keys('2')
        # Add list of comma separated categories
        raw_cat = self.selenium.find_element(By.ID, 'id_raw_categories')
        raw_cat.send_keys(categories)

        # Click the rename button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='modal-item']/div/div/form/div/button[@type='submit']"
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # The column must now have name another2
        self.search_table_row_by_string('column-table', 3, 'another2')

        # Goto the action page
        self.go_to_actions()

        # click on the create action out button
        self.create_new_personalized_text_action(action_name, action_desc)

        # Select filter tab
        self.select_filter_tab()
        self.open_condition(
            None,
            "//button[contains(@class, 'js-filter-create')]")
        # Select the another2 column (with new name
        select = Select(self.selenium.find_element(
            By.NAME,
            'builder_rule_0_filter'))
        select.select_by_value('another2')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # There should only be two operands
        filter_ops = self.selenium.find_elements(
            By.XPATH,
            '//select[@name="builder_rule_0_operator"]/option')
        self.assertEqual(len(filter_ops), 4)

        # There should be as many values as in the categories
        filter_vals = self.selenium.find_elements(
            By.XPATH,
            '//select[@name="builder_rule_0_value_0"]/option')
        self.assertEqual(len(filter_vals), len(categories.split(',')))

        # End of session
        self.logout()
