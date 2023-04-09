"""Create screen captures to include in the documentation."""
import os

from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ontask import models, tests


class ScreenTutorialTest(tests.ScreenTests):

    def test(self):
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
        self.selenium.find_element(
            By.CLASS_NAME,
            'js-create-workflow').click()
        self.wait_for_modal_open()

        self.selenium.find_element(
            By.ID,
            'id_name').send_keys(self.workflow_name)
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        desc.send_keys(self.description)

        # Take capture of the modal
        self.modal_ss('workflow_create.png')

        # Close the modal.
        desc.send_keys(Keys.RETURN)
        self.wait_for_modal_close()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@id='dataops-table']")
            )
        )

        self.body_ss('dataops_datauploadmerge2.png')
        # End of session
        self.logout()


class ScreenImportTest(tests.ScreenTests):

    def test(self):
        """
        Create a workflow, upload data and merge
        :return:
        """

        # Login
        self.login('instructor01@bogus.com')

        # Open Import page
        self.selenium.find_element(By.LINK_TEXT, 'Import workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Import workflow')
        )

        #
        # Import workflow
        #
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            self.workflow_name
        )
        self.selenium.find_element(By.ID, 'id_wf_file').send_keys(
            os.path.join(settings.BASE_DIR(), 'initial_workflow.gz')
        )

        # Picture of the body
        self.body_ss('workflow_import.png')

        # Click the import button
        self.selenium.find_element(
            By.XPATH,
            "//form/div/button[@type='Submit']"
        ).click()
        self.wait_for_page(title='OnTask :: Workflows')

        # End of session
        self.logout()


class ScreenTestFixtureBasic(
    tests.InitialWorkflowFixture,
    tests.ScreenTests,
):
    pass
    # def setUp(self):
    #     super().setUp()
    #     # Insert a SQL Connection
    #     sqlc = SQLConnection(
    #         name='remote server',
    #         description_text='Server with student records',
    #         conn_type='mysql',
    #         conn_driver='',
    #         db_user='remote_db_user',
    #         db_password=True,
    #         db_host='dbserver.bogus.com',
    #         db_port=None,
    #         db_name='demographics',
    #         db_table='s_records'
    #     )
    #     sqlc.save()
    #
    #     # Insert an Amazon Athena Connection
    #     athenac = AthenaConnection(
    #         name='athena connection',
    #         description_text='Connection to amazon athena server',
    #         aws_access_key='[YOUR AWS ACCESS KEY HERE]',
    #         aws_secret_access_key='[YOUR AWS SECRET ACCESS KEY HERE]',
    #         aws_bucket_name='[S3 BUCKET NAME HERE]',
    #         aws_file_path='[FILE PATH WITHIN BUCKET HERE]',
    #         aws_region_name='[AWS REGION NAME HERE]',
    #     )
    #     athenac.save()
    #


class ScreenTestSQLAdmin(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('superuser@bogus.com')
        self.body_ss('workflow_superuser_index.png')

        #
        # Open SQL Connection
        #
        self.go_to_sql_connections()
        self.body_ss('workflow_sql_connections_index.png')

        # click on the edit element
        self.selenium.find_element(
            By.XPATH,
            '//table[@id="connection-admin-table"]'
            '//tr/td[2][normalize-space() = "remote server"]/'
            '../td[1]/div/button[1]'
        ).click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('workflow_superuser_sql_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()

    # def test_athena_admin(self):
    #     # Login
    #     self.login('superuser@bogus.com')
    #
    #     #
    #     # Open Athena Connection
    #     #
    #     self.go_to_athena_connections()
    #     self.body_ss('workflow_athena_connections_index.png')
    #
    #     # click on the edit element
    #     self.selenium.find_element(
    #         By.XPATH,
    #         "//table[@id='connection-admin-table']"
    #         "//tr/td[1][normalize-space() = 'athena connection']"
    #     ).click()
    #     self.wait_for_modal_open()
    #
    #     # Take picture of the modal
    #     self.modal_ss('workflow_superuser_athena_edit.png')
    #
    #     # Click in the cancel button
    #     self.cancel_modal()
    #
    #     # End of session
    #     self.logout()
    #
    #     # Close the db_engine
    #     destroy_db_engine()


class ScreenTestWorkflow(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # List of workflows, navigation
        self.body_ss('workflow_index.png')

        # Workflow card
        self.element_ss(
            '//div[contains(@class, "ontask-card")]',
            'workflow_card.png')
        #
        # Navigation bar, details
        #
        self.access_workflow_from_home_page(self.workflow_name)

        # Take picture of the navigation bar
        self.element_ss("//body/div[@id='wflow-name']", 'navigation_bar.png')

        #
        # New column modal
        #
        self.go_to_details()
        self.body_ss('workflow_details.png')
        self.open_add_regular_column()
        self.modal_ss('workflow_add_column.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # Attributes
        #
        self.go_to_attribute_page()
        self.body_ss('workflow_attributes.png')

        #
        # Share
        #
        self.go_to_workflow_share()
        self.body_ss('workflow_share.png')

        #
        # EXPORT
        #
        self.go_to_workflow_export()
        self.body_ss('workflow_export.png')

        # Click back to the details page
        self.selenium.find_element(
            By.XPATH,
            "//a[normalize-space()='Cancel']"
        ).click()
        self.wait_for_id_and_spinner('attribute-table_previous')

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


class ScreenTestDetails(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        # Go to workflow details
        self.go_to_details()

        #
        # Ops/Edit Column
        #
        self.open_column_edit('SID')
        self.wait_for_modal_open()
        self.modal_ss('workflow_column_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()


class ScreenTestDataops(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        # Go to CSV
        self.go_to_upload_merge()
        self.body_ss('dataops_datauploadmerge.png')

        self.selenium.find_element(By.LINK_TEXT, "CSV").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )
        self.selenium.find_element(By.ID, 'id_data_file').send_keys(
            os.path.join(
                settings.BASE_DIR(),
                'ontask',
                'tests',
                'initial_workflow',
                'initial_workflow.csv')
        )

        # Picture of the body
        self.body_ss('dataops_csvupload.png')

        #
        # Dataops/Merge CSV Merge Step 2
        #
        # Click the NEXT button
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='id_make_key_2']")
            )
        )
        # Uncheck the columns that won't be keys
        col_checks = self.selenium.find_elements(
            By.XPATH,
            '//input[contains(@id, "id_make_key_")]')
        for col_check in col_checks[1:]:
            # Bring element until the middle of the page
            self.scroll_element_into_view(col_check)
            col_check.click()
        self.selenium.execute_script("window.scroll(0,0);")

        # Picture of the body
        self.body_ss('dataops_upload_merge_step2.png')

        #
        # Dataops/Merge CSV Merge Step 3
        #
        # Click the NEXT button
        submit_button = self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        )
        self.selenium.execute_script(
            "arguments[0].scrollIntoView("
            "{block: 'center', inline: 'nearest', behavior: 'instant'});",
            submit_button)
        WebDriverWait(self.selenium, 10).until(EC.visibility_of(submit_button))
        submit_button.click()
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
        Select(self.selenium.find_element(
            By.ID,
            'id_how_merge'
        )).select_by_value('left')

        # Picture of the body
        self.body_ss('dataops_upload_merge_step3.png')

        # Click the NEXT button
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"), 'Review and confirm')
        )

        # Picture of the body
        self.body_ss('dataops_upload_merge_step4.png')

        # Click on Finish
        submit_button = self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Finish']"
        )
        self.scroll_element_into_view(submit_button)
        submit_button.click()
        self.wait_for_id_and_spinner('table-data_previous')

        #
        # Dataops/Merge Excel Merge
        #
        # Go to Excel Upload/Merge
        self.go_to_excel_upload_merge_step_1()
        self.body_ss('dataops_upload_excel.png')
        self.go_to_table()
        #
        # Google doc merge
        #
        # Go to Excel Upload/Merge
        self.go_to_google_sheet_upload_merge_step_1()
        self.body_ss('dataops_upload_gsheet.png')
        self.go_to_table()

        #
        # S3 CSV merge
        #
        self.go_to_s3_upload_merge_step_1()
        self.body_ss('dataops_upload_s3.png')
        self.go_to_table()

        #
        # Dataops/Merge SQL Connection
        #
        self.go_to_sql_upload_merge()
        self.body_ss('dataops_SQL_available.png')

        # Click on the link RUN
        element = self.search_table_row_by_string(
            'conn-instructor-table',
            1,
            'remote server')
        element.find_element(By.XPATH, 'td[1]/a').click()
        self.wait_for_page(None, 'sql-load-step1')

        # Picture of the RUN menu in SQL
        self.body_ss('dataops_SQL_run.png')
        self.go_to_table()

        #
        # Dataops/Merge Athena Connection
        #
        # self.go_to_athena_upload_merge()
        # self.body_ss('dataops_athena_available.png')
        #
        # # Click on the link RUN
        # self.selenium.find_element(By.LINK_TEXT, 'Run').click()
        # self.wait_for_page(None, 'athena-load-step1')
        #
        # # Picture of the RUN menu in Athena
        # self.body_ss('dataops_athena_run.png')

        # Go back to details
        self.go_to_details()

        #
        # Dataops: Transform
        #
        self.go_to_transform()
        self.body_ss('dataops_transform_list.png')

        # Click to run test_plugin_1
        element = self.search_table_row_by_string(
            'transform-table',
            1,
            'Test Plugin 1 Name')
        element.find_element(By.XPATH, 'td[1]/a').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Picture of the body
        self.body_ss('dataops_transformation_run.png')

        #
        # Dataops: Model
        #
        self.go_to_model()
        self.body_ss('dataops_model_list.png')

        # Click to run linear model
        element = self.search_table_row_by_string(
            'transform-table',
            1,
            'Linear Model')
        element.find_element(By.XPATH, 'td[1]/a').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Picture of the body
        self.body_ss('dataops_model_run.png')

        # End of session
        self.logout()


class ScreenTestTable(ScreenTestFixtureBasic):

    def test(self):
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
        self.element_ss(
            '//div[@id="table-operation-buttons"]',
            'table_buttons.png')

        #
        # Table Views
        #
        self.selenium.find_element(By.ID, 'select-view-name').click()

        # Picture of the body
        self.body_ss('table_views.png')

        #
        # Specific table view
        #
        self.open_view('Midterm')

        # Picture of the body
        self.body_ss('table_view_view.png')

        # Click edit view definition
        self.selenium.find_element(
            By.XPATH,
            '//button[contains(@class, "js-view-edit")]').click()
        self.wait_for_modal_open()

        # Take picture of the modal
        self.modal_ss('table_view_edit.png')

        # Click in the cancel button
        self.cancel_modal()

        # End of session
        self.logout()


class ScreenTestAction(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Actions
        #
        self.body_ss('actions.png')

        #
        # Edit Action In
        #
        self.open_action_edit('Student comments Week 1', 'parameters')

        # Picture of the body
        self.body_ss('action_edit_action_in.png')

        # Open the "Create question modal"
        self.select_tab('conditions-tab')
        self.create_condition(
            'Full time',
            '',
            [('Attendance', 'equal', 'Full Time')]
        )

        # Open the "Create question modal"
        self.select_tab('questions-tab')
        self.body_ss('action_edit_action_in_question_tab.png')

        self.selenium.find_element(
            By.XPATH,
            "//button[contains(@class, 'js-action-question-add')]").click()
        self.wait_for_modal_open()
        self.modal_ss("action_edit_action_in_create_question.png")
        self.cancel_modal()

        # Open the Survey Parameters
        self.select_tab('parameters-tab')
        self.body_ss('action_edit_action_in_parameters.png')

        # Open the preview
        self.open_preview()
        self.modal_ss('action_action_in_preview.png')
        self.cancel_modal()

        # Done
        # Submit the action
        self.selenium.find_element(By.LINK_TEXT, 'Done').click()
        self.wait_for_id_and_spinner('action-index')

        #
        # Run Action In
        #
        self.open_action_run('Student comments Week 1', True)

        # Picture of the body
        self.body_ss('action_run_action_in.png')

        #
        # Enter data manually
        #
        self.selenium.find_element(
            By.XPATH,
            "//table[@id='actioninrun-data']/tbody/tr[1]/td[1]/a"
        ).click()
        self.wait_for_page(title='OnTask :: Enter Data')

        # Picture of the body
        self.body_ss('action_enter_data_action_in.png')

        #
        # Action In URL enable
        #
        self.go_to_actions()
        self.open_action_operation('Student comments Week 1', 'bi-link-45deg')

        # Take picture of the modal
        self.modal_ss('action_action_in_URL.png')

        # click on the OK button to return
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_for_modal_close()

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
        self.select_tab('filter-tab')
        self.selenium.find_element(By.CLASS_NAME, 'js-filter-edit').click()
        # Wait for the form to modify the filter
        WebDriverWait(self.selenium, 10).until(
            tests.ElementHasFullOpacity(
                (By.XPATH, "//div[@id='modal-item']"))
        )

        # Take picture of the modal
        self.modal_ss('action_action_out_edit_filter.png')

        # Click in the cancel button
        self.cancel_modal()

        #
        # Editor parts of action out
        #
        self.body_ss('action_action_out_filterpart.png')

        # Take picture of the condition set
        self.select_tab('conditions-tab')
        self.body_ss('action_action_out_conditionpart.png')

        # Open one of the conditions
        self.open_condition('No Video 1')
        # Take picture of the condition open
        self.modal_ss('action_action_out_edit_condition.png')
        self.cancel_modal()

        # Open the preview
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Preview']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            tests.ElementHasFullOpacity((By.XPATH, "//div[@id='modal-item']"))
        )
        self.modal_ss('action_action_out_preview.png')
        self.cancel_modal()

        #
        # Create a canvas email action
        #
        self.go_to_actions()
        # click on the create action button and create an action
        self.selenium.find_element(By.CLASS_NAME, 'js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            'Initial motivation'
        )
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(models.Action.PERSONALIZED_CANVAS_EMAIL)
        desc.send_keys('Motivating message depending on the program enrolled')

        self.modal_ss('action_personalized_canvas_email_create.png')

        # Cancel creation
        self.cancel_modal()

        # Open the action
        self.open_action_edit('Initial motivation')

        self.body_ss('action_personalized_canvas_email_edit.png')

        # Save action and back to action index
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_id_and_spinner('action-index')

        #
        # SEND LIST action
        #
        # click on the create action button and create an action
        self.selenium.find_element(By.CLASS_NAME, 'js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            'Send Email with report'
        )
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(models.Action.EMAIL_REPORT)
        desc.send_keys('Send email with column values as list')

        self.modal_ss('action_email_report_create.png')

        # Cancel creation
        self.cancel_modal()

        # Open the action
        self.open_action_edit('Send Email with report')
        self.body_ss('action_email_report_edit.png')

        self.select_tab('attachments-tab')
        self.body_ss('action_email_report_attachments.png')

        self.open_preview()
        self.modal_ss('action_email_report_preview.png')
        self.cancel_modal()

        # Save action and back to action index
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_id_and_spinner('action-index')

        #
        # SEND JSON REPORT action
        #
        # click on the create action button and create an action
        self.selenium.find_element(By.CLASS_NAME, 'js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            'Send JSON report'
        )
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(models.Action.JSON_REPORT)
        desc.send_keys(
            'Send the list of inactive students '
            'in week 2 to another platform')

        self.modal_ss('action_json_report_create.png')

        # Cancel creation
        self.cancel_modal()

        # Open the action
        self.open_action_edit('Send JSON report')
        self.body_ss('action_json_report_edit.png')
        self.open_preview()
        self.modal_ss('action_json_report_preview.png')
        self.cancel_modal()

        # Save action and back to action index
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_id_and_spinner('action-index')

        # Picture of Canvas scheduling
        # self.open_action_schedule('Send Canvas reminder')
        # self.body_ss('scheduler_action_canvas_email.png')
        # self.go_to_actions()

        # Picture of the action row
        self.element_ss(
            '//div[@id="action-cards"]//'
            'h5[normalize-space()="Midterm comments"]/..',
            'action_action_ops.png')

        #
        # Send emails
        #
        self.open_action_edit('Midterm comments')

        # Picture of the body
        self.body_ss('action_email_request_data.png')

        self.go_to_actions()
        self.open_action_edit('Initial motivation')

        # Picture of the body
        self.body_ss('action_personalized_canvas_email_run.png')

        #
        # Create ZIP
        #
        self.go_to_actions()
        self.open_action_operation(
            'Midterm comments',
            'bi-file-earmark-zip-fill',
            'zip-action-request-data')

        # Picture of the body
        self.body_ss('action_zip_request_data.png')

        #
        # JSON Edit
        #
        self.go_to_actions()
        self.open_action_edit('Send JSON to remote server')
        self.body_ss('action_personalized_json_edit.png')
        # Save action and back to action index
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Close']"
        ).click()
        self.wait_for_id_and_spinner('action-index')

        #
        # JSON RUN
        #
        self.open_action_json_run('Send JSON to remote server')
        self.body_ss('action_json_run_request_data.png')
        # Save action and back to action index
        self.selenium.find_element(By.LINK_TEXT, 'Cancel').click()
        self.wait_for_id_and_spinner('action-index')

        #
        # Action URL
        #
        self.open_action_operation('Midterm comments', 'bi-link-45deg')

        # Take picture of the modal
        self.modal_ss('action_URL_on.png')

        # click on the OK button to return
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='submit']"
        ).click()
        self.wait_close_modal_refresh_table('action-index')

        # End of session
        self.logout()


class ScreenTestScheduler(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        #
        # Open Action Schedule and schedule the Personalized Text action
        #
        self.open_action_operation(
            'Midterm comments',
            'bi-calendar',
            'email-schedule-send')

        # Fill out some fields
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            'Send Emails after week 3'
        )
        Select(self.selenium.find_element(
            By.ID,
            'id_item_column')
        ).select_by_visible_text('email')
        dt_widget = self.selenium.find_element(
            By.XPATH,
            "//input[@id='id_execute']"
        )
        dt_widget.clear()
        dt_widget.send_keys('2110-07-05 17:30:51')
        self.selenium.find_element(By.ID, 'id_subject').send_keys(
            'Your preparation activities for the week'
        )
        self.selenium.find_element(By.ID, 'id_track_read').click()

        # Take picture of the export page.
        self.body_ss('schedule_action_email.png')

        # Click the schedule button
        self.selenium.find_element(
            By.XPATH,
            "//button[@id='next-step-off']"
        ).click()
        self.wait_for_page(title='OnTask :: Operation scheduled')

        #
        # Actions
        #
        self.go_to_actions()

        #
        # Open Action Schedule and schedule the Personalized JSON
        #
        self.open_action_operation(
            'Send JSON to remote server',
            'bi-calendar',
            'email-schedule-send')

        # Fill out some fields
        self.selenium.find_element(By.ID, 'id_name').send_keys(
            'Send JSON object in Week 5'
        )
        Select(self.selenium.find_element(
            By.ID,
            'id_item_column')
        ).select_by_visible_text('email')
        dt_widget = self.selenium.find_element(
            By.XPATH,
            "//input[@id='id_execute']"
        )
        dt_widget.clear()
        dt_widget.send_keys('2110-07-25 17:00:00')

        self.selenium.find_element(By.ID, 'id_token').send_keys(
            'afabkvaidlfvsidkfe..kekfioroelallasifjjf;alksid'
        )

        # Take picture of the export page.
        self.body_ss('schedule_action_json.png')

        # Click the schedule button
        self.selenium.find_element(
            By.XPATH,
            "//button[@id='next-step-off']"
        ).click()
        self.wait_for_page(title='OnTask :: Operation scheduled')

        #
        # Scheduler
        #
        self.go_to_scheduler()

        # Take picture of the export page.
        self.body_ss('schedule.png')

        # End of session
        self.logout()


class ScreenTestLogs(ScreenTestFixtureBasic):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # Open Workflows page
        self.access_workflow_from_home_page(self.workflow_name)

        self.go_to_attribute_page()
        self.create_attribute('akey', 'avalue')

        # Logs
        self.go_to_logs()

        # Take picture of the body
        self.body_ss('logs.png')

        # End of session
        self.logout()


class ScreenTestRubric(ScreenTestFixtureBasic):

    def test(self):
        action_name = 'Project feedback'
        # Login
        self.login('instructor01@bogus.com')

        self.access_workflow_from_home_page(self.workflow_name)

        self.go_to_actions()

        # click on the create action button
        self.selenium.find_element(By.CLASS_NAME, 'js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(action_name)
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        desc.send_keys(
            'Provide feedback about the project using the results '
            + 'from the rubric')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(models.Action.RUBRIC_TEXT)
        self.modal_ss('rubric_create.png')
        self.cancel_modal()

        # Open the action
        self.open_action_edit(action_name)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "tox-edit-area")]')
            )
        )
        self.body_ss('rubric_edit_text.png')

        # Go to the rubric tab
        self.select_tab('rubric-tab')
        self.body_ss('rubric_edit_table_tab.png')

        # Preview
        self.open_preview()
        self.modal_ss('rubric_preview.png')
        self.cancel_modal()

        # End of session
        self.logout()
