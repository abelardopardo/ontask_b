# -*- coding: utf-8 -*-

"""Test live execution of operations related to workflows."""
import os

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from ontask import models, tests
from ontask.tests.compare import compare_workflows


class WorkflowInitial(tests.OnTaskLiveTestCase):

    def setUp(self):
        """Create the required users."""
        super().setUp()
        self.create_users()

    def test_01(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Create the workflow
        self.create_new_workflow(tests.WORKFLOW_NAME, tests.WORKFLOW_DESC)

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
            os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple.csv')
        )

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
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
        self.wait_for_id_and_spinner('table-data_previous')

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
            os.path.join(settings.ONTASK_FIXTURE_DIR, 'simple2.csv')
        )

        # Click on the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@name='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
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
        self.wait_for_id_and_spinner('table-data_previous')

        # Go to column details
        self.go_to_details()

        # Seventh column must be: another, string
        self.assert_column_name_type('one', 'Text')

        # Eight column must be one string
        self.assert_column_name_type('another', 'Text')

        # End of session
        self.logout()

    def test_02(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Create the workflow
        self.create_new_workflow(tests.WORKFLOW_NAME, tests.WORKFLOW_DESC)

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
                settings.ONTASK_FIXTURE_DIR,
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
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
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
        self.wait_for_id_and_spinner('table-data_previous')

        # Check that the number of rows is the correct one in the only
        # workflow available
        wf = models.Workflow.objects.all()[0]
        self.assertEqual(wf.nrows, 3)
        self.assertEqual(wf.ncols, 6)

        # End of session
        self.logout()


class WorkflowAttribute(tests.SimpleWorkflowFixture, tests.OnTaskLiveTestCase):

    def test(self):
        pass

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(tests.WORKFLOW_NAME)

        # Click on the more-ops and then attributes button
        self.go_to_attribute_page()

        # Attributes are initially empty
        self.assertIn('Attributes are pairs', self.selenium.page_source)

        # Create key1, value1
        self.create_attribute('key1', 'value1')

        # Values now should be in the table
        self.search_table_row_by_string('attribute-table', 2, 'key1')
        self.search_table_row_by_string('attribute-table', 3, 'value1')

        # Create key2, value2
        self.create_attribute('key2', 'value2')
        self.search_table_row_by_string('attribute-table', 2, 'key2')
        self.search_table_row_by_string('attribute-table', 3, 'value2')

        # Rename second attribute
        self.selenium.find_element_by_xpath(
            "//tr/td[2][normalize-space() = 'key2']/../td[1]/div/button[1]"
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
        workflow = models.Workflow.objects.all()[0]
        self.assertEqual(len(workflow.attributes), 2)
        self.assertEqual(workflow.attributes['key1'], 'value1')
        self.assertEqual(workflow.attributes['newkey2'], 'newvalue2')

        # Go back to the attribute page
        self.go_to_attribute_page()

        # click the delete button in the second row
        self.selenium.find_element_by_xpath(
            '//table[@id="attribute-table"]'
            '//tr[2]/td[1]//button[contains(@class, "js-attribute-delete")]'
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

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

        # There should only be a single element
        self.assertEqual(
            len(self.selenium.find_elements_by_xpath(
                '//table[@id="attribute-table"]/tbody/tr'
            )),
            1
        )
        # Check that the attributes are properly stored in the workflow
        workflow = models.Workflow.objects.all()[0]
        self.assertEqual(len(workflow.attributes), 1)
        self.assertEqual(workflow.attributes['key1'], 'value1')

        # End of session
        self.logout()


class WorkflowShare(tests.SimpleWorkflowFixture, tests.OnTaskLiveTestCase):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(tests.WORKFLOW_NAME)

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
        self.search_table_row_by_string(
            'share-table',
            2,
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
        self.search_table_row_by_string(
            'share-table',
            2,
            'instructor02@bogus.com')

        # Check that the shared users are properly stored in the workflow
        workflow = models.Workflow.objects.all()[0]
        self.assertEqual(workflow.shared.count(), 2)
        users = workflow.shared.values_list('email', flat=True)
        self.assertTrue('instructor02@bogus.com' in users)
        self.assertTrue('superuser@bogus.com' in users)

        # click the delete button in the superuser@bogus.com row
        element = self.search_table_row_by_string(
            'share-table',
            2,
            'superuser@bogus.com')
        element.find_element_by_xpath('td[1]/button').click()

        # Wait for the delete confirmation frame
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'),
                'Confirm user deletion'))
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
        workflow = models.Workflow.objects.all()[0]
        self.assertEqual(workflow.shared.count(), 1)
        users = workflow.shared.values_list('email', flat=True)
        self.assertTrue('instructor02@bogus.com' in users)

        # End of session
        self.logout()


class WorkflowImport(
    tests.SimpleWorkflowExportFixture,
    tests.OnTaskLiveTestCase,
):

    def test(self):

        # Login and wait for the table of workflows
        self.login('instructor01@bogus.com')

        # Click in the import button and wait
        self.selenium.find_element_by_link_text('Import workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Import workflow'))

        # Set the workflow name and file
        wname = self.selenium.find_element_by_id('id_name')
        wname.send_keys('newwf')
        wfile = self.selenium.find_element_by_id('id_wf_file')
        wfile.send_keys(os.path.join(
            settings.ONTASK_FIXTURE_DIR,
            'ontask_workflow.gz'))

        # Click in the submit
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 20).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//h5[contains(@class, 'card-header') "
                 "and normalize-space(text()) = '{0}']".format('newwf')),
            )
        )

        # Check elements in workflow and in newwf
        w1 = models.Workflow.objects.get(name=tests.WORKFLOW_NAME)
        w2 = models.Workflow.objects.get(name='newwf')

        compare_workflows(w1, w2)

        # # Equal descriptions
        # self.assertEqual(
        #     w1.description_text,
        #     w2.description_text)
        #
        # # Equal number of columns
        # self.assertEqual(w1.columns.count(), w2.columns.count())
        #
        # # Identical attributes
        # self.assertEqual(w1.attributes, w2.attributes)
        #
        # # Equal number of rows and columns
        # self.assertEqual(w1.nrows, w2.nrows)
        # self.assertEqual(w1.ncols, w2.ncols)
        #
        # # Equal names and column types
        # for x, y in zip(w1.columns.all(), w2.columns.all()):
        #     self.assertEqual(x.name, y.name)
        #     self.assertEqual(x.data_type, y.data_type)
        #     self.assertEqual(x.is_key, y.is_key)
        #
        # # Equal number of actions
        # self.assertEqual(
        #     w1.actions.count(),
        #     w2.actions.count())
        #
        # # Equal names and content in the conditions
        # for x, y in zip(w1.actions.all(), w2.actions.all()):
        #     self.assertEqual(x.name, y.name)
        #     self.assertEqual(x.description_text, y.description_text)
        #     self.assertEqual(x.text_content, y.text_content)
        #     compare_filters(x.get_filter(), y.get_filter())
        #     self.assertEqual(
        #         x.conditions.count(),
        #         y.conditions.count())
        #     for c1, c2 in zip(x.conditions.all(), y.conditions.all()):
        #         self.assertEqual(c1.name, c2.name)
        #         self.assertEqual(
        #             c1.description_text,
        #             c2.description_text)
        #         self.assertEqual(c1.formula, c2.formula)
        #         self.assertEqual(c1.is_filter, c2.is_filter)

        # End of session
        self.logout()
