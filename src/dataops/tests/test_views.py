# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.shortcuts import reverse
from django.utils.html import escape
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db


class DataopsSymbols(test.OntaskLiveTestCase):
    fixtures = ['wflow_symbols']
    filename = os.path.join(
        settings.PROJECT_PATH,
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
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('sss')
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success'))
        )

        # Edit the name column
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[4]/td[4]/button/span"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'id_name')
            )
        )

        # Replace name by symbols
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Click in the submit/save button
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()

        # Click in the New Column button
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]"
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
        # Wait for the modal to close
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        # FLAKY
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success'))
        )

        # Click in the attributes section
        self.selenium.find_element_by_xpath(
            "//div[@id='workflow-area']/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-attribute-create'))
        )

        # Delete the existing one and confirm deletion
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]").click()
        # Wait for modal to close
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        # FLAKY
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,
                                            'js-attribute-create'))
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
            "(//button[@type='submit'])[3]").click()
        # Wait for modal to close
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        # Save and close the attribute page
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]").click()

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
        self.selenium.find_element_by_id("id____ontask___select_3").click()
        self.selenium.find_element_by_id("id____ontask___select_4").click()
        self.selenium.find_element_by_id("id____ontask___select_1").click()

        # Submit the new action in
        self.selenium.find_element_by_xpath(
            "(//button[@name='Submit'])[2]").click()
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
        self.selenium.find_element_by_link_text("1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id("id____ontask___select_1").send_keys(
            "Carmelo Coton2")
        self.selenium.find_element_by_id("id____ontask___select_2").click()
        self.selenium.find_element_by_id("id____ontask___select_2").clear()
        self.selenium.find_element_by_id("id____ontask___select_2").send_keys(
            "xxx"
        )

        # Submit the data for one entry
        self.selenium.find_element_by_xpath(
            "//body/div[3]/div/form/button[1]/span").click()
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
            "//table[@id='action-table']/tbody/tr[2]/td[5]/a").click()

        # Insert attribute
        self.selenium.find_element_by_id("select-attribute-name").click()
        Select(self.selenium.find_element_by_id(
            "select-attribute-name")).select_by_visible_text("-----")

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
            "(//button[@type='submit'])[3]").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

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
            "builder_rule_0_filter")).select_by_visible_text(symbols)
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
            "(//button[@type='submit'])[3]").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
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
        self.assertIn('New Workflow', self.selenium.page_source)
        self.assertIn('Import', self.selenium.page_source)

        # Open the workflow
        wf_link = self.selenium.find_element_by_link_text('sss')
        wf_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Select the email column and click in the edit button
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[1]/td[4]/button/span"
        ).click()

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

        # Select the age column and click in the edit button
        self.selenium.find_element_by_xpath(
            "//table[@id='column-table']/tbody/tr[3]/td[4]/button/span"
        ).click()

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'column-table_previous'))
        )

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
        self.selenium.find_element_by_id("id____ontask___select_3").click()
        self.selenium.find_element_by_id("id____ontask___select_0").click()
        self.selenium.find_element_by_xpath("(//button[@name='Submit'])[2]").click()
        # Web for the modal to close
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for page to refresh
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
            "(//button[@name='submit'])[2]"
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
            "(//button[@name='submit'])[2]"
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
            "(//button[@name='submit'])[2]"
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
