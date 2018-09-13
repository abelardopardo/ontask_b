# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.test import TestCase, LiveServerTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys

from action.models import Action
from dataops import pandas_db
from ontask.permissions import group_names

# email, [groups], Superuser?
user_info = [
    ('Student One', 'student1@bogus.com', [group_names[0]], False),
    ('Student Two', 'student2@bogus.com', [group_names[0]], False),
    ('Student Three', 'student3@bogus.com', [group_names[0]], False),
    ('Instructor One', 'instructor1@bogus.com', [group_names[1]], False),
    ('Instructor Two', 'instructor2@bogus.com', [group_names[1]], False),
    ('Instructor Three', 'instructor3@bogus.com', [group_names[1]], False),
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


class OntaskTestCase(TestCase):
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
    @classmethod
    def setUpClass(cls):
        super(OntaskLiveTestCase, cls).setUpClass()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("dom.file.createInChild", True)
        cls.selenium = webdriver.Firefox(firefox_profile=fp)
        cls.selenium.set_window_size(2880, 1800)
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
            EC.title_is("OnTask :: Workflows")
        )

        self.assertIn('Open or create a workflow', self.selenium.page_source)

    def logout(self):
        self.open(reverse('accounts:logout'))

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

    def create_new_workflow(self, wname, wdesc=''):
        # Create the workflow
        self.selenium.find_element_by_class_name(
            'js-create-workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name'))
        )

        self.selenium.find_element_by_id('id_name').send_keys(wname)
        desc = self.selenium.find_element_by_id('id_description_text')
        desc.send_keys(wdesc)
        desc.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )

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

    def go_to_upload_merge(self):
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Manage table data']"
        ).click()
        self.selenium.find_element_by_link_text('Upload or merge data')
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Data Upload/Merge')
        )

    def go_to_csv_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//tbody/tr[1]/td[1]/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )

    def go_to_excel_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//tbody/tr[2]/td[1]/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge Excel')
        )

    def go_to_transform(self):
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Manage table data']"
        ).click()
        self.selenium.find_element_by_link_text('Execute plugin').click()
        self.wait_for_datatable('transform-table_previous')

    def go_to_attribute_page(self):
        self.selenium.find_element_by_xpath(
            "//buton[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_link_text('Workflow attributes').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-attribute-create')))

    def go_to_share(self):
        # Click on the share
        self.selenium.find_element_by_xpath(
            "//buton[normalize-space()='More workflow operations']"
        ).click()
        self.selenium.find_element_by_link_text('Share workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-share-create')))

    def go_to_actions(self):
        # Goto the action page
        self.selenium.find_element_by_link_text('Actions').click()
        # Wait for page to refresh
        self.wait_for_datatable('action-table_previous')
        self.assertIn('New Action', self.selenium.page_source)

    def go_to_table(self):
        self.selenium.find_element_by_link_text("Table").click()
        self.wait_for_datatable('table-data_previous')
        self.assertIn('Table View', self.selenium.page_source)

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
            "//buton[normalize-space()='Add column']"
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

    def delete_column(self, col_name):
        element = self.search_table_row_by_string('column-table', 2, col_name)
        element.find_element_by_xpath(
            "button[normalize-space()='More Operations']"
        ).click()
        element.find_element_by_xpath(
            "button[normalize-space()='Delete this column']"
        ).click()

        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//form/div/h4[@class='modal-title']"),
                'Confirm column deletion')
        )
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('column-table_previous')

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

    def create_condition_base(self, zone_xpath, cname, cdesc, rule_tuples):
        # Click on the right button
        self.selenium.find_element_by_xpath(zone_xpath).click()
        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

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
        self.wait_close_modal_refresh_table('html-editor')

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
            EC.presence_of_element_located((By.CLASS_NAME, 'modal-open'))
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
            EC.presence_of_element_located((By.CLASS_NAME, 'modal-open'))
        )

    def open_column_edit(self, name):
        row = self.search_table_row_by_string('column-table', 2, name)
        row.find_element_by_xpath("td[5]/div/button").click()
        row.find_element_by_xpath("td[5]/div/ul/li[1]/button").click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'id_name'))
        )

    def open_action_edit(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Edit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'js-action-preview')]"),
            )
        )

    def open_action_run(self, name):
        element = self.search_action(name)
        element.find_element_by_link_text("Run").click()
        self.wait_for_datatable('actioninrun-data_previous')

    def open_browse_preview(self, n=0, close=True):
        self.selenium.find_element_by_xpath(
            "//button[contains(@class, 'js-action-preview')]").click()
        # Wait for the modal to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

        for x in range(n):
            self.selenium.find_element_by_xpath(
                "//div[@id='modal-item']/div/div/div/div[2]/button[3]/span"
            ).click()

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

    def create_condition(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-condition-create')]",
            cname,
            cdesc,
            rule_tuples)

    def edit_condition(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-condition-edit')]",
            cname,
            cdesc,
            rule_tuples)

    def create_filter(self, cname, cdesc, rule_tuples):
        self.create_condition_base(
            "//button[contains(@class, 'js-filter-create')]",
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
