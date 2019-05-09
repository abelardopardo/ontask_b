# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import test

from django.conf import settings
from django.utils.html import escape
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from dataops.pandas import check_wf_df, load_table
from dataops.sql.column_queries import is_column_in_table
from workflow.models import Workflow


class DataopsSymbols(test.OnTaskLiveTestCase):
    fixtures = ['wflow_symbols']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'wflow_symbols.sql'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_symbols(self):
        symbols = '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # Open the workflow
        self.access_workflow_from_home_page('sss')

        # Go to the column details
        self.go_to_details()

        # Edit the name column
        self.open_column_edit('name')

        # Replace name by symbols
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Click in the submit/save button
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click on the Add Column button
        self.open_add_regular_column()

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
        self.go_to_attribute_page()

        # Delete the existing one and confirm deletion
        # click the delete button in the second row
        self.selenium.find_element_by_xpath(
            '//table[@id="attribute-table"]'
            '//tr[1]/td[3]//button[contains(@class, "js-attribute-delete")]'
        ).click()
        # Click in the delete confirm button
        self.selenium.find_element_by_xpath(
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
        self.open_action_edit('action in')

        # Go to questions
        self.select_questions_tab()

        # Set the right columns to process
        self.click_dropdown_option(
            "//div[@id='column-selector']",
            '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~2'
        )
        self.wait_for_datatable('column-selected-table_previous')
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )

        # Set some parameters
        self.select_parameters_tab()
        self.click_dropdown_option("//div[@id='select-key-column-name']", 'sid')
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.select_parameters_tab()
        self.click_dropdown_option("//div[@id='select-key-column-name']",
                                   'email')
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Save action-in
        self.select_questions_tab()
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_datatable('action-table_previous')

        # Click in the RUN link of the action in
        element = self.search_action('action in')
        element.find_element_by_link_text("Run").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Enter data using the RUN menu. Select one entry to populate
        self.selenium.find_element_by_link_text("student01@bogus.com").click()
        self.wait_for_page(element_id='action-row-datainput')
        self.selenium.find_element_by_id("id____ontask___select_1").click()
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id("id____ontask___select_1").send_keys(
            "17")
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
            "//div[@id='action-row-datainput']//form//button").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Go Back to the action table
        self.go_to_actions()

        # Edit the action out
        self.open_action_edit('action_out')

        # Click in the editor
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'note-editable')
            )
        )
        self.selenium.find_element_by_class_name('note-editable').click()

        # Insert attribute
        self.click_dropdown_option("//div[@id='attribute-selector']",
                                   symbols + '3')

        # Insert column name
        self.click_dropdown_option("//div[@id='column-selector']", symbols)

        # Insert second column name
        self.click_dropdown_option("//div[@id='column-selector']",
                                   symbols + '2')

        # Create new condition
        self.create_condition(symbols + "4",
                              '',
                              [(symbols, "begins with", "C")])

        # Create the filter
        self.create_filter('', [(symbols + "2", "doesn't begin with", "x")])

        # Click the preview button
        self.select_text_tab()
        self.selenium.find_element_by_class_name('js-action-preview').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-action-preview-nxt'))
        )

        # Certain name should be in the page now.
        self.assertIn('Carmelo Coton', self.selenium.page_source)

        # Click in the "Close" button
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']/div/div/div/div[2]/button[2]").click()

        assert check_wf_df(Workflow.objects.get(name='sss'))

        # End of session
        self.logout()

    def test_02_symbols(self):
        symbols = '!#$%&()*+,-./\\:;<=>?@[]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('sss')

        # Go to column details
        self.go_to_details()

        # Edit the email column
        self.open_column_edit('email')

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Select the age column and click in the edit button
        self.open_column_edit('age')

        # Append symbols to the name
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").send_keys(symbols)

        # Save column information
        self.selenium.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_close_modal_refresh_table('column-table_previous')

        # Go to the table link
        self.go_to_table()

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn('<td class=" dt-center">12</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">12.1</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">13.2</td>',
                      self.selenium.page_source)

        # Go to the actions page
        self.go_to_actions()

        # Edit the action-in at the top of the table
        self.open_action_edit('action in')

        # Set the correct values for an action-in
        # Set the right columns to process
        self.select_parameters_tab()
        self.click_dropdown_option("//div[@id='select-key-column-name']",
                                   'email' + symbols)
        # This wait is incorrect. Don't know how to wait for an AJAX call.
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Done editing the action in
        self.select_questions_tab()
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_datatable('action-table_previous')

        # Click in the run link
        self.open_action_run('action in', True)

        # Click on the first value
        self.selenium.find_element_by_link_text("student01@bogus.com").click()

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
        self.wait_for_datatable('actioninrun-data_previous')

        # Click on the second value
        self.selenium.find_element_by_link_text("student02@bogus.com").click()

        # Modify the value of the columne
        self.selenium.find_element_by_id("id____ontask___select_1").clear()
        self.selenium.find_element_by_id(
            "id____ontask___select_1"
        ).send_keys("15")
        # Submit changes to the second element
        self.selenium.find_element_by_xpath(
            "(//button[@name='submit'])[1]"
        ).click()
        self.wait_for_datatable('actioninrun-data_previous')

        # Click on the third value
        self.selenium.find_element_by_link_text("student03@bogus.com").click()

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
        self.wait_for_datatable('actioninrun-data_previous')

        # Click in the back link!
        self.selenium.find_element_by_link_text('Back').click()
        self.wait_for_datatable('action-table_previous')

        # Go to the table page
        self.go_to_table()

        # Assert the new values
        self.assertIn('<td class=" dt-center">14</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">15</td>',
                      self.selenium.page_source)
        self.assertIn('<td class=" dt-center">16</td>',
                      self.selenium.page_source)

        assert check_wf_df(Workflow.objects.get(name='sss'))

        # End of session
        self.logout()


class DataopsExcelUpload(test.OnTaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_excelupload(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1')

        # Go to Excel upload/merge
        self.go_to_excel_upload_merge_step_1()

        # Upload file
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
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_name("Submit").click()
        self.wait_for_datatable('table-data_previous')

        # The number of rows must be 29
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 29)
        self.assertEqual(wflow.ncols, 14)

        assert check_wf_df(Workflow.objects.get(name='wflow1'))

        # End of session
        self.logout()


class DataopsExcelUploadSheet(test.OnTaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_excelupload_sheet(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1')

        # Go to Excel upload/merge
        self.go_to_excel_upload_merge_step_1()

        # Upload the file
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
        self.wait_for_datatable('table-data_previous')

        # The number of rows must be 19
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 19)
        self.assertEqual(wflow.ncols, 14)

        assert check_wf_df(Workflow.objects.get(name='wflow1'))

        # End of session
        self.logout()


class DataopsNaNProcessing(test.OnTaskLiveTestCase):
    fixtures = ['empty_wflow']
    action_text = "Bool1 = {{ bool1 }}\\n" + \
                  "Bool2 = {{ bool2 }}\\n" + \
                  "Bool3 = {{ bool3 }}\\n" + \
                  "{% if bool1 cond %}Bool 1 is true{% endif %}\\n" + \
                  "{% if bool2 cond %}Bool 2 is true{% endif %}\\n" + \
                  "{% if bool3 cond %}Bool 3 is true{% endif %}\\n"

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_nan_manipulation(self):
        # Login
        self.login('instructor01@bogus.com')

        self.create_new_workflow('NaN')

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//table[@id='dataops-table']//a[normalize-space()='CSV']").click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )

        # Select file and upload
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'test_df_merge_update_df1.csv')
        )
        self.selenium.find_element_by_name("Submit").click()
        self.wait_for_page()

        # Submit
        self.selenium.find_element_by_xpath(
            "(//button[@name='Submit'])[2]"
        ).click()
        self.wait_for_datatable('table-data_previous')

        # Select again the upload/merge function
        self.go_to_csv_upload_merge_step_1()

        # Select the second file and submit
        self.selenium.find_element_by_id("id_file").send_keys(
            os.path.join(settings.BASE_DIR(),
                         'dataops',
                         'fixtures',
                         'test_df_merge_update_df2.csv')
        )
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//body/div/h1"),
                                             'Select Columns')
        )

        # Select all the columns for upload
        self.selenium.find_element_by_name("Submit").click()
        # Wait for the upload/merge
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Select Keys and Merge Option')
        )

        # Choose the default options for the merge (key and outer)
        # Select the merger function type
        select = Select(self.selenium.find_element_by_id('id_how_merge'))
        select.select_by_value('outer')
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Review and confirm')
        )

        # Check the merge summary and proceed
        self.selenium.find_element_by_name("Submit").click()
        # Wait for the upload/merge to finish
        self.wait_for_datatable('table-data_previous')

        # Go to the actions page
        self.go_to_actions()

        # Create a new action
        self.create_new_personalized_text_action("action out", '')

        # Create three conditions
        self.select_condition_tab()
        self.create_condition("bool1 cond", '', [('bool1', None, True)])
        self.create_condition("bool 2 cond", '', [('bool2', None, True)])
        self.create_condition('bool3 cond', '', [('bool3', None, True)])

        # insert the action text
        self.select_text_tab()
        self.selenium.execute_script(
            """$('#id_text_content').summernote('editor.insertText', 
            "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.open_browse_preview(11)

        assert check_wf_df(Workflow.objects.get(name='wflow1'))

        # End of session
        self.logout()


class DataopsPluginExecution(test.OnTaskLiveTestCase):
    fixtures = ['plugin_execution']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'plugin_execution.sql'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_01_first_plugin(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('Plugin test')

        # Open the transform page
        self.go_to_transform()

        # Click in the first plugin
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'Test Plugin 1 Name')
        element.find_element_by_link_text('Test Plugin 1 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))
        )

        # Provide the execution data
        self.selenium.find_element_by_xpath("//input[@type='text']").click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()

        # Select the merge key
        self.select_plugin_output_tab()

        self.selenium.find_element_by_id("id_merge_key").click()
        Select(self.selenium.find_element_by_id(
            "id_merge_key"
        )).select_by_visible_text("email")

        # Submit the execution
        self.selenium.find_element_by_name("Submit").click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        self.assertTrue(is_column_in_table(wflow.get_data_frame_table_name(),
                                           'RESULT 1'))
        self.assertTrue(is_column_in_table(wflow.get_data_frame_table_name(),
                                           'RESULT 2'))
        df = load_table(wflow.get_data_frame_table_name())
        self.assertTrue(all([x == 1 for x in df['RESULT 1']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2']]))

        # Second execution, this time adding a suffix to the column
        self.go_to_actions()
        self.go_to_transform()

        # Click in the first plugin
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'Test Plugin 1 Name')
        element.find_element_by_link_text('Test Plugin 1 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))
        )

        # Provide the execution data
        self.selenium.find_element_by_xpath("//input[@type='text']").click()
        # Wait for the column eleemnt to open
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.NAME, "columns"),
            )
        )
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()

        # Select the merge key
        self.select_plugin_output_tab()
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
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        self.assertTrue(is_column_in_table(wflow.get_data_frame_table_name(),
                                           'RESULT 1_2'))
        self.assertTrue(is_column_in_table(wflow.get_data_frame_table_name(),
                                           'RESULT 2_2'))
        df = load_table(wflow.get_data_frame_table_name())
        self.assertTrue(all([x == 1 for x in df['RESULT 1_2']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2_2']]))

        assert check_wf_df(Workflow.objects.get(name='Plugin test'))

        # End of session
        self.logout()

    def test_02_second_plugin(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('Plugin test')

        # Open the transform page
        self.go_to_transform()

        # Click in the second plugin
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'Test Plugin 2 Name')
        element.find_element_by_link_text('Test Plugin 2 Name').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))
        )

        # Provide the execution data (input columns and merge key
        self.selenium.find_element_by_id(
            "id____ontask___upload_input_0"
        ).click()
        Select(self.selenium.find_element_by_id(
            "id____ontask___upload_input_0"
        )).select_by_visible_text('A1')
        self.selenium.find_element_by_id(
            "id____ontask___upload_input_1"
        ).click()
        Select(self.selenium.find_element_by_id(
            "id____ontask___upload_input_1"
        )).select_by_visible_text('A2')
        # merge key
        self.select_plugin_output_tab()
        self.selenium.find_element_by_id("id_merge_key").click()
        Select(self.selenium.find_element_by_id(
            "id_merge_key"
        )).select_by_visible_text("email")
        # Submit the execution
        self.selenium.find_element_by_name("Submit").click()

        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Plugin scheduled for execution')
        )

        # There should be a message on that page
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                "//div[@id='plugin-run-done']/div/a"
            ).text.startswith(
                'You may check the status in log number'
            )
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = load_table(wflow.get_data_frame_table_name())
        self.assertTrue('RESULT 3' in set(df.columns))
        self.assertTrue('RESULT 4' in set(df.columns))
        self.assertTrue(df['RESULT 3'].equals(df['A1'] + df['A2']))
        self.assertTrue(df['RESULT 4'].equals(df['A1'] - df['A2']))

        assert check_wf_df(Workflow.objects.get(name='Plugin test'))

        # End of session
        self.logout()


class DataopsMerge(test.OnTaskLiveTestCase):
    wf_name = 'Testing Merge'
    fixtures = ['test_merge']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'test_merge.sql'
    )
    merge_file = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'test_df_merge_update_df2.csv'
    )

    def setUp(self):
        super().setUp()
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def template_merge(self, method, rename=True):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wf_name)

        # Go to the upload/merge page
        self.go_to_upload_merge()

        # Dataops/Merge CSV Merge Step 1
        self.selenium.find_element_by_link_text("CSV").click()
        WebDriverWait(self.selenium, 10).until(
            EC.title_is('OnTask :: Upload/Merge CSV')
        )
        self.selenium.find_element_by_id('id_file').send_keys(self.merge_file)

        # Click the NEXT button
        self.selenium.find_element_by_xpath(
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
            self.selenium.find_element_by_id('id_new_name_0').send_keys('2')

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

        # Dataops/Merge CSV Merge Step 3
        # Select left merge
        Select(self.selenium.find_element_by_id(
            'id_how_merge'
        )).select_by_value(method)

        # Click the NEXT button
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/h1"),
                'Review and confirm')
        )

        # Dataops/Merge CSV Merge Step 4
        # Click in Finish
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Finish']"
        ).click()
        self.wait_for_datatable('table-data_previous')

    def test_01_merge_inner(self):
        self.template_merge('inner')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_02_merge_outer(self):
        self.template_merge('outer', False)

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_03_merge_left(self):
        self.template_merge('left')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_04_merge_right(self):
        self.template_merge('right', rename=False)

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_05_merge_outer_fail(self):
        self.template_merge('outer')

        # Assert that the error is at the top of the page
        self.assertIn(
            'Merge operation produced a result without any key columns.',
            self.selenium.page_source
        )

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = load_table(wflow.get_data_frame_table_name())

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' not in set(df.columns))
        self.assertTrue('double3' not in set(df.columns))
        self.assertTrue('bool3' not in set(df.columns))
        self.assertTrue('date3' not in set(df.columns))

        assert check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()


class DataopsEmptyKeyAfterMerge(DataopsMerge):
    wf_name = 'Test Empty Key after Merge'
    fixtures = ['test_empty_key_after_merge']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'test_empty_key_after_merge.sql'
    )
    merge_file = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'test_empty_key_after_merge.csv'
    )

    def test_merge(self):
        self.template_merge('outer', rename=False)

        # Assert the presence of the error in the page
        self.assertIn('Merge operation failed.', self.selenium.page_source)

        # Assert additional properties
        wflow = Workflow.objects.get(name=self.wf_name)
        self.assertTrue(wflow.columns.get(name='key1').is_key,
                        'Column key1 has lost is key property')
        self.assertTrue(wflow.columns.get(name='key2').is_key,
                        'Column key2 has lost is key property')
        self.logout()
