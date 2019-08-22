# -*- coding: utf-8 -*-

import os
import test

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ontask.dataops.pandas import db
from ontask.models import Workflow


class WorkflowInitial(test.OnTaskLiveTestCase):
    def setUp(self):
        super().setUp()
        test.create_users()

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_workflow_create_upload_merge_column_edit(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Create the workflow
        self.create_new_workflow(test.wflow_name, test.wflow_desc)

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//table[@id='dataops-table']//a[normalize-space()='CSV']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

        # Set the file name
        self.selenium.find_element_by_id('id_data_file').send_keys(
            os.path.join(
                settings.BASE_DIR(),
                'ontask',
                'fixtures',
                'simple.csv')
        )

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
                'Select Columns')
        )

        # Change the name of one of the columns
        input_email = self.selenium.find_element_by_xpath(
            "//table[@id='workflow-table']/tbody/tr[3]/td[3]/input"
        )
        input_email.clear()
        input_email.send_keys('email')

        # Click on the FINISH button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()

        # Wait for detail table
        self.wait_for_datatable('table-data_previous')

        # Go to column details
        self.go_to_details()

        # First column must be: age, double
        self.assert_column_name_type('sid', 'Number', 1)

        # Second column must be email string
        self.assert_column_name_type('name', 'Text', 2)

        # Third column must be sid integer
        self.assert_column_name_type('email', 'Text', 3)

        # Fourth column must be name string
        self.assert_column_name_type('age', 'Number', 4)

        # Fifth registered and boolean
        self.assert_column_name_type('registered', 'True/False', 5)

        # Sixth when and datetime
        self.assert_column_name_type('when', 'Date and time', 6)

        # Go to CSV Upload/Merge Step 1
        self.go_to_csv_upload_merge_step_1()

        # Set the file name
        self.selenium.find_element_by_id('id_data_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                'ontask',
                'fixtures',
                'simple2.csv')
        )

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
                'Select Columns')
        )

        # Change the name of sid2 to sid
        input_email = self.selenium.find_element_by_xpath(
            "//table[@id='workflow-table']/tbody/tr[3]/td[3]/input"
        )
        input_email.clear()
        input_email.send_keys('sid')

        # Click on the Next button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"), 'Select Keys and Merge Option')
        )

        # Select SID in the first key
        self.selenium.find_element_by_id('id_dst_key').send_keys('sid')
        # Select SID in the first key
        self.selenium.find_element_by_id('id_src_key').send_keys('sid')

        # Select the merger function type
        select = Select(self.selenium.find_element_by_id(
            'id_how_merge'))
        select.select_by_value('outer')

        # Click on the Next button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"), 'Review and confirm')
        )

        # Click on the FINISH button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        # Wait for the upload/merge to finish
        self.wait_for_datatable('table-data_previous')

        # Go to column details
        self.go_to_details()

        # Seventh column must be: another, string
        self.assert_column_name_type('one', 'Text')

        # Eight column must be one string
        self.assert_column_name_type('another', 'Text')

        # End of session
        self.logout()

        # Close the db_engine
        db.destroy_db_engine(db.engine)

    def test_02_workflow_create_upload_with_prelude(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Create the workflow
        self.create_new_workflow(test.wflow_name, test.wflow_desc)

        # Go to the CSV upload step 1
        self.selenium.find_element_by_xpath(
            "//table[@id='dataops-table']//a[normalize-space()='CSV']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

        # Set the file name
        self.selenium.find_element_by_id('id_data_file').send_keys(
            os.path.join(
                settings.BASE_DIR(),
                'ontask',
                'fixtures',
                'csv_with_prelude_postlude.csv'),
        )
        # Set the prelude to 6 lines and postlude to 3
        self.selenium.find_element_by_id('id_skip_lines_at_top').clear()
        self.selenium.find_element_by_id('id_skip_lines_at_top').send_keys('6')
        self.selenium.find_element_by_id('id_skip_lines_at_bottom').clear()
        self.selenium.find_element_by_id(
            'id_skip_lines_at_bottom'
        ).send_keys('3')

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
                'Select Columns')
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Click on the FINISH button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()

        # Wait for the details table
        self.wait_for_datatable('table-data_previous')

        # Check that the number of rows is the correct one in the only
        # workflow available
        wf = Workflow.objects.all()[0]
        self.assertEqual(wf.nrows, 3)
        self.assertEqual(wf.ncols, 6)

        # End of session
        self.logout()


class WorkflowModify(test.OnTaskLiveTestCase):
    fixtures = ['simple_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow.sql'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_02_workflow_column_create_delete(self):
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
        self.access_workflow_from_home_page(test.wflow_name)

        # Go to column details
        self.go_to_details()

        # Edit the age column
        self.open_column_edit('age')

        # Untick the is_key option
        is_key = self.selenium.find_element_by_id('id_is_key')
        self.assertTrue(is_key.is_selected())
        is_key.click()
        # Click on the Submit button
        self.selenium.find_element_by_xpath(
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
            db.check_wf_df(Workflow.objects.get(id=1))
            idx += 1

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

    def test_03_workflow_column_rename(self):
        categories = 'aaa, bbb, ccc'
        action_name = 'simple action'
        action_desc = 'action description text'

        # Login
        self.login('instructor01@bogus.com')

        # Open the workflow
        self.access_workflow_from_home_page(test.wflow_name)

        # Go to the details page
        self.go_to_details()

        # Edit the another column and change the name
        self.open_column_edit('another')

        # Change the name of the column
        self.selenium.find_element_by_id('id_name').send_keys('2')
        # Add list of comma separated categories
        raw_cat = self.selenium.find_element_by_id(
            'id_raw_categories'
        )
        raw_cat.send_keys(categories)

        # Click the rename button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/form/div/button[@type='submit']"
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # The column must now have name another2
        self.search_table_row_by_string('column-table', 2, 'another2')

        # Goto the action page
        self.go_to_actions()

        # click in the create action out button
        self.create_new_personalized_text_action(action_name, action_desc)

        # Select filter tab
        self.select_filter_tab()
        self.open_condition(None,
            "//button[contains(@class, 'js-filter-create')]")
        # Select the another2 column (with new name
        select = Select(self.selenium.find_element_by_name(
            'builder_rule_0_filter'))
        select.select_by_value('another2')
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@name='builder_rule_0_filter']")
            )
        )

        # There should only be two operands
        filter_ops = self.selenium.find_elements_by_xpath(
            "//select[@name='builder_rule_0_operator']/option"
        )
        self.assertEqual(len(filter_ops), 4)

        # There should be as many values as in the categories
        filter_vals = self.selenium.find_elements_by_xpath(
            "//select[@name='builder_rule_0_value_0']/option"
        )
        self.assertEqual(len(filter_vals), len(categories.split(',')))

        # End of session
        self.logout()


class WorkflowAttribute(test.OnTaskLiveTestCase):
    fixtures = ['simple_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow.sql'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_workflow_attributes(self):
        pass

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(test.wflow_name)

        # Click on the more-ops and then attributes button
        self.go_to_attribute_page()

        # Attributes are initially empty
        self.assertIn('Attributes are pairs', self.selenium.page_source)

        # Create key1, value1
        self.create_attribute('key1', 'value1')

        # Values now should be in the table
        self.search_table_row_by_string('attribute-table', 1, 'key1')
        self.search_table_row_by_string('attribute-table', 2, 'value1')

        # Create key2, value2
        self.create_attribute('key2', 'value2')
        self.search_table_row_by_string('attribute-table', 1, 'key2')
        self.search_table_row_by_string('attribute-table', 2, 'value2')

        # Rename second attribute
        self.selenium.find_element_by_xpath(
            "//tr/td[1][normalize-space() = 'key2']"
        ).click()
        self.wait_for_modal_open()
        self.selenium.find_element_by_id('id_key').clear()
        self.selenium.find_element_by_id('id_key').send_keys('newkey2')
        self.selenium.find_element_by_id('id_attr_value').clear()
        self.selenium.find_element_by_id(
            'id_attr_value').send_keys('newvalue2')

        # Click in the submit button
        self.selenium.find_element_by_xpath(
            "//div[@id = 'modal-item']//div[@class='modal-footer']/button"
        ).click()

        # Go back to the attribute table page
        self.wait_close_modal_refresh_table('attribute-table_previous')

        # Check that the attributes are properly stored in the workflow
        workflow = Workflow.objects.all()[0]
        self.assertEqual(len(workflow.attributes), 2)
        self.assertEqual(workflow.attributes['key1'], 'value1')
        self.assertEqual(workflow.attributes['newkey2'], 'newvalue2')

        # Go back to the attribute page
        self.go_to_attribute_page()

        # click the delete button in the second row
        self.selenium.find_element_by_xpath(
            '//table[@id="attribute-table"]'
            '//tr[2]/td[3]//button[contains(@class, "js-attribute-delete")]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@id="modal-item"]//div[@class="modal-footer"]/button')),
        )
        # Click in the delete confirm button
        self.selenium.find_element_by_xpath(
            '//div[@id = "modal-item"]//div[@class = "modal-footer"]/button'
        ).click()
        # MODAL WAITING
        self.wait_for_page(element_id='workflow-detail')
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-attribute-create')
            )
        )

        # There should only be a single element
        self.assertEqual(
            len(self.selenium.find_elements_by_xpath(
                '//table[@id="attribute-table"]/tbody/tr'
            )),
            1
        )
        # Check that the attributes are properly stored in the workflow
        workflow = Workflow.objects.all()[0]
        self.assertEqual(len(workflow.attributes), 1)
        self.assertEqual(workflow.attributes['key1'], 'value1')

        # End of session
        self.logout()


class WorkflowShare(test.OnTaskLiveTestCase):
    fixtures = ['simple_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow.sql'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_workflow_share(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(test.wflow_name)

        # Click on the share
        self.go_to_workflow_share()

        # Click in the add user button
        self.selenium.find_element_by_class_name('js-share-create').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'),
                'Select user to allow access to the workflow'))

        # Fill out the form
        self.selenium.find_element_by_id('id_user_email').send_keys(
            'instructor02@bogus.com')

        # Click in the share button
        self.selenium.find_element_by_xpath(
            "//div[@id = 'modal-item']//div[@class = 'modal-footer']/button"
        ).click()

        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for the  page to reload.
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-share-create'))
        )

        # Value now should be in the table
        self.select_share_tab()
        self.search_table_row_by_string('share-table',
            1,
            'instructor02@bogus.com')

        # Click in the create share dialog again
        self.selenium.find_element_by_class_name('js-share-create').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'),
                'Select user to allow access to the workflow'))

        # Fill out the form
        self.selenium.find_element_by_id('id_user_email').send_keys(
            'superuser@bogus.com')

        # Click in the button to add the user
        self.selenium.find_element_by_xpath(
            "//div[@id = 'modal-item']//div[@class = 'modal-footer']/button"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Wait for the  page to reload.
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-share-create'))
        )

        # Value now should be in the table
        self.select_share_tab()
        self.search_table_row_by_string('share-table',
            1,
            'instructor02@bogus.com')

        # Check that the shared users are properly stored in the workflow
        workflow = Workflow.objects.all()[0]
        self.assertEqual(workflow.shared.count(), 2)
        users = workflow.shared.values_list('email', flat=True)
        self.assertTrue('instructor02@bogus.com' in users)
        self.assertTrue('superuser@bogus.com' in users)

        # click the delete button in the superuser@bogus.com row
        element = self.search_table_row_by_string('share-table',
            1,
            'superuser@bogus.com')
        element.find_element_by_xpath('td[2]/button').click()

        # Wait for the delete confirmation frame
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'modal-title'),
                'Confirm user deletion')
        )
        # Click in the delete confirm button
        self.selenium.find_element_by_xpath(
            "//div[@id = 'modal-item']//div[@class = 'modal-footer']/button"
        ).click()

        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # There should only be a single element
        self.select_share_tab()
        self.assertEqual(
            len(self.selenium.find_elements_by_xpath(
                "//table[@id='share-table']/tbody/tr"
            )),
            1
        )
        # Check that the shared users are properly stored in the workflow
        workflow = Workflow.objects.all()[0]
        self.assertEqual(workflow.shared.count(), 1)
        users = workflow.shared.values_list('email', flat=True)
        self.assertTrue('instructor02@bogus.com' in users)

        # End of session
        self.logout()
