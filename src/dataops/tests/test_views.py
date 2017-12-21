# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.shortcuts import reverse
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
            EC.element_to_be_clickable(
                (By.ID, 'id_name')
            )
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

        # Click in the attributes section
        self.selenium.find_element_by_link_text("Attributes").click()

        # Delete the existing one
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]").click()

        # Add a new attribute and insert key (symbols) and value
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        self.selenium.find_element_by_id("id_key").click()
        self.selenium.find_element_by_id("id_key").clear()
        self.selenium.find_element_by_id("id_key").send_keys(symbols + 3)
        self.selenium.find_element_by_id("id_value").click()
        self.selenium.find_element_by_id("id_value").clear()
        self.selenium.find_element_by_id("id_value").send_keys("vvv")

        # Submit new attribute
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]").click()

        # Save and close the attribute page
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[2]").click()

        # Click in the TABLE link
        self.selenium.find_element_by_link_text("Table").click()

        # Verify that everything appears normally

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

        # Click in the RUN link of the action in
        self.selenium.find_element_by_link_text("Run").click()

        # Enter data using the RUN menu. Select one entry to populate
        self.selenium.find_element_by_link_text("1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id("id____ontask___select_1").send_keys(
            "Carmelo Coton2")
        self.selenium.find_element_by_id("id____ontask___select_2").click()
        self.selenium.find_element_by_id("id____ontask___select_2").clear()
        self.selenium.find_element_by_id("id____ontask___select_2").send_keys(
            "xxx")

        # Submit the data for one entry
        self.selenium.find_element_by_xpath(
            "//body[@id='dummybodyid']/div[3]/div/form/button[2]/span").click()

        # FIX FIX FIX!
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        self.selenium.find_element_by_xpath(
            "//table[@id='action-table']/tbody/tr[2]/td[5]/a").click()
        self.selenium.find_element_by_xpath(
            "//div[@id='html-editor']/form/div[2]/div[3]/div[2]").click()
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_id("select-attribute-name").click()
        Select(self.selenium.find_element_by_id(
            "select-attribute-name")).select_by_visible_text("-----")
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_id("select-column-name").click()
        Select(self.selenium.find_element_by_id(
            "select-column-name")).select_by_visible_text("-----")
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_id("select-column-name").click()
        Select(self.selenium.find_element_by_id(
            "select-column-name")).select_by_visible_text("-----")
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_name("Submit").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[3]").click()
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(
            "!#$%&()*+,-./:;<=>?@[\\]^_`{|}~4")
        self.selenium.find_element_by_id("id_description_text").click()
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text(
            "!#$%&()*+,-./:;<=>?@[\\]^_`{|}~")
        self.selenium.find_element_by_name("builder_rule_0_operator").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_operator")).select_by_visible_text(
            "begins with")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name("builder_rule_0_value_0").send_keys(
            "C")
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[2]").click()
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(
            "!#$%&()*+,-./:;<=>?@[\\]^_`{|}~"
        )
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter")).select_by_visible_text(
            "!#$%&()*+,-./:;<=>?@[\\]^_`{|}~")
        self.selenium.find_element_by_name("builder_rule_0_operator").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_operator")).select_by_visible_text(
            "doesn't begin with")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name("builder_rule_0_value_0").send_keys(
            "x")
        self.selenium.find_element_by_xpath(
            "(//button[@type='submit'])[3]").click()
        self.selenium.find_element_by_xpath(
            "//div[@id='html-editor']/form/div[2]/div[3]/div[2]").click()
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/div/div/button[2]/span").click()
        # ERROR: Caught exception [unknown command [editContent]]
        self.selenium.find_element_by_xpath(
            "(//button[@type='button'])[172]").click()
        self.selenium.find_element_by_xpath(
            "(//button[@name='Submit'])[2]").click()

        # End of session
        self.logout()
