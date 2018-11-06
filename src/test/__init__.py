# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO
import os
import math

import pandas as pd
from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.test import TransactionTestCase, LiveServerTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from action.models import Action
from dataops import pandas_db
from ontask.permissions import group_names

# email, [groups], Superuser?
user_info = [
    ('Student One', 'student01@bogus.com', [group_names[0]], False),
    ('Student Two', 'student02@bogus.com', [group_names[0]], False),
    ('Student Three', 'student03@bogus.com', [group_names[0]], False),
    ('Instructor One', 'instructor01@bogus.com', [group_names[1]], False),
    ('Instructor Two', 'instructor02@bogus.com', [group_names[1]], False),
    ('Instructor Three', 'instructor03@bogus.com', [group_names[1]], False),
    ('Super User', 'superuser@bogus.com', group_names, True)]

boguspwd = 'boguspwd'

# Workflow elements used in various tests
wflow_name = 'wflow1'
wflow_desc = 'description text for workflow 1'
wflow_empty = 'The workflow does not have data'


def create_groups():
    """
    Create the user groups for OnTask
    :return:
    """

    for gname in group_names:
        Group.objects.get_or_create(name=gname)


def create_users():
    """
    Create all the users based in the user_info
    :return:
    """

    # Create the groups first
    create_groups()

    for uname, uemail, glist, suser in user_info:
        try:
            uobj = get_user_model().objects.get(email=uemail)
        except ObjectDoesNotExist:
            uobj = get_user_model().objects.create_user(
                name=uname,
                email=uemail,
                password=boguspwd)

        for gname in glist:
            gobj = Group.objects.get(name=gname)
            uobj.groups.add(gobj)
            uobj.save()

    # Create the tokens for all the users
    for usr in get_user_model().objects.all():
        Token.objects.create(user=usr)


class ElementHasFullOpacity(object):
    """
    Detect when an element has opacity equal to 1

    locator - used to find the element
    returns the WebElement once opacity is equal to 1
    """

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if element.value_of_css_property('opacity') == '1':
            return element
        else:
            return False


class OntaskTestCase(TransactionTestCase):
    @classmethod
    def tearDownClass(cls):
        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskTestCase, cls).tearDownClass()


class OntaskApiTestCase(APITransactionTestCase):
    @classmethod
    def tearDownClass(cls):
        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskApiTestCase, cls).tearDownClass()

    def compare_wflows(self, jwflow, workflow):
        # Name and description match the one in the db
        self.assertEqual(jwflow['name'], workflow.name)
        self.assertEqual(jwflow['description_text'],
                         workflow.description_text)

        jattr = jwflow['attributes']
        dattr = workflow.attributes
        self.assertEqual(set(jattr.items()),
                         set(dattr.items()))

    def compare_tables(self, m1, m2):
        """
        Compares two pandas data frames
        :param m1: Pandas data frame
        :param m2: Pandas data frame
        :return:
        """

        # If both are empty, done.
        if m2 is None and m1 is None:
            return

        # Assert that the number of columns are identical
        self.assertEqual(len(list(m1.columns)),
                         len(list(m2.columns)))

        # The names of the columns have to be identical
        self.assertEqual(set(list(m1.columns)),
                         set(list(m2.columns)))

        # Check the values of every column
        for cname in list(m1.columns):
            jvals = m1[cname].values
            dfvals = m2[cname].values

            # Compare removing the NaN, otherwise, the comparison breaks.
            self.assertEqual(
                [x for x in list(jvals) if not pd.isnull(x)],
                [x for x in list(dfvals) if not pd.isnull(x)]
            )


class OntaskLiveTestCase(LiveServerTestCase):

    viewport_height = 2880
    viewport_width = 1800

    @classmethod
    def setUpClass(cls):
        super(OntaskLiveTestCase, cls).setUpClass()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("dom.file.createInChild", True)
        cls.selenium = webdriver.Firefox(firefox_profile=fp)
        # cls.selenium = webdriver.Chrome()
        cls.selenium.set_window_size(cls.viewport_height,
                                     cls.viewport_width)
        # cls.selenium.implicitly_wait(30)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        pandas_db.destroy_db_engine(pandas_db.engine)
        super(OntaskLiveTestCase, cls).tearDownClass()

    def open(self, url):
        self.selenium.get("%s%s" % (self.live_server_url, url))

    def login(self, uemail):
        self.open(reverse('accounts:login'))
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username')))
        self.selenium.find_element_by_id('id_username').send_keys(uemail)
        self.selenium.find_element_by_id('id_password').send_keys(boguspwd)
        self.selenium.find_element_by_id('submit-id-sign_in').click()
        # Wait for the user profile page
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@id='workflow-table']/tbody/tr/td")
            )
        )

        self.assertIn('Open or create a workflow', self.selenium.page_source)

    def logout(self):
        self.open(reverse('accounts:logout'))
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@id='div_id_username']")
            )
        )

    def wait_for_modal_open(self, xpath="//div[@id='modal-item']//form"):
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def wait_for_datatable(self, table_id):
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, table_id))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def wait_close_modal_refresh_table(self, table_id):
        """
        Function used  to wait for a modal window to close and for a table
        with certain ID to appear again as a consequence of the browser's
        response.
        :param table_id: Id of the table being refreshed
        :return:
        """
        # Close modal (wail until the modal-open element disappears)
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Wait for the table to be refreshed
        self.wait_for_datatable(table_id)

    def wait_for_page(self, title=None, element_id=None):
        if title:
            WebDriverWait(self.selenium, 10).until(
                EC.title_is(title)
            )

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.invisibility_of_element_located((By.ID, 'img-spinner'))
        )

        if element_id:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, element_id))
            )

    def cancel_modal(self):
        # Click in the cancel button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@data-dismiss='modal']"
        ).click()
        # Wail until the modal-open element disappears
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

    def search_table_row_by_string(self, table_id, colidx, value):
        """
        Given a table id and a column index, it traverses the table searching
        for the given value in the column.
        :param table_id: ID of the HTML table element
        :param colidx: Column index
        :param value: Value to search
        :return: Row Element
        """
        # Table ID must be in the page
        self.assertIn(table_id, self.selenium.page_source)

        rows = self.selenium.find_elements_by_xpath(
            "//table[@id='{0}']/tbody/tr/td[{1}]".format(table_id, colidx)
        )
        self.assertTrue(rows, 'No rows found in table {0}'.format(table_id))

        names = [x.text for x in rows]
        self.assertTrue(value in names,
                        "{0} not in table {1}.".format(value, table_id))
        return self.selenium.find_element_by_xpath(
            "//table[@id='{0}']/tbody/tr[{1}]".format(
                table_id, names.index(value) + 1
            )
        )

    def search_action(self, action_name):
        return self.search_table_row_by_string('action-table', 1, action_name)

    def search_column(self, column_name):
        return self.search_table_row_by_string('column-table', 2, column_name)

    def access_workflow_from_home_page(self, wname, wait=True):
        # Verify that this is the right page
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        row_element = self.search_table_row_by_string('workflow-table',
                                                      1,
                                                      wname)
        row_element.find_element_by_xpath("td[5]/div/a").click()

        if wait:
            self.wait_for_datatable('column-table_previous')

    def go_to_details(self):
        # Goto the details page
        self.selenium.find_element_by_link_text('Details').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-area'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.assertIn('More workflow operations', self.selenium.page_source)

    def go_to_sql_connections(self):
        # Goto the details page
        self.selenium.find_element_by_link_text('SQL Connections').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'sqlconn-table'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def go_to_upload_merge(self):
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Manage table data']"
        ).click()
        self.selenium.find_element_by_link_text('Upload or merge data').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@id='dataops-table']")
            )
        )

    def go_to_csv_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//tbody/tr[1]/td[1]/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

    def go_to_excel_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//tbody/tr[2]/td[1]/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

    def go_to_sql_upload_merge(self):
        self.go_to_upload_merge()

        # Goto SQL option
        self.selenium.find_element_by_xpath(
            "//table[@id='dataops-table']//a[normalize-space()='SQL "
            "Connections']").click()
        self.wait_for_datatable('sqlconn-table_previous')

    def go_to_transform(self):
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Manage table data']"
        ).click()
        self.selenium.find_element_by_link_text('Execute plugin').click()
        self.wait_for_datatable('transform-table_previous')

    def go_to_attribute_page(self):
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_link_text('Workflow attributes').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-attribute-create')))

    def go_to_workflow_share(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_link_text('Share workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-share-create')))

    def go_to_workflow_export(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_link_text('Export workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))

    def go_to_workflow_rename(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Rename workflow']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def go_to_workflow_flush(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Flush data table']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def go_to_workflow_delete(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Delete workflow']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def go_to_actions(self):
        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        # Wait for page to refresh
        self.wait_for_datatable('action-table_previous')
        self.assertIn('New action', self.selenium.page_source)

    def go_to_table(self):
        self.selenium.find_element_by_link_text("Table").click()
        self.wait_for_datatable('table-data_previous')
        self.assertIn('Table', self.selenium.page_source)

    def go_to_scheduler(self):
        # Goto the action page
        self.selenium.find_element_by_link_text('Scheduler').click()
        # Wait for page to refresh
        self.wait_for_datatable('scheduler-table_previous')
        self.assertIn('Scheduled Operations', self.selenium.page_source)

    def go_to_logs(self):
        # Goto the action page
        self.selenium.find_element_by_link_text('Logs').click()
        # Wait for page to refresh
        self.wait_for_datatable('log-table_previous')
        self.assertIn('Logs', self.selenium.page_source)

    def go_to_table_views(self):
        self.go_to_table()

        self.selenium.find_element_by_link_text("Table").click()
        self.wait_for_datatable('table-data_previous')
        self.assertIn('Table View', self.selenium.page_source)

        self.selenium.find_element_by_link_text('Views').click()
        self.wait_for_datatable('view-table_previous')

    def add_column(self,
                   col_name,
                   col_type,
                   col_categories='',
                   col_init='',
                   index=None):
        # Click on the Add Column -> Regular column
        self.open_add_regular_column()

        # Set the fields
        self.selenium.find_element_by_id('id_name').send_keys(col_name)
        select = Select(self.selenium.find_element_by_id(
            'id_data_type'))
        select.select_by_value(col_type)
        if col_categories:
            self.selenium.find_element_by_id(
                'id_raw_categories').send_keys(col_categories)
        if col_init:
            self.selenium.find_element_by_id(
                'id_initial_value'
            ).send_keys(col_init)
        if index:
            self.selenium.find_element_by_id('id_position').send_keys(
                str(index)
            )

        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[normalize-space()='Add column']"
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

    def delete_column(self, col_name):
        element = self.search_table_row_by_string('column-table', 2, col_name)
        element.find_element_by_xpath(
            "td//button[normalize-space()='Delete']"
        ).click()

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('column-table_previous')

    def create_new_workflow(self, wname, wdesc=''):
        # Create the workflow
        self.selenium.find_element_by_class_name(
            'js-create-workflow').click()
        self.wait_for_modal_open()

        self.selenium.find_element_by_id('id_name').send_keys(wname)
        desc = self.selenium.find_element_by_id('id_description_text')
        desc.send_keys(wdesc)
        desc.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@id='dataops-table']")
            )
        )

    def create_new_personalized_text_action(self, aname, adesc=''):
        # click in the create action button
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys(aname)
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(Action.PERSONALIZED_TEXT)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h4[@id='filter-set']/div/button")
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def create_attribute(self, attribute_key, attribute_value):
        # Click in the new attribute dialog
        self.selenium.find_element_by_class_name('js-attribute-create').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'modal-title'),
                                             'Create attribute')
        )

        # Fill out the form
        element = self.selenium.find_element_by_id('id_key')
        element.clear()
        element.send_keys(attribute_key)
        element = self.selenium.find_element_by_id('id_value')
        element.clear()
        element.send_keys(attribute_value)

        # Click in the create attribute button
        self.selenium.find_element_by_xpath(
            "//div[@class='modal-footer']/button[normalize-space()='Create "
            "attribute']"
        ).click()

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

    def create_new_survey_action(self, aname, adesc=''):
        # click in the create action button
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys(aname)
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(Action.SURVEY)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h4[@id='filter-set']/div/button")
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def create_filter(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-filter-create')]",
            cname,
            cdesc,
            rule_tuples)

    def create_condition(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-condition-create')]",
            cname,
            cdesc,
            rule_tuples)

    def create_condition_base(self, zone_xpath, cname, cdesc, rule_tuples):
        # Open the right modal
        self.open_condition(cname, zone_xpath)

        # Set the values of the condition
        form_field = self.selenium.find_element_by_id("id_name")
        form_field.click()
        form_field.clear()
        form_field.send_keys(cname)
        if cdesc:
            form_field = self.selenium.find_element_by_id("id_description_text")
            form_field.click()
            form_field.clear()
            form_field.send_keys(cdesc)

        idx = 0
        for rule_filter, rule_operator, rule_value in rule_tuples:
            # Set the FILTER
            form_field = self.selenium.find_element_by_name(
                'builder_rule_{0}_filter'.format(idx)
            )
            form_field.click()
            Select(form_field).select_by_visible_text(rule_filter)

            # Set the operator
            if rule_operator:
                form_field = self.selenium.find_element_by_name(
                    "builder_rule_{0}_operator".format(idx)
                )
                form_field.click()
                Select(form_field).select_by_visible_text(rule_operator)

            # Set the value
            if rule_operator:
                form_item = self.selenium.find_element_by_name(
                    "builder_rule_{0}_value_0".format(idx)
                )
                form_item.click()
                form_item.clear()
                form_item.send_keys(rule_value)
            else:
                # This is the case in which the operator is implicit (boolean)
                if rule_value:
                    value_idx = 2
                else:
                    value_idx = 1
                self.selenium.find_element_by_xpath(
                    "(//input[@name='builder_rule_{0}_value_0'])[{1}]".format(
                        idx,
                        value_idx
                    )
                ).click()

            idx += 1

        # Save the condition
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Close modal (wail until the modal-open element disappears)
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

    def create_view(self, vname, vdesc, cols):
        self.go_to_table_views()

        # Button to add a view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add View']"
        ).click()
        # Wait for the form to create the derived column
        self.wait_for_modal_open()

        # Insert data to create the view
        element = self.selenium.find_element_by_id("id_name")
        element.click()
        element.clear()
        element.send_keys(vname)
        if vdesc:
            element = self.selenium.find_element_by_id("id_description_text")
            element.click()
            element.clear()
            element.send_keys(vdesc)

        # Focus on the column area
        self.selenium.find_element_by_xpath(
            "//*[@placeholder='Click here to search']").click()
        options = self.selenium.find_element_by_xpath(
            '//*[@id="div_id_columns"]//div[@class="sol-selection"]'
        )
        for cname in cols:
            element = options.find_element_by_xpath(
                'div/label/div[normalize-space()="{0}"]'.format(cname)
            ).click()

        self.selenium.find_element_by_css_selector("div.modal-title").click()

        # Save the view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add view']"
        ).click()
        self.wait_close_modal_refresh_table('view-table_previous')

    def open_add_regular_column(self):
        # Click on the Add Column button
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add Column']"
        ).click()

        # Click on the Regular Column
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Regular column']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def open_add_derived_column(self):
        # Click on the Add Column button
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add Column']"
        ).click()

        # Click on the Regular Column
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Formula-derived column']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )

    def open_column_edit(self, name):
        row = self.search_column(name)
        row.find_element_by_xpath(
            "td//button[normalize-space()='Edit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='modal-item']//form")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def open_action_edit(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Edit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'js-action-preview')]"),
            )
        )

    def open_action_rename(self, name):
        element = self.search_action(name)
        element.find_element_by_xpath(
            "td//button[normalize-space()='More']").click()
        element.find_element_by_xpath(
            "td//button[normalize-space()='Rename']").click()
        self.wait_for_modal_open()

    def open_action_email(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Email").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'js-email-preview')]"),
            )
        )

    def open_action_json_run(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Run").click()
        self.wait_for_page(element_id='json-action-request-data')

    def open_action_survey_run(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Run").click()
        self.wait_for_datatable('actioninrun-data_previous')

    def open_action_schedule(self, name):
        row = self.search_action(name)
        row.find_element_by_xpath(
            "td//button[normalize-space()='More']"
        ).click()
        row.find_element_by_xpath(
            "td//a[normalize-space()='Schedule']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='Next']")
            )
        )

    def open_preview(self):
        self.selenium.find_element_by_xpath(
            "//button[contains(@class, 'js-action-preview')]").click()
        # Wait for the modal to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, "preview-body")
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def open_browse_preview(self, n=0, close=True):
        self.open_preview()

        for x in range(n):
            self.selenium.find_element_by_xpath(
                "//div[@id='modal-item']/div/div/div/div[2]/button[3]/span"
            ).click()
            # Wait for the modal to appear
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "preview-body")
                )
            )

        if close:
            self.selenium.find_element_by_xpath(
                "//div[@id='modal-item']/div/div/div/div[2]/button[2]"
            ).click()
            # Close modal (wail until the modal-open element disappears)
            WebDriverWait(self.selenium, 10).until_not(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'modal-open')
                )
            )

    def open_condition(self, cname, xpath=None):
        # Click on the right button
        if xpath:
            self.selenium.find_element_by_xpath(xpath).click()
        else:
            self.selenium.find_element_by_xpath(
                "//div[@id='condition-set']"
                "/div/button[contains(normalize-space(), '{0}')]".format(cname)
            ).click()

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def open_filter(self):
        # Click on the right button
        self.selenium.find_element_by_xpath(
            "//button[contains(@class, 'js-filter-edit')]",
        ).click()

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )

    def open_view(self, vname):
        # Go to views first
        self.go_to_table_views()

        element = self.search_table_row_by_string('view-table', 1, vname)
        element.find_element_by_xpath(
            "td//a[normalize-space()='Table']"
        ).click()
        self.wait_for_datatable('table-data_previous')

    def edit_condition(self, oldname, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//div[@id='condition-set']"
            "/div/button[contains(normalize-space(), '{0}')]".format(oldname),
            cname,
            cdesc,
            rule_tuples)

    def edit_filter(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-filter-edit')]",
            cname,
            cdesc,
            rule_tuples)

    def delete_filter(self):
        self.selenium.find_element_by_xpath(
            "//h4[@id='filter-set']/div/button[2]"
        ).click()
        self.selenium.find_element_by_class_name('js-filter-delete').click()
        # Wait for the screen to delete the filter
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Confirm filter deletion')
        )

        # Click in the "delete filter"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[normalize-space()='Delete filter']"
        ).click()
        self.wait_close_modal_refresh_table('html-editor')

    def delete_condition(self, cname):
        """
        Given a condition name, search for it in the right DIV and click the
        buttons to remove it.
        :param cname: Condition name
        :return:
        """
        # Get the button for the condition
        element = self.selenium.find_element_by_xpath(
            "//div[@id='condition-set']/div/"
            "button[contains(normalize-space(), '{0}')]".format(cname)
        )
        # Get the arrow element
        element = element.find_element_by_xpath('..')
        element.find_element_by_xpath('button[2]').click()

        # Click in the delete button
        element.find_element_by_xpath(
            "ul/li/button[normalize-space()='Delete']"
        ).click()

        # Wait for the screen to delete the condition
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='modal-item']/div/div/form/div/h4"),
                'Confirm condition deletion')
        )

        # Click in the "delete condition"
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[normalize-space()='Delete "
            "condition']"
        ).click()
        self.wait_close_modal_refresh_table('html-editor')


class ScreenTests(OntaskLiveTestCase):
    weight = 1024
    height = 1800
    prefix = ''
    workflow_name = 'BIOL1011'
    description = 'Course on Cell Biology'
    modal_xpath = "//div[@id='modal-item']/div[@class='modal-dialog']/div[" \
                  "@class='modal-content']"

    @staticmethod
    def img_path(f):
        return os.path.join(settings.BASE_DIR(), 'test', 'images', f)

    def element_ss(self, xpath, ss_filename):
        """
        Take the snapshot of the element with the given xpath and store it in
        the given filename
        :return: Nothing
        """

        if not xpath or not ss_filename:
            raise Exception('Incorrect invocation of element_ss')

        element = self.selenium.find_element_by_xpath(xpath)

        coordinates = element.location
        dimensions = element.size

        img = Image.open(StringIO.StringIO(
            self.selenium.find_element_by_xpath(
                xpath
            ).screenshot_as_png)

        )

        # Cap height
        if dimensions['height'] < self.viewport_height / 2:
            img = img.crop(
                (math.floor(2 * coordinates['x']),
                 math.floor(2 * coordinates['y']),
                 math.ceil(2 * coordinates['x'] + 2 * dimensions['width']),
                 math.ceil(2 * coordinates['y'] + 2 * dimensions['height']))
            )

        img.save(self.img_path(self.prefix + ss_filename))

    def modal_ss(self, ss_filename):
        self.element_ss(self.modal_xpath, ss_filename)

    def body_ss(self, ss_filename):
        self.element_ss('//body', ss_filename)

    @classmethod
    def setUpClass(cls):
        super(ScreenTests, cls).setUpClass()
        cls.selenium.set_window_size(cls.weight, cls.height)
