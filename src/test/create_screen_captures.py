# -*- coding: utf-8 -*-


from future import standard_library

from action.models import Action

standard_library.install_aliases()
import os

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db
from test import ElementHasFullOpacity, ScreenTests

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
        self.wait_for_modal_close()

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
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
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
        xpath_txt = \
            "//table[@id='sqlconn-admin-table']" \
            "//tr/td[1][text() = '{0}']/..".format('Remote server')
        # Click in the dropdown
        self.open_dropdown_click_option(
            xpath_txt + "/td[1]/div/button",
            'Edit'
        )

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
        self.element_ss("//body/div[@id='wflow-name']", 'navigation_bar.png')

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
                (By.XPATH, "//body/div/h1"),
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

        # Open the preview
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Preview']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )
        self.modal_ss('action_action_in_preview.png')
        self.cancel_modal()

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
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
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

        # Open the preview
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Preview']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )
        self.modal_ss('action_action_out_preview.png')
        self.cancel_modal()

        #
        # Create a canvas email action
        #
        self.go_to_actions()
        # click in the create action button and create an action
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys(
            'Send Canvas reminder'
        )
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(Action.PERSONALIZED_CANVAS_EMAIL)
        desc.send_keys('Week 3 reminder to review material')

        self.modal_ss('action_personalized_canvas_email_create.png')

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

        self.create_filter('No activity in Week 2',
                           '',
                           [('Days online 2', 'equal', '0')])
        self.selenium.find_element_by_id('id_content').send_keys(
            """Dear {{ GivenName }}

We recommend that you review the discussions in the online forum about the topics we are going to cover this week

Regards

John Doe
Course Coordinator""")
        self.body_ss('action_personalized_canvas_email_edit.png')

        # Save action and back to action index
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Save']"
        ).click()
        self.wait_for_datatable('action-table_previous')

        #
        # Back to the table of actions
        #
        self.go_to_actions()

        # Picture of the action row
        self.element_ss(
            "//table[@id='action-table']/tbody/tr/td[normalize-space("
            ")='Midterm comments']/..",
            'action_action_ops.png'
        )

        #
        # Send emails
        #
        self.open_action_email('Midterm comments')

        # Picture of the body
        self.body_ss('action_email_request_data.png')

        self.go_to_actions()
        self.open_action_canvas_email('Send Canvas reminder')

        # Picture of the body
        self.body_ss('action_personalized_canvas_email_run.png')

        #
        # Create ZIP
        #
        self.go_to_actions()
        self.open_action_zip('Midterm comments')

        # Picture of the body
        self.body_ss('action_zip_request_data.png')

        #
        # JSON Edit
        #
        self.go_to_actions()
        self.open_action_edit('Send JSON to remote server')
        self.body_ss('action_personalized_json_edit.png')

        #
        # JSON RUN
        #
        self.go_to_actions()
        self.open_action_json_run('Send JSON to remote server')
        self.body_ss('action_json_run_request_data.png')

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
        # Open Action Schedule and schedule the Personalized Text action
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
        # Actions
        #
        self.go_to_actions()

        #
        # Open Action Schedule and schedule the Personalized JSON
        #
        self.open_action_schedule('Send JSON to remote server')

        # Fill out some fields
        self.selenium.find_element_by_id('id_name').send_keys(
            'Send JSON object in Week 5'
        )
        dt_widget = self.selenium.find_element_by_xpath(
            "//input[@id='id_execute']"
        )
        self.selenium.execute_script(
            "arguments[0].value = '2110-07-25 17:00:00';",
            dt_widget
        )
        self.selenium.find_element_by_id('id_token').send_keys(
            'afabkvaidlfvsidkfe..kekfioroelallasifjjf;alksid'
        )

        # Take picture of the export page.
        self.body_ss('schedule_action_json.png')

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
