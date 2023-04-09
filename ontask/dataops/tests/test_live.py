"""Test live execution of dataops views.s"""
import os

from django.conf import settings
from django.utils.html import escape
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ontask import models, tests
from ontask.core import ONTASK_UPLOAD_FIELD_PREFIX
from ontask.dataops import pandas, sql


class DataopsSymbols1(tests.WflowSymbolsFixture, tests.OnTaskLiveTestCase):

    def test(self):
        symbols = '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # Open the workflow
        self.access_workflow_from_home_page('wflow1')

        # Go to the column details
        self.go_to_details()

        # Edit the name column
        self.open_column_edit('name')

        # Replace name by symbols
        self.selenium.find_element(By.ID, "id_name").click()
        self.selenium.find_element(By.ID, "id_name").clear()
        self.selenium.find_element(By.ID, "id_name").send_keys(symbols)

        # Click in the submit/save button
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click on the Add Column button
        self.open_add_regular_column()

        # Set name to symbols (new column) and type to string
        self.selenium.find_element(By.ID, "id_name").click()
        self.selenium.find_element(By.ID, "id_name").clear()
        self.selenium.find_element(By.ID, "id_name").send_keys(symbols)
        self.selenium.find_element(By.ID, "id_data_type").click()
        Select(self.selenium.find_element(
            By.ID,
            "id_data_type"
        )).select_by_visible_text("string")

        # Save the new column
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'error_1_id_name')))

        # There should be a message saying that the name of this column already
        # exists
        self.assertIn(
            'There is a column already with this name',
            self.selenium.page_source)

        # Click again in the name and introduce something different
        self.selenium.find_element(By.ID, "id_name").click()
        self.selenium.find_element(By.ID, "id_name").clear()
        self.selenium.find_element(By.ID, "id_name").send_keys(symbols + '2')

        # Save the new column
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click in the attributes section
        self.go_to_attribute_page()

        # Delete the existing one and confirm deletion
        # click the delete button in the second row
        self.selenium.find_element(
            By.XPATH,
            '//table[@id="attribute-table"]'
            '//tr[1]/td[1]//button[contains(@class, "js-attribute-delete")]'
        ).click()
        self.wait_for_modal_open()

        # Click in the delete confirm button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id = 'modal-item']//div[@class = 'modal-footer']/button"
        ).click()

        # MODAL WAITING
        self.wait_for_page(element_id='workflow-detail')

        # Add a new attribute and insert key (symbols) and value
        self.create_attribute(symbols + '3', 'vvv')

        # Click in the TABLE link
        self.go_to_table()

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn(escape(symbols + '2'), self.selenium.page_source)

        # Click in the Actions navigation menu
        self.go_to_actions()

        # Edit the action-in
        self.open_action_edit('action in', 'parameters')

        # Go to questions
        self.select_tab('questions-tab')

        # Set the right columns to process
        self.click_dropdown_option(
            'column-selector',
            '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~2'
        )
        self.wait_for_id_and_spinner('column-selected-table_previous')
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )

        # Set some parameters
        self.select_tab('parameters-tab')
        self.click_dropdown_option('select-key-column-name', 'sid')
        self.wait_for_spinner()
        self.select_tab('parameters-tab')
        self.click_dropdown_option('select-key-column-name', 'email')
        self.wait_for_spinner()

        # Save action-in
        self.select_tab('questions-tab')
        self.selenium.find_element(By.LINK_TEXT, 'Done').click()
        self.wait_for_id_and_spinner('action-index')

        # Click in the link to enable the URL for the action
        self.open_action_operation('action in', 'fa-link')
        self.assertIn(
            'This URL provides access to the content personalised',
            self.selenium.page_source)

        # Click to Enable the URL
        self.selenium.find_element(By.ID, 'id_serve_enabled').click()

        # Click OK
        self.selenium.find_element(
            By.CSS_SELECTOR,
            'div.modal-footer > button.btn.btn-outline-primary'
        ).click()

        # close modal
        self.wait_for_modal_close()

        # Click in the RUN link of the action in
        self.open_action_run('action in', is_action_in=True)

        # Enter data using the RUN menu. Select one entry to populate
        self.selenium.find_element(By.LINK_TEXT, "student01@bogus.com").click()
        self.wait_for_page(element_id='action-row-datainput')
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '1')
        field.click()
        field.clear()
        field.send_keys('17')
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '2')
        field.click()
        field.clear()
        field.send_keys('Carmelo Coton2')
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '3')
        field.click()
        field.clear()
        field.send_keys('xxx')

        # Submit the data for one entry
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='action-row-datainput']//form//button").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'actioninrun-data_previous'))
        )

        # Go Back to the action table
        self.go_to_actions()

        # Edit the action out
        self.open_action_edit('action_out')

        # Click in the editor
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'tox-edit-area')
            )
        )
        self.selenium.find_element(By.CLASS_NAME, 'tox-edit-area').click()

        # Insert attribute
        self.click_dropdown_option('attribute-selector', symbols + '3')

        # Insert column name
        self.click_dropdown_option('column-selector', symbols)

        # Insert second column name
        self.click_dropdown_option('column-selector', symbols + '2')

        # Create new condition
        self.create_condition(
            symbols + "4",
            '',
            [(symbols, "begins with", "C")])

        # Create the filter
        self.create_filter('', [(symbols + "2", "doesn't begin with", "x")])

        # Click the preview button
        self.select_tab('text-tab')
        self.selenium.find_element(By.CLASS_NAME, 'js-action-preview').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-action-preview-nxt'))
        )

        # Certain name should be in the page now.
        self.assertIn('Carmelo Coton', self.selenium.page_source)

        # Click in the "Close" button
        self.selenium.find_element(
            By.XPATH,
            "//div[@id='modal-item']/div/div/div/div[2]/button[2]").click()

        # End of session
        self.logout()


class DataopsSymbols2(tests.WflowSymbolsFixture, tests.OnTaskLiveTestCase):

    def test(self):
        symbols = '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1')

        # Go to column details
        self.go_to_details()

        # Edit the email column
        self.open_column_edit('email')

        # Append symbols to the name
        self.selenium.find_element(By.ID, "id_name").click()
        self.selenium.find_element(By.ID, "id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Select the age column and click on the edit button
        self.open_column_edit('age')

        # Append symbols to the name
        self.selenium.find_element(By.ID, "id_name").click()
        self.selenium.find_element(By.ID, "id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Go to the table link
        self.go_to_table()

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn(
            '<td class=" dt-center">12</td>',
            self.selenium.page_source)
        self.assertIn(
            '<td class=" dt-center">12.1</td>',
            self.selenium.page_source)
        self.assertIn(
            '<td class=" dt-center">13.2</td>',
            self.selenium.page_source)

        # Go to the actions page
        self.go_to_actions()

        # Edit the action-in at the top of the table
        self.open_action_edit('action in', 'parameters')

        # Set the correct values for an action-in
        # Set the right columns to process
        self.select_tab('parameters-tab')
        self.click_dropdown_option('select-key-column-name', 'email' + symbols)
        # This wait is incorrect. Don't know how to wait for an AJAX call.
        self.wait_for_spinner()

        # Done editing the action in
        self.select_tab('questions-tab')
        self.selenium.find_element(By.LINK_TEXT, 'Done').click()
        self.wait_for_id_and_spinner('action-index')

        # Click in the run link
        self.open_action_run('action in', True)

        # Click on the first value
        self.selenium.find_element(By.LINK_TEXT, "student01@bogus.com").click()

        # Modify the value of the column
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '1')
        field.click()
        field.clear()
        field.send_keys('14')

        # Submit changes to the first element
        self.selenium.find_element(
            By.XPATH,
            "(//button[@name='submit'])[1]"
        ).click()
        self.wait_for_id_and_spinner('actioninrun-data_previous')

        # Click on the second value
        self.selenium.find_element(By.LINK_TEXT, "student02@bogus.com").click()

        # Modify the value of the columne
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '1')
        field.click()
        field.clear()
        field.send_keys('15')

        # Submit changes to the second element
        self.selenium.find_element(
            By.XPATH,
            "(//button[@name='submit'])[1]"
        ).click()
        self.wait_for_id_and_spinner('actioninrun-data_previous')

        # Click on the third value
        self.selenium.find_element(By.LINK_TEXT, "student03@bogus.com").click()

        # Modify the value of the column
        field = self.selenium.find_element(
            By.ID,
            'id_' + ONTASK_UPLOAD_FIELD_PREFIX + '1')
        field.click()
        field.clear()
        field.send_keys('16')

        # Submit changes to the second element
        self.selenium.find_element(
            By.XPATH,
            "(//button[@name='submit'])[1]"
        ).click()
        self.wait_for_id_and_spinner('actioninrun-data_previous')

        # Click in the back link!
        self.selenium.find_element(By.LINK_TEXT, 'Back').click()
        self.wait_for_id_and_spinner('action-index')

        # Go to the table page
        self.go_to_table()

        # Assert the new values
        self.assertIn(
            '<td class=" dt-center">14</td>',
            self.selenium.page_source)
        self.assertIn(
            '<td class=" dt-center">15</td>',
            self.selenium.page_source)
        self.assertIn(
            '<td class=" dt-center">16</td>',
            self.selenium.page_source)

        # End of session
        self.logout()


class DataopsExcelUpload(tests.EmptyWorkflowFixture, tests.OnTaskLiveTestCase):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1')

        # Go to Excel upload/merge
        self.go_to_excel_upload_merge_step_1()

        # Upload file
        self.selenium.find_element(By.ID, "id_data_file").send_keys(
            os.path.join(settings.ONTASK_FIXTURE_DIR, 'excel_upload.xlsx')
        )
        self.selenium.find_element(By.ID, "id_sheet").click()
        self.selenium.find_element(By.ID, "id_sheet").clear()
        self.selenium.find_element(By.ID, "id_sheet").send_keys("results")
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'checkAll'))
        )
        self.wait_for_spinner()
        self.selenium.find_element(By.NAME, "Submit").click()
        self.wait_for_id_and_spinner('table-data_previous')

        # The number of rows must be 29
        wflow = models.Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 29)
        self.assertEqual(wflow.ncols, 14)

        # End of session
        self.logout()


class DataopsExcelUploadSheet(
    tests.EmptyWorkflowFixture,
    tests.OnTaskLiveTestCase,
):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1')

        # Go to Excel upload/merge
        self.go_to_excel_upload_merge_step_1()

        # Upload the file
        self.selenium.find_element(By.ID, "id_data_file").send_keys(
            os.path.join(settings.ONTASK_FIXTURE_DIR, 'excel_upload.xlsx')
        )
        self.selenium.find_element(By.ID, "id_sheet").click()
        self.selenium.find_element(By.ID, "id_sheet").clear()
        self.selenium.find_element(By.ID, "id_sheet").send_keys("second sheet")
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'checkAll'))
        )
        self.selenium.find_element(By.NAME, "Submit").click()
        self.wait_for_id_and_spinner('table-data_previous')

        # The number of rows must be 19
        wflow = models.Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 19)
        self.assertEqual(wflow.ncols, 14)

        # End of session
        self.logout()


class DataopsNaNProcessing(
    tests.EmptyWorkflowFixture,
    tests.OnTaskLiveTestCase,
):
    action_text = "Bool1 = {{ bool1 }}\\n" + \
                  "Bool2 = {{ bool2 }}\\n" + \
                  "Bool3 = {{ bool3 }}\\n" + \
                  "{% if bool1 cond %}Bool 1 is true{% endif %}\\n" + \
                  "{% if bool2 cond %}Bool 2 is true{% endif %}\\n" + \
                  "{% if bool3 cond %}Bool 3 is true{% endif %}\\n"

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        self.create_new_workflow('NaN')

        # Go to CSV Upload/Merge
        self.selenium.find_element(
            By.XPATH,
            "//table[@id='dataops-table']//a[normalize-space()='CSV']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

        # Select file and upload
        self.selenium.find_element(By.ID, "id_data_file").send_keys(
            os.path.join(
                settings.ONTASK_FIXTURE_DIR,
                'test_df_merge_update_df1.csv'))
        self.selenium.find_element(By.NAME, "Submit").click()
        self.wait_for_page()

        # Submit
        self.selenium.find_element(
            By.XPATH,
            "(//button[@name='Submit'])[2]"
        ).click()
        self.wait_for_id_and_spinner('table-data_previous')

        # Select again the upload/merge function
        self.go_to_csv_upload_merge_step_1()

        # Select the second file and submit
        self.selenium.find_element(By.ID, "id_data_file").send_keys(
            os.path.join(
                settings.ONTASK_FIXTURE_DIR,
                'test_df_merge_update_df2.csv')
        )
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Select Columns')
        )

        # Select all the columns for upload
        self.selenium.find_element(By.NAME, "Submit").click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Select Keys and Merge Option')
        )

        # Choose the default options for the merge (key and outer)
        # Select the merger function type
        select = Select(self.selenium.find_element(By.ID, 'id_how_merge'))
        select.select_by_value('outer')
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Review and confirm')
        )

        # Check the merge summary and proceed
        self.selenium.find_element(By.NAME, "Submit").click()
        # Wait for the upload/merge to finish
        self.wait_for_id_and_spinner('table-data_previous')

        # Go to the actions page
        self.go_to_actions()

        # Create a new action
        self.create_new_personalized_text_action("action out", '')

        # Create three conditions
        self.create_condition("bool1 cond", '', [('bool1', 'equal', 'true')])
        self.create_condition("bool 2 cond", '', [('bool2', 'equal', 'true')])
        self.create_condition('bool3 cond', '', [('bool3', 'equal', 'true')])

        # insert the action text
        self.select_tab('text-tab')
        self.selenium.find_element(By.CLASS_NAME, 'tox-edit-area').click()
        self.selenium.execute_script(
            """tinymce.get('id_text_content').execCommand('mceInsertContent', 
            false, "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.open_browse_preview(11)

        # End of session
        self.logout()


class DataopsPluginExecution1(
    tests.PluginExecutionFixture,
    tests.OnTaskLiveTestCase,
):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('Plugin test')

        # Open the transform page
        self.go_to_transform()

        # Click in the first plugin
        element = self.search_table_row_by_string(
            'transform-table',
            1,
            'Test Plugin 1 Name')
        element.find_element(By.LINK_TEXT, 'Test Plugin 1 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))
        )

        # Provide the execution data
        self.selenium.find_element(By.XPATH, "//input[@type='text']").click()
        self.selenium.find_element(By.NAME, "columns").click()
        self.selenium.find_element(
            By.XPATH,
            "(//input[@name='columns'])[2]"
        ).click()

        # Select the merge key
        self.select_tab('outputs-tab')

        self.selenium.find_element(By.ID, "id_merge_key").click()
        Select(self.selenium.find_element(
            By.ID,
            "id_merge_key"
        )).select_by_visible_text("email")

        # Submit the execution
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element(
                By.XPATH,
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name='Plugin test')
        self.assertTrue(
            sql.is_column_in_table(
                wflow.get_data_frame_table_name(),
                'RESULT 1'))
        self.assertTrue(
            sql.is_column_in_table(
                wflow.get_data_frame_table_name(),
                'RESULT 2'))
        df = pandas.load_table(wflow.get_data_frame_table_name())
        self.assertTrue(all([x == 1 for x in df['RESULT 1']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2']]))

        # Second execution, this time adding a suffix to the column
        self.go_to_actions()
        self.go_to_transform()

        # Click in the first plugin
        element = self.search_table_row_by_string(
            'transform-table',
            1,
            'Test Plugin 1 Name')
        element.find_element(By.LINK_TEXT, 'Test Plugin 1 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))
        )

        # Provide the execution data
        self.selenium.find_element(By.XPATH, "//input[@type='text']").click()
        # Wait for the column eleemnt to open
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.NAME, "columns"),
            )
        )
        self.selenium.find_element(By.NAME, "columns").click()
        self.selenium.find_element(
            By.XPATH,
            "(//input[@name='columns'])[2]"
        ).click()

        # Select the merge key
        self.select_tab('outputs-tab')
        self.selenium.find_element(By.ID, "id_merge_key").click()
        Select(self.selenium.find_element(
            By.ID,
            "id_merge_key")).select_by_visible_text("email")

        # Put the suffix _2
        self.selenium.find_element(By.ID, "id_out_column_suffix").click()
        self.selenium.find_element(By.ID, "id_out_column_suffix").clear()
        self.selenium.find_element(
            By.ID,
            "id_out_column_suffix").send_keys("_2")

        # Submit the execution
        self.selenium.find_element(By.NAME, "Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element(
                By.XPATH,
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name='Plugin test')
        self.assertTrue(
            sql.is_column_in_table(
                wflow.get_data_frame_table_name(),
                'RESULT 1_2'))
        self.assertTrue(
            sql.is_column_in_table(
                wflow.get_data_frame_table_name(),
                'RESULT 2_2'))
        df = pandas.load_table(wflow.get_data_frame_table_name())
        self.assertTrue(all([x == 1 for x in df['RESULT 1_2']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2_2']]))

        # End of session
        self.logout()


class DataopsPluginExecution2(
    tests.PluginExecutionFixture,
    tests.OnTaskLiveTestCase,
):

    def test(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('Plugin test')

        # Open the transform page
        self.go_to_transform()

        # Click in the second plugin
        element = self.search_table_row_by_string(
            'transform-table',
            1,
            'Test Plugin 2 Name')
        element.find_element(By.LINK_TEXT, 'Test Plugin 2 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )
        # Spinner not visible
        self.wait_for_spinner()

        # Provide the execution data (input columns and merge key
        self.selenium.find_element(
            By.ID,
            "id____ontask___upload_input_0"
        ).click()
        Select(self.selenium.find_element(
            By.ID,
            "id____ontask___upload_input_0"
        )).select_by_visible_text('A1')
        self.selenium.find_element(
            By.ID,
            "id____ontask___upload_input_1"
        ).click()
        Select(self.selenium.find_element(
            By.ID,
            "id____ontask___upload_input_1"
        )).select_by_visible_text('A2')
        # merge key
        self.select_tab('outputs-tab')
        self.selenium.find_element(By.ID, "id_merge_key").click()
        Select(self.selenium.find_element(
            By.ID,
            "id_merge_key"
        )).select_by_visible_text("email")
        # Submit the execution
        self.selenium.find_element(By.NAME, "Submit").click()

        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element(
                By.XPATH,
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name='Plugin test')
        df = pandas.load_table(wflow.get_data_frame_table_name())
        self.assertTrue('RESULT 3' in set(df.columns))
        self.assertTrue('RESULT 4' in set(df.columns))
        self.assertTrue(df['RESULT 3'].equals(df['A1'] + df['A2']))
        self.assertTrue(df['RESULT 4'].equals(df['A1'] - df['A2']))

        # End of session
        self.logout()


class DataopsMergeBasic(tests.OnTaskLiveTestCase):
    """Basic class to test various merge variations."""

    wflow_name = None
    merge_file = ''

    def template_merge(self, method, rename=True):
        """Template function to use with merge tests."""
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Go to the upload/merge page
        self.go_to_upload_merge()

        # Dataops/Merge CSV Merge Step 1
        self.selenium.find_element(By.LINK_TEXT, "CSV").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )
        self.selenium.find_element(
            By.ID,
            'id_data_file').send_keys(self.merge_file)

        # Click the NEXT button
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='id_new_name_0']")
            )
        )

        # Dataops/Merge CSV Merge Step 2
        if rename:
            # Rename the column
            self.selenium.find_element(By.ID, 'id_new_name_0').send_keys('2')

        # Click the NEXT button
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        ).click()
        self.wait_for_page()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//select[@id='id_dst_key']")
            )
        )

        # Dataops/Merge CSV Merge Step 3
        # Select left merge
        Select(self.selenium.find_element(
            By.ID,
            'id_how_merge'
        )).select_by_value(method)

        # Click the NEXT button
        self.selenium.find_element(
            By.XPATH,
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Review and confirm')
        )

        # Dataops/Merge CSV Merge Step 4
        # Click in Finish
        self.selenium.find_element(
            By.XPATH,
            "//button[normalize-space()='Finish']"
        ).click()
        self.wait_for_id_and_spinner('table-data_previous')


class DataopsMergeInner(tests.TestMergeFixture, DataopsMergeBasic):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')

    def test(self):
        self.template_merge('inner')

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        df = pandas.load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        # End of session
        self.logout()


class DataopsMergeOuter(tests.TestMergeFixture, DataopsMergeBasic):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')

    def test(self):
        self.template_merge('outer', False)

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        df = pandas.load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        # End of session
        self.logout()


class DataopsMergeLeft(tests.TestMergeFixture, DataopsMergeBasic):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')

    def test(self):
        self.template_merge('left')

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        df = pandas.load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        # End of session
        self.logout()


class DataopsMergeRight(tests.TestMergeFixture, DataopsMergeBasic):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')

    def test(self):
        self.template_merge('right', rename=False)

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        df = pandas.load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        # End of session
        self.logout()


class DataopsMergeOuterFail(tests.TestMergeFixture, DataopsMergeBasic):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_df_merge_update_df2.csv')

    def test(self):
        self.template_merge('outer')

        # Assert that the error is at the top of the page
        self.assertIn(
            'Merge operation produced a result without any key columns.',
            self.selenium.page_source
        )

        # Assert the content of the dataframe
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        df = pandas.load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' not in set(df.columns))
        self.assertTrue('double3' not in set(df.columns))
        self.assertTrue('bool3' not in set(df.columns))
        self.assertTrue('date3' not in set(df.columns))

        # End of session
        self.logout()


class DataopsEmptyKeyAfterMerge(
    tests.TestEmptyKeyAfterMergeFixture,
    DataopsMergeBasic,
):
    merge_file = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'test_empty_key_after_merge.csv')

    def test(self):
        self.template_merge('outer', rename=False)

        # Assert the presence of the error in the page
        self.assertIn('Merge operation failed.', self.selenium.page_source)

        # Assert additional properties
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        self.assertTrue(
            wflow.columns.get(name='key1').is_key,
            'Column key1 has lost is key property')
        self.assertTrue(
            wflow.columns.get(name='key2').is_key,
            'Column key2 has lost is key property')
        self.logout()
