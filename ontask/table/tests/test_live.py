# -*- coding: utf-8 -*-

"""Classes for testing."""
import os

from django.conf import settings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from ontask import models, tests
from ontask.dataops import pandas


class TableDerivedColumns(tests.OnTaskLiveTestCase):
    fixtures = ['derived_column']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'derived_column.sql'
    )

    wflow_name = 'combine columns'

    def test_table_create_derived_columns(self):
        """Test operations to create derived columns."""
        # Login
        self.login('instructor01@bogus.com')

        # Open workflow
        self.access_workflow_from_home_page(self.wflow_name)

        # Go to table page
        self.go_to_table()

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D1 = c1 + c2
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d1")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("sum: Sum selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[3]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D2 = c3 * c4
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d2")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("prod: Product of the selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[4]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[5]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D3 = max(c5, c6)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d3")
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("max: Maximum of the selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[6]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[7]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D4 = min(c7, c8)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d4")
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("min: Minimum of the selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[8]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[9]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D5 = mean(c1, c2)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d5")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("mean: Mean of the selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[3]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D6 = median(c3, c4)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d6")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text("median: Median of the selected columns")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[4]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[5]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D7 = std(c5, c6)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d7")
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text(
            "std: Standard deviation over the selected columns"
        )
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[6]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[7]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D8 = all(c91, c92)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d8")
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text(
            "all: True when all elements in selected columns are true"
        )
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        # Wait for JS to do its thing
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//input[@name='columns'])[12]"))
        )
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[11]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[12]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Click in the add derived column button
        self.open_add_derived_column()

        # Fill out the details for D9 = any(c91, c92)
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("d9")
        self.selenium.find_element_by_id("id_op_type").click()
        Select(self.selenium.find_element_by_id(
            "id_op_type"
        )).select_by_visible_text(
            "any: True when any element in selected columns is true"
        )
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        # Wait for JS to do its thing
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//input[@name='columns'])[12]"))
        )
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[11]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[12]"
        ).click()
        self.selenium.find_element_by_css_selector(
            "div.modal-footer > button.btn.btn-outline-primary"
        ).click()
        # MODAL WAITING
        self.wait_close_modal_refresh_table('table-data_previous')

        # Check that the data is correct
        df = pandas.load_table(
             models.Workflow.objects.all()[0].get_data_frame_table_name(),
        )

        # d1 = c1 + c2
        self.assertTrue((df['d1'] == df[['c1', 'c2']].sum(axis=1)).all())
        # d2 = c3 * c4
        self.assertTrue((df['d2'] == df[['c3', 'c4']].prod(axis=1)).all())
        # d3 = max(c5, c6)
        self.assertTrue((df['d3'] == df[['c5', 'c6']].max(axis=1)).all())
        # d4 = min(c7, c8)
        self.assertTrue((df['d4'] == df[['c7', 'c8']].min(axis=1)).all())
        # d5 = mean(c1, c2)
        self.assertTrue((df['d5'] == df[['c1', 'c2']].mean(axis=1)).all())
        # d6 = median(c3, c4)
        self.assertTrue((df['d6'] == df[['c3', 'c4']].median(axis=1)).all())
        # d7 = std(c5, c6) (error below 10^{-11})
        self.assertTrue(
            ((df['d7'] - df[['c5', 'c6']].std(axis=1)).abs() < 0.1e-12).all())
        # d8 = all(c91, c92)
        self.assertTrue((df['d8'] == df[['c91', 'c92']].all(axis=1)).all())
        # d9 = any(c91, c92)
        self.assertTrue((df['d9'] == df[['c91', 'c92']].any(axis=1)).all())

        # End of session
        self.logout()


class TableViews(tests.OnTaskLiveTestCase):
    fixtures = ['derived_column']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'derived_column.sql'
    )

    wflow_name = 'combine columns'

    # Test operations with all derived columns
    def test_table_views(self):
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Open the Table view
        self.go_to_table()

        # Open the Views menu
        self.selenium.find_element_by_link_text("Views").click()

        # Button to add a view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='View']"
        ).click()
        self.wait_for_modal_open()

        # Insert data to create the first view
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("v1")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[2]"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[3]"
        ).click()
        self.selenium.find_element_by_css_selector("div.modal-body").click()
        self.selenium.find_element_by_css_selector(
            "button.btn.btn-xs.btn-success"
        ).click()
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter"
        )).select_by_visible_text("c1")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name(
            "builder_rule_0_value_0"
        ).send_keys("5")
        # Save the view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add view']"
        ).click()
        self.wait_close_modal_refresh_table('view-table_previous')

        # Click in the link to see the table resulting from this view
        self.selenium.find_element_by_xpath(
            "//table[@id='view-table']"
            "//td[2][normalize-space() = 'v1']/../td[1]/div/a[2]"
        ).click()
        # Wait for the table to be refreshed
        self.wait_for_datatable('table-data_previous')

        # Check the number of entries
        self.assertIn(
            'Showing 1 to 10 of 13 entries (filtered from 100 total entries)',
            self.selenium.page_source)

        # Go back to the views page
        self.selenium.find_element_by_link_text("Views").click()
        # Wait for the table to be refreshed
        self.wait_for_datatable('view-table_previous')

        # Add a second view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='View']"
        ).click()
        self.wait_for_modal_open()

        # Add the details for the second view
        self.selenium.find_element_by_id("id_name").click()
        self.selenium.find_element_by_id("id_name").clear()
        self.selenium.find_element_by_id("id_name").send_keys("v2")
        self.selenium.find_element_by_css_selector(
            "div.sol-input-container > input[type=\"text\"]"
        ).click()
        self.selenium.find_element_by_name("columns").click()
        self.selenium.find_element_by_xpath(
            "//div[@id='div_id_columns']/div/div/div/div[3]/div[2]/label/div"
        ).click()
        self.selenium.find_element_by_xpath(
            "(//input[@name='columns'])[3]"
        ).click()
        self.selenium.find_element_by_id("div_id_columns").click()
        self.selenium.find_element_by_css_selector(
            "button.btn.btn-xs.btn-success"
        ).click()
        self.selenium.find_element_by_name("builder_rule_0_filter").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_filter"
        )).select_by_visible_text("c2")
        self.selenium.find_element_by_name("builder_rule_0_operator").click()
        Select(self.selenium.find_element_by_name(
            "builder_rule_0_operator"
        )).select_by_visible_text("greater or equal")
        self.selenium.find_element_by_name("builder_rule_0_value_0").click()
        self.selenium.find_element_by_name("builder_rule_0_value_0").clear()
        self.selenium.find_element_by_name(
            "builder_rule_0_value_0"
        ).send_keys("5")
        # Save the view
        self.selenium.find_element_by_xpath(
            "//button[normalize-space()='Add view']"
        ).click()
        self.wait_close_modal_refresh_table('view-table_previous')

        # Check the table resulting from the view
        self.selenium.find_element_by_xpath(
            "//table[@id='view-table']"
            "//td[2][normalize-space() = 'v2']/../td[1]/div/a[2]"
        ).click()
        # Wait for the table to be refreshed
        self.wait_for_datatable('table-data_previous')

        # Check the number of entries
        self.assertIn(
            'Showing 1 to 10 of 42 entries (filtered from 100 total entries)',
            self.selenium.page_source)

        # Click in views button and go back to the full table
        self.selenium.find_element_by_xpath(
            "//div[@id='table-operation-buttons']/div/div[2]/button"
        ).click()
        self.selenium.find_element_by_link_text("Full table").click()
        # Wait for the table to be refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@id='table-content']/h1"),
                'Table'
            )
        )

        self.wait_for_datatable('table-data_previous')

        # Check the number of entries
        self.assertIn(
            'Showing 1 to 10 of 100 entries',
            self.selenium.page_source)

        # Go back to the view management
        self.selenium.find_element_by_link_text("Views").click()
        # Wait for the table to be refreshed
        self.wait_for_datatable('view-table_previous')

        # Click in the clone link of the first view
        self.selenium.find_element_by_xpath(
            "//table[@id='view-table']//tr/td[2][normalize-space() = 'v1']/"
            "../td[1]/div/button[1]"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[normalize-space()="Clone view"]')
            )
        )
        # Confirm view cloning
        self.selenium.find_element_by_xpath(
            "//div[@class='modal-footer']/button[normalize-space()='Clone "
            "view']"
        ).click()
        self.wait_close_modal_refresh_table('view-table_previous')

        # Open the view with the clone
        self.selenium.find_element_by_xpath(
            "//table[@id='view-table']"
            "//td[2][normalize-space() = 'Copy of v1']/../td[1]/div/a[2]"
        ).click()
        # Wait for the table to be refreshed
        self.wait_for_datatable('table-data_previous')

        # Check the number of entries
        self.assertIn(
            'Showing 1 to 10 of 13 entries (filtered from 100 total entries)',
            self.selenium.page_source)

        # End of session
        self.logout()


class TableInsertRow(tests.OnTaskLiveTestCase):
    fixtures = ['derived_column']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'derived_column.sql'
    )

    wflow_name = 'combine columns'

    def test_table_insert_row(self):
        """Test operations  with derived columns."""
        # Login
        self.login('instructor01@bogus.com')

        # GO TO THE WORKFLOW PAGE
        self.access_workflow_from_home_page(self.wflow_name)

        # Go to the table page
        self.go_to_table()

        # Click on the add row button
        self.selenium.find_element_by_link_text('Row').click()

        # Fill out the fields in the form
        for x in range(0, 10):
            keyelem = self.selenium.find_element_by_id(
                'id____ontask___upload_{0}'.format(x)
            )
            keyelem.clear()
            keyelem.send_keys(str(x))

        # Set c91 to true
        c91 = self.selenium.find_element_by_id('id____ontask___upload_10')
        self.assertFalse(c91.is_selected())
        c91.click()
        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            "//form//button[@type='submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger'))
        )

        # Incorrect primary key introduced (repeated value)
        self.assertIn('The new data does not preserve the key property',
                      self.selenium.page_source)

        # Introduce a valid primary key
        keyelem = self.selenium.find_element_by_id(
            'id____ontask___upload_0'
        )
        keyelem.clear()
        keyelem.send_keys('100')
        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            "//form//button[@type='submit']"
        ).click()
        self.wait_for_datatable('table-data_previous')

        # Go to page 11 of the table
        self.selenium.find_element_by_link_text('11').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'sorting_1'),
                                             '100')
        )

        # Click in the Ops -> delete button -> Delete row
        element = self.selenium.find_element_by_xpath(
            "//table[@id='table-data']"
            "//tr/td[2][normalize-space() = '100']/"
            "../td[1]/div/button"
        )
        ActionChains(self.selenium).move_to_element(element).click().perform()
        self.wait_for_modal_open()
        self.selenium.find_element_by_xpath(
            "//div[@id='modal-item']//button[@type='submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, 'table-data_info'),
                'of 100 entries'
            )
        )

        # End of session
        self.logout()
