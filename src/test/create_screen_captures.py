# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO
import os

from PIL import Image
from django.conf import settings
from django.shortcuts import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db
from test import element_has_full_opacity


class ScreenTests(test.OntaskLiveTestCase):
    weight = 1024
    height = 1800
    prefix = ''
    workflow_name = 'BIOL1011'
    description = 'Course on Cell Biology'
    modal_xpath = "//div[@id='modal-item']/div[@class='modal-dialog']/div[" \
                  "@class='modal-content']"

    @staticmethod
    def img_path(f):
        return os.path.join(
            settings.BASE_DIR(),
            'test',
            'images',
            f)

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

    def element_ss(self, xpath, ss_filename):
        """
        Take the snapshot of the element with the given xpath and store it in
        the given filename
        :return: Nothing
        """

        if xpath and ss_filename:
            Image.open(StringIO.StringIO(
                self.selenium.find_element_by_xpath(
                    xpath
                ).screenshot_as_png)
            ).save(self.img_path(self.prefix + ss_filename))

    def modal_ss(self, ss_filename):
        self.element_ss(self.modal_xpath, ss_filename)

    def body_ss(self, ss_filename):
        self.element_ss('//body', ss_filename)

    @classmethod
    def setUpClass(cls):
        super(ScreenTests, cls).setUpClass()
        cls.selenium.set_window_size(cls.weight, cls.height)


class ScreenTutorialTest(ScreenTests):

    def setUp(self):
        super(ScreenTutorialTest, self).setUp()
        test.create_users()

    def test_ss_00(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')
        self.body_ss('workflow_index_empty.png')

        #
        # Create new workflow
        #
        self.selenium.find_element_by_class_name(
            'js-create-workflow').click()
        self.wait_for_modal_open()

        self.selenium.find_element_by_id('id_name').send_keys(self.workflow_name)
        desc = self.selenium.find_element_by_id('id_description_text')
        desc.send_keys(self.description)

        # Take capture of the modal
        self.modal_ss('workflow_create.png')

        # Close the modal.
        desc.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@id='dataops-table']")
            )
        )

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)


class ScreenImportTest(ScreenTests):

    def setUp(self):
        super(ScreenImportTest, self).setUp()
        test.create_users()

    def test_ss_01(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Open Import page
        self.selenium.find_element_by_link_text('Import workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Import workflow')
        )

        #
        # Import workflow
        #
        self.selenium.find_element_by_id('id_name').send_keys(
            self.workflow_name
        )
        self.selenium.find_element_by_id('id_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                         '..',
                         'initial_workflow.gz')
        )

        # Picture of the body
        self.body_ss('workflow_import.png')

        # Click the import button
        self.selenium.find_element_by_xpath(
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_page(title='OnTask :: Workflows')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)


class ScreenTestFixture(ScreenTests):
    fixtures = ['../initial_workflow/initial_workflow.json']
    filename = os.path.join(
        settings.BASE_DIR(),
        '..',
        'initial_workflow',
        'initial_workflow.sql'
    )

    wflow_name = 'combine columns'

    def setUp(self):
        super(ScreenTestFixture, self).setUp()
        pandas_db.pg_restore_table(self.filename)

        # Insert a SQL Connection
        # sqlc = SQLConnection(
        #     name='remote server',
        #     description_txt='Server with student records',
        #     conn_type='mysql',
        #     conn_driver='',
        #     db_user='remote_db_user',
        #     db_password=True,
        #     db_host='dbserver.bogus.com',
        #     db_port=None,
        #     db_name='demographics',
        #     db_table='s_records'
        # )
        # sqlc.save()

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(ScreenTestFixture, self).tearDown()

    def test_sql_admin(self):
        # Login
        self.login('superuser@bogus.com')
        self.body_ss('workflow_superuser_index.png')

        #
        # Open SQL Connection
        #
        self.go_to_sql_connections()
        self.body_ss('workflow_sql_connections_index.png')

        # click in the edit element
        element = self.search_table_row_by_string('sqlconn-table',
                                                  1,
                                                  'Remote server')
        element.find_element_by_xpath(
            "td/div/button[normalize-space()='Operations']"
        ).click()
        element.find_element_by_xpath(
            "td//button[normalize-space()='Edit']"
        ).click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('workflow_superuser_sql_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_workflow(self):
        # Login
        self.login('instructor01@bogus.com')

        # List of workflows, navigation
        self.body_ss('workflow_index.png')

        #
        # Navigation bar, details
        #
        self.access_workflow_from_home_page(self.workflow_name)
        self.body_ss('workflow_details.png')

        # Take picture of the navigation bar
        self.element_ss("//body/div[3]", 'navigation_bar.png')

        #
        # New column modal
        #
        self.open_add_regular_column()
        self.modal_ss('workflow_add_column.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # Attributes
        #
        self.go_to_attribute_page()
        self.body_ss('workflow_attributes.png')

        # Click back to the details page
        self.go_to_details()

        #
        # Share
        #
        self.go_to_workflow_share()
        self.body_ss('workflow_share.png')

        # Click back to the details page
        self.go_to_details()

        #
        # EXPORT
        #
        self.go_to_workflow_export()
        self.body_ss('workflow_export.png')

        # Click back to the details page
        self.selenium.find_element_by_xpath(
            "//div[@class='modal-footer']/a[normalize-space()='Cancel']"
        ).click()
        self.wait_for_datatable('column-table_previous')

        #
        # RENAME
        #
        self.go_to_workflow_rename()
        self.modal_ss('workflow_rename.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # FLUSH DATA
        #
        self.go_to_workflow_flush()
        self.modal_ss('workflow_flush.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # DELETE
        #
        self.go_to_workflow_delete()
        self.modal_ss('workflow_delete.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_details(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        # Table of columns (separated)
        self.element_ss("//div[@id='column-table_wrapper']",
                        'wokflow_columns.png')

        #
        # Ops/Edit Column
        #
        self.open_column_edit('SID')
        self.modal_ss('workflow_column_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_dataops(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        # Go to CSV
        self.go_to_upload_merge()
        self.body_ss('dataops_datauploadmerge.png')

        self.selenium.find_element_by_link_text("CSV Upload/Merge").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )
        self.selenium.find_element_by_id('id_file').send_keys(
            os.path.join(settings.BASE_DIR(),
                         '..',
                         'initial_workflow',
                         'initial_workflow.csv')
        )

        # Picture of the body
        self.body_ss('dataops_csvupload.png')

        #
        # Dataops/Merge CSV Merge Step 2
        #
        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='id_make_key_2']")
            )
        )
        # Unckeck the columns that won't be keys
        for k_num in [2, 3, 40, 45, 46, 47, 49, 50, 51, 59, 61, 64]:
            self.selenium.find_element_by_id(
                'id_make_key_{0}'.format(k_num)
            ).click()

        # Picture of the body
        self.body_ss('dataops_upload_merge_step2.png')

        #
        # Dataops/Merge CSV Merge Step 3
        #
        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@id='id_dst_key']")
            )
        )

        #
        # Dataops/Merge CSV Merge Step 4
        #
        # Click the NEXT button
        # Select left merge
        Select(self.selenium.find_element_by_id(
            'id_how_merge'
        )).select_by_value('left')

        # Picture of the body
        self.body_ss('dataops_upload_merge_step3.png')

        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-header'),
                'Step 4: Review and confirm')
        )

        # Picture of the body
        self.body_ss('dataops_upload_merge_step4.png')

        # Click on Finish
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Finish']"
        ).click()
        self.wait_for_datatable('column-table_previous')

        #
        # Dataops/Merge Excel Merge
        #
        # Go to Excel Upload/Merge
        self.go_to_excel_upload_merge_step_1()
        self.body_ss('dataops_upload_excel.png')

        # Back to details
        self.go_to_details()

        #
        # Dataops/Merge SQL Connection
        #
        self.go_to_sql_upload_merge()
        self.body_ss('dataops_SQL_available.png')

        # Click on the link RUN
        self.selenium.find_element_by_link_text('Run').click()

        # Picture of the RUN menu in SQL
        self.body_ss('dataops_SQL_run.png')

        # Go back to details
        self.go_to_details()

        #
        # Dataops: Transform
        #
        self.go_to_transform()
        self.body_ss('dataops_transform_list.png')

        # Click to run test_plugin_1
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'test_plugin_1')
        element.find_element_by_link_text('Run').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Picture of the body
        self.body_ss('dataops_transformation_run.png')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_table(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Table
        #
        self.go_to_table()

        # Picture of the body
        self.body_ss('table.png')

        # Picture of the buttons
        self.element_ss("//div[@id='table-content']/div[1]",
                        'table_buttons.png')

        #
        # Table Views
        #
        self.go_to_table_views()

        # Picture of the body
        self.body_ss('table_views.png')

        #
        # Specific table view
        #
        element = self.search_table_row_by_string('view-table', 1, 'Midterm')
        element.find_element_by_xpath('td[4]/div/a').click()
        self.wait_for_datatable('table-data_previous')

        # Picture of the body
        self.body_ss('table_view_view.png')

        # Click edit view definition
        self.go_to_table_views()
        element = self.search_table_row_by_string('view-table', 1, 'Midterm')
        element.find_element_by_xpath(
            "td//button[normalize-space()='More']"
        ).click()
        element.find_element_by_xpath(
            "td//button[normalize-space()='Edit']"
        ).click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('table_view_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_action(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Actions
        #
        self.go_to_actions()
        self.body_ss('actions.png')

        #
        # Edit Action In
        #
        self.open_action_edit('Student comments Week 1')

        # Picture of the body
        self.body_ss('action_edit_action_in.png')

        #
        # Run Action In
        #
        self.selenium.find_element_by_xpath(
            "//a[normalize-space()='Run']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'actioninrun-data_previous')
            )
        )

        # Picture of the body
        self.body_ss('action_run_action_in.png')

        #
        # Enter data manually
        #
        self.selenium.find_element_by_xpath(
            "//table[@id='actioninrun-data']/tbody/tr[1]/td[1]/a"
        ).click()
        self.wait_for_page(title='OnTask :: Enter Data')

        # Picture of the body
        self.body_ss('action_enter_data_action_in.png')

        #
        # Action In URL enable
        #
        self.go_to_actions()
        element = self.search_action('Student comments Week 1')
        element.find_element_by_xpath(
            "td[5]/div/button[1]"
        ).click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('action_action_in_URL.png')

        # click in the OK button to return
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        # MODAL WAITING
        self.wait_for_datatable('action-table_previous')

        #
        # Edit Action Out
        #
        self.open_action_edit(
            'Comments about how to prepare the lecture (Week 4)'
        )

        # Picture of the body
        self.body_ss('action_edit_action_out.png')

        #
        # Edit filter in action out
        #
        self.selenium.find_element_by_class_name('js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            element_has_full_opacity((By.XPATH, "//div[@id='modal-item']"))
        )

        # Take picture of the modal
        self.modal_ss('action_action_out_edit_filter.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # Editor parts of action out
        #
        self.element_ss("//h4[@id='filter-set']",
                        'action_action_out_filterpart.png')

        # Take picture of the condition set
        self.element_ss("//div[@id='condition-set']",
                        'action_action_out_conditionpart.png')

        # Take picture of the html editor
        self.element_ss("//div[@id='html-editor']",
                        'action_action_out_editorpart.png')

        #
        # Action row
        #
        self.go_to_actions()

        # Picture of the action row
        self.element_ss(
            "//table[@id='action-table']/tbody/tr[3]",
            'action_action_ops.png'
        )

        #
        # Send emails
        #
        self.open_action_email('Midterm comments')

        # Picture of the body
        self.body_ss('action_email_request_data.png')

        #
        # Action URL
        #
        self.go_to_actions()
        element = self.search_table_row_by_string('action-table',
                                                  1,
                                                  'Midterm comments')
        element.find_element_by_xpath("td[5]/div/button[1]").click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('action_URL_on.png')

        # click in the OK button to return
        self.selenium.find_element_by_xpath(
            "//button[@type='submit']"
        ).click()
        self.wait_close_modal_refresh_table('action-table_previous')

        # End of session
        self.logout()

        # Close the db_engine
        # pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_scheduler(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Actions
        #
        self.go_to_actions()

        #
        # Open Action Schedule
        #
        self.open_action_schedule('Midterm comments')

        # Fill out some fields
        self.selenium.find_element_by_id('id_name').send_keys(
            'Send Emails after week 3'
        )
        Select(self.selenium.find_element_by_id(
            'id_item_column')
        ).select_by_visible_text('email')
        dt_widget = self.selenium.find_element_by_xpath(
            "//input[@id='id_execute']"
        )
        self.selenium.execute_script(
            "arguments[0].value = '2110-07-05 17:30:51';",
            dt_widget
        )
        self.selenium.find_element_by_id('id_subject').send_keys(
            'Your preparation activities for the week'
        )
        self.selenium.find_element_by_id('id_track_read').click()

        # Take picture of the export page.
        self.body_ss('schedule_action_email.png')

        # Click the schedule button
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page(title='OnTask :: Action scheduled')

        #
        # Scheduler
        #
        self.go_to_scheduler()

        # Take picture of the export page.
        self.body_ss('schedule.png')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)

    def test_ss_logs(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Logs
        #
        self.go_to_logs()

        # Take picture of the body
        self.body_ss('logs.png')

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
