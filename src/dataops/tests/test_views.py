# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import time

from django.conf import settings
from django.shortcuts import reverse
from django.utils.html import escape
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db
from workflow.models import Workflow


class DataopsSymbols(test.OntaskLiveTestCase):
    fixtures = ['wflow_symbols']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'wflow_symbols_df.sql'
    )

    def setUp(self):
        super(DataopsSymbols, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsSymbols, self).tearDown()

    def test_01_symbols(self):
        symbols = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~'

        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('sss')
        wf_link.click()
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Edit the name column
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[4]/td[5]/div/button"
        ).click()
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[4]/td[5]/div/ul/li[1]/button"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'id_name'))
        )

        # Replace name by symbols
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Click in the submit/save button
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Click in the New Column button
        self.selenium.find_element_by_class_name(
            'js-workflow-column-add'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Add column')
        )

        # Set name to symbols (new column) and type to string
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)
        self.selenium.find_element_by_id("id_data_type").click()
        Select(self.selenium.find_element_by_id(
            "id_data_type"
        )).select_by_visible_text("string")

        # Save the new column
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'error_1_id_name')))

        # There should be a message saying that the name of this column already
        # exists
        self.assertIn('There is a column already with this name',
                      self.selenium.page_source)

        # Click again in the name and introduce something different
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols + '2')

        # Save the new column
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click in the attributes section
        self.selenium.find_element_by_xpath(
            "//div[@id='workflow-area']/div/button[3]"
        ).click()
        self.selenium.find_element_by_link_text('Attributes').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-attribute-create'))
        )

        # Delete the existing one and confirm deletion
        self.selenium.find_element_by_xpath(
            "//table[@id='attribute-table']/tbody/tr/td[3]/button[2]"
        ).click()
        # Wait for the delete confirmation frame
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'modal-title'),
                                             'Confirm attribute deletion')
        )
        # Click in the delete confirm button
        self.selenium.find_element_by_xpath(
            "//div[@class='modal-footer']/button[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'attribute-table_previous'))
        )

        # Add a new attribute and insert key (symbols) and value
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create attribute')
        )

        # Add key and value
        self.selenium.find_element_by_id("id_key").click()
        self.selenium.find_element_by_id("id_key").clear()
        self.selenium.find_element_by_id("id_key").send_keys(symbols + '3')
        self.selenium.find_element_by_id("id_value").click()
        self.selenium.find_element_by_id("id_value").clear()
        self.selenium.find_element_by_id("id_value").send_keys("vvv")

        # Submit new attribute
        self.selenium.find_element_by_xpath(
            "//div[@class='modal-footer']/button[2]"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('attribute-table_previous')

        # Save and close the attribute page
        self.selenium.find_element_by_link_text('Back').click()
        # Wait for the details page
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click in the TABLE link
        self.selenium.find_element_by_link_text("Table").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'table-data_previous'))
        )

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn(escape(symbols + '2'), self.selenium.page_source)

        # Click in the Actions navigation menu
        self.selenium.find_element_by_link_text("Actions").click()

        # Edit the action-in
        self.selenium.find_element_by_link_text("Edit").click()

        # Set the right columns to process
        select = Select(self.selenium.find_element_by_id(
            'select-column-name'))
        select.select_by_visible_text('!#$%&()*+,-./:;<=>?@[\]^_`{|}~2')
        time.sleep(2)
        # # Table disappears (page is updating)
        # WebDriverWait(self.selenium, 10).until_not(
        #     EC.presence_of_element_located(
        #         (By.ID, 'column-selected-table_previous')
        #     )
        # )
        # Table appears (page refreshed)
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )
        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'))
        select.select_by_visible_text('sid')
        # Table disappears (page is updating)
        # WebDriverWait(self.selenium, 10).until_not(
        #     EC.presence_of_element_located(
        #         (By.ID, 'column-selected-table_previous')
        #     )
        # )
        time.sleep(2)
        # Table appears (page refreshed)
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )
        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'))
        select.select_by_visible_text('email')
        # Table disappears (page is updating)
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )
        # Table appears (page refreshed)
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )

        # Save action-in
        self.selenium.find_element_by_link_text('Done').click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-table_previous'))
        )

        # Click in the RUN link of the action in
        self.selenium.find_element_by_link_text("Run").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Enter data using the RUN menu. Select one entry to populate
        self.selenium.find_element_by_link_text("student1@bogus.com").click()
        self.selenium.find_element_by_id("id____ontask___select_2").click()
        self.selenium.find_element_by_id("id____ontask___select_2").clear()
        self.selenium.find_element_by_id("id____ontask___select_2").send_keys(
            "Carmelo Coton2")
        self.selenium.find_element_by_id("id____ontask___select_3").click()
        self.selenium.find_element_by_id("id____ontask___select_3").clear()
        self.selenium.find_element_by_id("id____ontask___select_3").send_keys(
            "xxx"
        )

        # Submit the data for one entry
        self.selenium.find_element_by_xpath(
            "//body/div[4]/div/form/button[1]/span").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Go Back to the action table
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-table_previous'))
        )

        # Edit the action out
        self.selenium.find_element_by_xpath(
            "//table[@id='action-table']/tbody/tr[2]/td[5]/div/a").click()

        # Insert attribute
        self.selenium.find_element_by_id("select-attribute-name").click()
        Select(self.selenium.find_element_by_id(
            "select-attribute-name")).select_by_visible_text("- Attribute -")

        # Insert column name
        self.selenium.find_element_by_id("select-column-name").click()
        Select(self.selenium.find_element_by_id(
            "select-column-name")).select_by_visible_text(symbols)

        # Insert second column name
        self.selenium.find_element_by_id("select-column-name").click()
        Select(self.selenium.find_element_by_id(
            "select-column-name")).select_by_visible_text(symbols + '2')

        # Create new condition
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))

        # Set the values of the condition
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols + "4")
        self.selenium.find_element_by_id("id_description_text").click()
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text(symbols)
        self.selenium.find_element_by_name("builder_rule_0_operator").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_operator")).select_by_visible_text(
            "begins with")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name("builder_rule_0_value_0").send_keys(
            "C")

        # Save the condition
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]").click()
        self.wait_close_modal_refresh_table('html-editor')

        # Create a filter
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))

        # Fill in the details
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text(symbols + "2")
        self.selenium.find_element_by_name("builder_rule_0_operator").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_operator")).select_by_visible_text(
            "doesn't begin with")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name("builder_rule_0_value_0").send_keys(
            "x")
        # Save the filter
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to reload
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//h4[@id='filter-set']/div/button")
            )
        )

        # Click the preview button
        self.selenium.find_element_by_xpath(
            "//div[@id='html-editor']/form/div[3]/button").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-action-preview-nxt'))
        )

        # Certain name should be in the page now.
        self.assertIn('Carmelo Coton', self.selenium.page_source)

        # Click in the "Close" button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/div/div[2]/button[2]").click()

        # End of session
        self.logout()

    def test_02_symbols(self):
        symbols = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~'

        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('sss')
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Select the email column and click in the edit button
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[3]/td[5]/div/button"
        ).click()
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[3]/td[5]/div/ul/li[1]/button"
        ).click()
        # Wait for the form to create the derived column
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Edit column')
        )

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Select the age column and click in the edit button
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[4]/td[5]/div/button"
        ).click()
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[4]/td[5]/div/ul/li[1]/button"
        ).click()
        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Edit column')
        )

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Go to the table link
        self.selenium.find_element_by_link_text("Table").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'table-data_previous'))
        )

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn('<td class=" dt-center">12</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">12.1</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">13.2</td>',
                      self.selenium.page_source)

        # Go to the actions page
        self.selenium.find_element_by_link_text("Actions").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-table_previous'))
        )

        # Edit the action-in at the top of the table
        self.selenium.find_element_by_link_text("Edit").click()

        # Set the correct values for an action-in
        # Set the right columns to process
        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'))
        select.select_by_visible_text('email')
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME,
                                        'js-workflow-column-edit'))
        )

        # Done editing the action in
        self.selenium.find_element_by_link_text('Done').click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-table_previous'))
        )

        # Click in the run link
        self.selenium.find_element_by_link_text("Run").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Click on the first value
        self.selenium.find_element_by_link_text("student1@bogus.com").click()

        # Modify the value of the column
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id("id____ontask___select_1").send_keys(
            "14"
        )
        # Submit changes to the first element
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Click on the second value
        self.selenium.find_element_by_link_text("student2@bogus.com").click()

        # Modify the value of the column
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id(
            "id____ontask___select_1"
        ).send_keys("15")
        # Submit changes to the second element
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Click on the third value
        self.selenium.find_element_by_link_text("student3@bogus.com").click()

        # Modify the value of the column
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id(
            "id____ontask___select_1"
        ).send_keys("16")
        # Submit changes to the second element
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Click in the back link!
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-table_previous'))
        )

        # Go to the table page
        self.selenium.find_element_by_link_text("Table").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'table-data_previous'))
        )

        # Assert the new values
        self.assertIn('<td class=" dt-center">14</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">15</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">16</td>',
                      self.selenium.page_source)

        # End of session
        self.logout()


class DataopsExcelUpload(test.OntaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsExcelUpload, self).tearDown()

    def test_01_excelupload(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('wflow1')
        wf_link.click()

        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Data Upload/Merge").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )

        self.selenium.find_element_by_link_text("Excel Upload/Merge").click()
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'excel_upload.xlsx')
        )
        self.selenium.find_element_by_id("id_sheet").click()
        self.selenium.find_element_by_id("id_sheet").clear()
        self.selenium.find_element_by_id("id_sheet").send_keys("results")
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'checkAll'))
        )
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Details')
        )

        # The number of rows must be 29
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 29)
        self.assertEqual(wflow.ncols, 14)

        # End of session
        self.logout()


class DataopsExcelUploadSheet(test.OntaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsExcelUploadSheet, self).tearDown()

    def test_01_excelupload_sheet(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('wflow1')
        wf_link.click()

        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Data Upload/Merge").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )
        self.selenium.find_element_by_link_text("Excel Upload/Merge").click()
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'excel_upload.xlsx')
        )
        self.selenium.find_element_by_id("id_sheet").click()
        self.selenium.find_element_by_id("id_sheet").clear()
        self.selenium.find_element_by_id("id_sheet").send_keys("second sheet")
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'checkAll'))
        )
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Details')
        )

        # The number of rows must be 19
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 19)
        self.assertEqual(wflow.ncols, 14)

        # End of session
        self.logout()


class DataopsNaNProcessing(test.OntaskLiveTestCase):
    fixtures = ['empty_wflow']
    action_text = "Bool1 = {{ bool1 }}\\n" + \
                  "Bool2 = {{ bool2 }}\\n" + \
                  "Bool3 = {{ bool3 }}\\n" + \
                  "{% if bool1 cond %}Bool 1 is true{% endif %}\\n" + \
                  "{% if bool2 cond %}Bool 2 is true{% endif %}\\n" + \
                  "{% if bool3 cond %}Bool 3 is true{% endif %}\\n"

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsNaNProcessing, self).tearDown()

    def test_01_nan_manipulation(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # Create new workflow
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name'))
        )

        # Insert name and click create
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("NaN")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        # Wait for details page
        WebDriverWait(self.selenium, 20).until(
            EC.title_is('OnTask :: Details')
        )

        # Open the Dataops page
        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Data Upload/Merge").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )

        # Start the upload process: Select upload
        self.selenium.find_element_by_link_text("CSV Upload/Merge").click()

        # Select file and upload
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'test_df_merge_update_df1.csv')
        )
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Step 2: Select Columns')
        )

        # Submit
        self.selenium.find_element_by_xpath(
            "(//button[@name='Submit'])[2]"
        ).click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 20).until(
            EC.title_is('OnTask :: Details')
        )

        # Select again the upload/merge function
        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Data Upload/Merge").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )
        self.selenium.find_element_by_link_text("CSV Upload/Merge").click()

        # Select the second file and submit
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'test_df_merge_update_df2.csv')
        )
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Step 2: Select Columns')
        )

        # Select all the columns for upload
        self.selenium.find_element_by_name("Submit").click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-header'),
                'Step 3: Select Keys and Merge Option')
        )

        # Choose the default options for the merge (key and outer)
        # Select the merger function type
        select = Select(self.selenium.find_element_by_id('id_how_merge'))
        select.select_by_value('outer')
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-header'),
                'Step 4: Review and confirm')
        )

        # Check the merge summary and proceed
        self.selenium.find_element_by_name("Submit").click()
        # Wait for the upload/merge to finish
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Workflow Details')
        )
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success'))
        )

        # Go to the actions page
        self.selenium.find_element_by_link_text("Actions").click()

        # Create a new action
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name'))
        )

        # Type action name and click complete to edit
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("action out")
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//h4[@id='filter-set']/div/button")
            )
        )

        # Create the first condition.
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add name and condition
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("bool1 cond")
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text("bool1")
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@name='builder_rule_0_value_0']")
            )
        )
        self.selenium.find_element_by_xpath(
            "(//input[@name='builder_rule_0_value_0'])[2]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Create the second condition
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add name and condition
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("bool2 cond")
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text("bool2")
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@name='builder_rule_0_value_0']")
            )
        )
        self.selenium.find_element_by_xpath(
            "(//input[@name='builder_rule_0_value_0'])[2]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]"
        ).click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # Create the third condition
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]"
        ).click()
        # Wait for the form to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Create condition')
        )

        # Add name and condition
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("bool3 cond")
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text("bool3")
        # Wait for the select elements to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@name='builder_rule_0_value_0']")
            )
        )
        self.selenium.find_element_by_xpath(
            "(//input[@name='builder_rule_0_value_0'])[2]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]").click()
        # MODAL WAITING
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-edit')
            )
        )

        # insert the action text
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', 
            "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.selenium.find_element_by_xpath(
            "//button[contains(@class, 'js-action-preview')]").click()
        # Wait for the modal to appear
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/div/div/h4"),
                'Action Preview 1')
        )

        for x in range(11):
            self.selenium.find_element_by_xpath(
                "//div[@id='modal-item']/div/div/div/div[2]/button[3]/span"
            ).click()

        # End of session
        self.logout()


class DataopsPluginExecution(test.OntaskLiveTestCase):
    fixtures = ['plugin_execution']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'plugin_execution.sql'
    )

    def setUp(self):
        super(DataopsPluginExecution, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsPluginExecution, self).tearDown()

    def test_01_first_plugin(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('Plugin test')
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Open the transform page
        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Transform").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'transform-table_previous'))
        )

        # Click in the first plugin
        self.selenium.find_element_by_xpath(
            "//table[@id='transform-table']/tbody/tr[4]/td[7]/div/a"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Provide the execution data
        self.selenium.find_element_by_xpath("//input[@type='text']").click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()

        # Click outside the SOL widget
        self.selenium.find_element_by_class_name(
            'sol-current-selection'
        ).click()

        self.selenium.find_element_by_id("id_merge_key").click()
        Select(self.selenium.find_element_by_id(
            "id_merge_key"
        )).select_by_visible_text("email")
        # Submit the execution
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'plugin-execution-report'))
        )

        # Done. Click continue.
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 1' in set(df.columns))
        self.assertTrue('RESULT 2' in set(df.columns))
        self.assertTrue(all([x == 1 for x in df['RESULT 1']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2']]))

        # Second execution, this time adding a suffix to the column
        # Open the transform page
        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Transform").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'transform-table_previous'))
        )

        # Click in the first plugin
        self.selenium.find_element_by_xpath(
            "//table[@id='transform-table']/tbody/tr[4]/td[7]/div/a"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Provide the execution data
        self.selenium.find_element_by_xpath("//input[@type='text']").click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()
        # Click outside the SOL widget
        self.selenium.find_element_by_class_name(
            'sol-current-selection'
        ).click()
        self.selenium.find_element_by_id("id_merge_key").click()
        Select(self.selenium.find_element_by_id(
            "id_merge_key"
        )).select_by_visible_text("email")

        # Put the suffix _2
        self.selenium.find_element_by_id("id_out_column_suffix").click()
        self.selenium.find_element_by_id("id_out_column_suffix").clear()
        self.selenium.find_element_by_id("id_out_column_suffix").send_keys("_2")

        # Submit the execution
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'plugin-execution-report'))
        )

        # Done. Click continue.
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 1_2' in set(df.columns))
        self.assertTrue('RESULT 2_2' in set(df.columns))
        self.assertTrue(all([x == 1 for x in df['RESULT 1_2']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2_2']]))


        # End of session
        self.logout()

    def test_02_second_plugin(self):
        # Login
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))

        # GO TO THE WORKFLOW PAGE
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Workflows'))
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('Plugin test')
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Open the transform page
        self.selenium.find_element_by_link_text("Dataops").click()
        self.selenium.find_element_by_link_text("Transform").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'transform-table_previous'))
        )

        # Click in the second plugin
        self.selenium.find_element_by_xpath(
            "//table[@id='transform-table']/tbody/tr[5]/td[7]/div/a"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Provide the execution data
        self.selenium.find_element_by_id("id_merge_key").click()
        Select(self.selenium.find_element_by_id(
            "id_merge_key"
        )).select_by_visible_text("email")
        # Submit the execution
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'plugin-execution-report'))
        )

        # Done. Click continue.
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 3' in set(df.columns))
        self.assertTrue('RESULT 4' in set(df.columns))
        self.assertTrue(df['RESULT 3'].equals(df['A1'] + df['A2']))
        self.assertTrue(df['RESULT 4'].equals(df['A1'] - df['A2']))

        # End of session
        self.logout()

