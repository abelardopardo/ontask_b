# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.utils.html import escape
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import test
from dataops import pandas_db
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
        super(DataopsSymbols, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsSymbols, self).tearDown()

    def test_01_symbols(self):
        symbols = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # Go to the details page
        self.access_workflow_from_home_page('sss')

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
        self.wait_close_modal_refresh_table('attribute-table_previous')

        # Add a new attribute and insert key (symbols) and value
        self.create_attribute(symbols + '3', 'vvv')

        # Save and close the attribute page
        self.selenium.find_element_by_link_text('Back').click()
        # Wait for the details page
        self.wait_close_modal_refresh_table('column-table_previous')

        # Click in the TABLE link
        self.go_to_table()

        # Verify that everything appears normally
        self.assertIn(escape(symbols), self.selenium.page_source)
        self.assertIn(escape(symbols + '2'), self.selenium.page_source)

        # Click in the Actions navigation menu
        self.go_to_actions()

        # Edit the action-in
        self.open_action_edit('action in')

        # Set the right columns to process
        select = Select(self.selenium.find_element_by_id(
            'select-column-name'))
        select.select_by_visible_text('!#$%&()*+,-./:;<=>?@[\]^_`{|}~2')
        self.wait_for_datatable('column-selected-table_previous')
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'column-selected-table_previous')
            )
        )

        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'))
        select.select_by_visible_text('sid')
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'))
        select.select_by_visible_text('email')
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Save action-in
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
            "//body/div[4]/div/form/button[1]/span").click()
        # Wait for paging widget
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'actioninrun-data_previous'))
        )

        # Go Back to the action table
        self.selenium.find_element_by_xpath(
            "//div[@id='table-content']/a"
        ).click()
        # Wait for paging widget
        self.wait_for_datatable('action-table_previous')

        # Edit the action out
        element = self.search_action('action_out')
        element.find_element_by_link_text("Edit").click()

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
        self.create_condition(symbols + "4",
                              '',
                              [(symbols, "begins with", "C")])

        # Create the filter
        self.create_filter(symbols,
                           '',
                           [(symbols + "2", "doesn't begin with", "x")])

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

        assert pandas_db.check_wf_df(Workflow.objects.get(name='sss'))

        # End of session
        self.logout()

    def test_02_symbols(self):
        symbols = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~'

        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('sss')

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
        select = Select(self.selenium.find_element_by_id(
            'select-key-column-name'
        ))
        select.select_by_visible_text('email' + symbols)
        # This wait is incorrect. Don't know how to wait for an AJAX call.
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

        # Done editing the action in
        self.selenium.find_element_by_link_text('Done').click()
        self.wait_for_datatable('action-table_previous')

        # Click in the run link
        self.open_action_survey_run('action in')

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

        # Modify the value of the column
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

        assert pandas_db.check_wf_df(Workflow.objects.get(name='sss'))

        # End of session
        self.logout()


class DataopsExcelUpload(test.OnTaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsExcelUpload, self).tearDown()

    def test_01_excelupload(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1', False)

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
        self.wait_for_datatable('column-table_previous')

        # The number of rows must be 29
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 29)
        self.assertEqual(wflow.ncols, 14)

        assert pandas_db.check_wf_df(Workflow.objects.get(name='wflow1'))

        # End of session
        self.logout()


class DataopsExcelUploadSheet(test.OnTaskLiveTestCase):
    fixtures = ['empty_wflow']

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsExcelUploadSheet, self).tearDown()

    def test_01_excelupload_sheet(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page('wflow1', False)

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
        self.wait_for_datatable('column-table_previous')

        # The number of rows must be 19
        wflow = Workflow.objects.all()[0]
        self.assertEqual(wflow.nrows, 19)
        self.assertEqual(wflow.ncols, 14)

        assert pandas_db.check_wf_df(Workflow.objects.get(name='wflow1'))

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
        pandas_db.delete_all_tables()
        super(DataopsNaNProcessing, self).tearDown()

    def test_01_nan_manipulation(self):
        # Login
        self.login('instructor01@bogus.com')

        self.create_new_workflow('NaN')

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            "//tbody/tr[1]/td[1]/a[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//form")
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
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
        self.wait_for_datatable('column-table_previous')

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
        self.wait_for_datatable('column-table_previous')

        # Go to the actions page
        self.go_to_actions()

        # Create a new action
        self.create_new_personalized_text_action("action out", '')

        # Create three conditions
        self.create_condition("bool1 cond", '', [('bool1', None, True)])
        self.create_condition("bool 2 cond", '', [('bool2', None, True)])
        self.create_condition('bool3 cond', '', [('bool3', None, True)])

        # insert the action text
        self.selenium.execute_script(
            """$('#id_content').summernote('editor.insertText', 
            "{0}");""".format(self.action_text)
        )

        # Click in the preview and circle around the 12 rows
        self.open_browse_preview(11)

        assert pandas_db.check_wf_df(Workflow.objects.get(name='wflow1'))

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
        super(DataopsPluginExecution, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsPluginExecution, self).tearDown()

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
                                                  'test_plugin_1')
        element.find_element_by_link_text('Run').click()
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
        self.selenium.find_element_by_id('div_id_merge_key').click()

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
        self.selenium.find_element_by_link_text('Continue').click()
        self.wait_for_datatable('column-table_previous')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 1' in set(df.columns))
        self.assertTrue('RESULT 2' in set(df.columns))
        self.assertTrue(all([x == 1 for x in df['RESULT 1']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2']]))

        # Second execution, this time adding a suffix to the column
        self.go_to_transform()

        # Click in the first plugin
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'test_plugin_1')
        element.find_element_by_link_text('Run').click()
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
        self.selenium.find_element_by_link_text('Continue').click()
        self.wait_for_datatable('column-table_previous')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 1_2' in set(df.columns))
        self.assertTrue('RESULT 2_2' in set(df.columns))
        self.assertTrue(all([x == 1 for x in df['RESULT 1_2']]))
        self.assertTrue(all([x == 2 for x in df['RESULT 2_2']]))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Plugin test'))

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
        # Click in the first plugin
        element = self.search_table_row_by_string('transform-table',
                                                  1,
                                                  'test_plugin_2')
        element.find_element_by_link_text('Run').click()
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
        self.wait_for_page(element_id='plugin-execution-report')

        # Done. Click continue.
        self.selenium.find_element_by_link_text('Continue').click()
        self.wait_for_datatable('column-table_previous')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name='Plugin test')
        df = pandas_db.load_from_db(wflow.id)
        self.assertTrue('RESULT 3' in set(df.columns))
        self.assertTrue('RESULT 4' in set(df.columns))
        self.assertTrue(df['RESULT 3'].equals(df['A1'] + df['A2']))
        self.assertTrue(df['RESULT 4'].equals(df['A1'] - df['A2']))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Plugin test'))

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
        super(DataopsMerge, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(DataopsMerge, self).tearDown()

    def template_merge(self, method, rename=True):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wf_name)

        # Go to the upload/merge page
        self.go_to_upload_merge()

        # Dataops/Merge CSV Merge Step 1
        self.selenium.find_element_by_link_text("CSV Upload/Merge").click()
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
                (By.CLASS_NAME, 'page-header'),
                'Step 4: Review and confirm')
        )

        # Dataops/Merge CSV Merge Step 4
        # Click in Finish
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Finish']"
        ).click()
        self.wait_for_datatable('column-table_previous')


    def test_01_merge_inner(self):
        self.template_merge('inner')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = pandas_db.load_from_db(wflow.id)

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_02_merge_outer(self):
        self.template_merge('outer', False)

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = pandas_db.load_from_db(wflow.id)

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_03_merge_left(self):
        self.template_merge('left')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = pandas_db.load_from_db(wflow.id)

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()

    def test_04_merge_right(self):
        self.template_merge('right')

        # Assert the content of the dataframe
        wflow = Workflow.objects.get(name=self.wf_name)
        df = pandas_db.load_from_db(wflow.id)

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' in set(df.columns))
        self.assertTrue('text3' in set(df.columns))
        self.assertTrue('double3' in set(df.columns))
        self.assertTrue('bool3' in set(df.columns))
        self.assertTrue('date3' in set(df.columns))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Testing Merge'))

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
        df = pandas_db.load_from_db(wflow.id)

        self.assertTrue('key' in set(df.columns))
        self.assertTrue('key2' not in set(df.columns))
        self.assertTrue('text3' not in set(df.columns))
        self.assertTrue('double3' not in set(df.columns))
        self.assertTrue('bool3' not in set(df.columns))
        self.assertTrue('date3' not in set(df.columns))

        assert pandas_db.check_wf_df(Workflow.objects.get(name='Testing Merge'))

        # End of session
        self.logout()
