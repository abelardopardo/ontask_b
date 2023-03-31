# -*- coding: utf-8 -*-

"""Basic class definitions for testing."""
import io
import math
import os
import subprocess
from typing import Dict, Mapping, Optional

from PIL import Image
from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import connection
from django.test import LiveServerTestCase, RequestFactory, TransactionTestCase
from django.urls import resolve, reverse
import pandas as pd
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from ontask import OnTaskSharedState, models
from ontask.core import GROUP_NAMES, SessionPayload
from ontask.core.checks import sanity_checks
from ontask.dataops import pandas

user_info = [
    ('Student One', 'student01@bogus.com', [GROUP_NAMES[0]], False),
    ('Student Two', 'student02@bogus.com', [GROUP_NAMES[0]], False),
    ('Student Three', 'student03@bogus.com', [GROUP_NAMES[0]], False),
    ('Instructor One', 'instructor01@bogus.com', [GROUP_NAMES[1]], False),
    ('Instructor Two', 'instructor02@bogus.com', [GROUP_NAMES[1]], False),
    ('Instructor Three', 'instructor03@bogus.com', [GROUP_NAMES[1]], False),
    ('Super User', 'superuser@bogus.com', GROUP_NAMES, True)]
boguspwd = 'boguspwd'


class ElementHasFullOpacity:
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
        return False


class OnTaskBasicTestCase(TransactionTestCase):
    """Basic test case to prepare/dismantle tests."""

    reset_sequences = True

    fixtures = []
    filename = None

    @classmethod
    def setUpClass(cls):
        if cls.filename:
            cls._pg_restore_table(cls.filename)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        pandas.destroy_db_engine(OnTaskSharedState.engine)
        super().tearDownClass()

    def tearDown(self) -> None:
        sanity_checks()
        self._delete_all_tables()
        super().tearDown()

    @staticmethod
    def _pg_restore_table(filename):
        """Upload a dump into the existing database

        :param filename: File in pg_dump format to restore
        :return: Nothing. Effect reflected in the DB
        """
        process = subprocess.Popen([
            'psql',
            '-o',
            '/dev/null',
            '-d',
            settings.DATABASES['default']['NAME'],
            '-q',
            '-f',
            filename])
        process.wait()

    @staticmethod
    def _delete_all_tables():
        """Delete all tables related to existing workflows."""
        cursor = connection.cursor()
        table_list = connection.introspection.get_table_list(cursor)
        for tinfo in table_list:
            if not tinfo.name.startswith(models.Workflow.table_prefix):
                continue
            cursor.execute('DROP TABLE "{0}";'.format(tinfo.name))

        # To make sure the table is dropped.
        connection.commit()

    @staticmethod
    def create_groups():
        """Create the user groups for OnTask."""
        for gname in GROUP_NAMES:
            Group.objects.get_or_create(name=gname)

    def create_users(self):
        """Create all the users based in the user_info."""
        self.create_groups()
        for uname, uemail, glist, __ in user_info:
            uobj = get_user_model().objects.filter(email=uemail).first()
            if not uobj:
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


class OnTaskTestCase(OnTaskBasicTestCase):
    """OnTask test cases not using selenium."""

    user_email = None
    user_pwd = None
    wflow_name = None
    workflow = None

    last_request = None

    @classmethod
    def _store_workflow_in_session(cls, session, wflow: models.Workflow):
        """Store the workflow id, name, and number of rows in the session.

        :param session: Current session used to store the information
        :param wflow: Workflow object
        :return: Nothing. Store the id, name and nrows in the session
        """
        session['ontask_workflow_rows'] = wflow.nrows
        session['ontask_workflow_id'] = wflow.id
        session['ontask_workflow_name'] = wflow.name

    def setUp(self):
        super().setUp()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        if self.user_email:
            self.user = get_user_model().objects.get(email=self.user_email)
            self.client.login(email=self.user_email, password=self.user_pwd)
        if self.wflow_name:
            self.workflow = models.Workflow.objects.get(
                name=self.wflow_name)
        self.last_request = None

    def add_middleware(self, request: http.HttpRequest) -> http.HttpRequest:
        """Add middleware values to the request."""
        request.user = self.user
        # adding session
        SessionMiddleware().process_request(request)
        # adding messages
        setattr(request, '_messages', FallbackStorage(request))
        if self.workflow:
            self._store_workflow_in_session(request.session, self.workflow)
        request.session.save()

        return request

    def get_response(
        self,
        url_name: str,
        url_params: Optional[Mapping] = None,
        method: Optional[str] = 'GET',
        req_params: Optional[Mapping] = None,
        meta=None,
        is_ajax: Optional[bool] = False,
        session_payload: Optional[Dict] = None,
        **kwargs
    ) -> http.HttpResponse:
        """Create a request and send it to a processing function.

        :param url_name: URL name as defined in urls.py
        :param url_params: Dictionary to give reverse to generate the full URL.
        :param method: GET (default) or POST
        :param req_params: Additional parameters to add to the request (for
        POST requests)
        :param meta: Dictionary of name, value for META
        :param is_ajax: Generate an ajax request or not
        :param session_payload: Dictionary to add to the request session
        :param kwargs: Additional arguments to attach to the URL
        :return:
        """
        url_params = {} if url_params is None else url_params
        url_str = reverse(url_name, kwargs=url_params)

        if req_params is None:
            req_params = {}

        if is_ajax:
            kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        if method == 'GET':
            request = self.factory.get(url_str, req_params, **kwargs)
        elif method == 'POST':
            request = self.factory.post(url_str, req_params, **kwargs)
        else:
            raise Exception('Incorrect request method')

        meta = {} if meta is None else meta
        for obj_name, obj_item in meta.items():
            request.META[obj_name] = obj_item

        old_payload = {}
        if self.last_request:
            old_payload = SessionPayload.get_session_payload(
                self.last_request)

        if session_payload:
            old_payload.update(session_payload)

        self.last_request = self.add_middleware(request)

        SessionPayload(self.last_request.session, old_payload)

        return resolve(url_str).func(self.last_request, **url_params)


class OnTaskApiTestCase(OnTaskBasicTestCase, APITransactionTestCase):
    """OnTask tests for the API."""

    def compare_wflows(self, jwflow, workflow):
        """Compare two workflows."""
        # Name and description match the one in the db
        self.assertEqual(jwflow['name'], workflow.name)
        self.assertEqual(jwflow['description_text'], workflow.description_text)

        jattr = jwflow['attributes']
        dattr = workflow.attributes
        self.assertEqual(set(jattr.items()), set(dattr.items()))

    def compare_tables(self, dframe1: pd.DataFrame, dframe2: pd.DataFrame):
        """Compare two pandas data frames.

        :param dframe1: Pandas data frame
        :param dframe2: Pandas data frame
        :return: Nothing. Assert various properties.
        """
        # If both are empty, done.
        if dframe2 is None and dframe1 is None:
            return

        # Assert that the number of columns are identical
        self.assertEqual(
            len(list(dframe1.columns)),
            len(list(dframe2.columns)))

        # The names of the columns have to be identical
        self.assertEqual(
            set(list(dframe1.columns)),
            set(list(dframe2.columns)))

        # Check the values of every column
        for cname in list(dframe1.columns):
            jvals = dframe1[cname].values
            dfvals = dframe2[cname].values

            # Compare removing the NaN, otherwise, the comparison breaks.
            self.assertEqual(
                [x for x in list(jvals) if not pd.isnull(x)],
                [x for x in list(dfvals) if not pd.isnull(x)]
            )


class OnTaskLiveTestCase(OnTaskBasicTestCase, LiveServerTestCase):
    """OnTask tests that use selenium."""

    viewport_height = 1024
    viewport_width = 1024
    device_pixel_ratio = 1
    max_image_height = 1440
    headless = True

    class_and_text_xpath = \
        '//{0}[contains(@class, "{1}") and normalize-space(text()) = "{2}"]'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.headless = cls.headless
        fp = webdriver.FirefoxProfile()
        fp.set_preference('dom.file.createInChild', True)
        fp.set_preference('font.size.variable.x-western', 14)
        cls.selenium = webdriver.Firefox(options=options, firefox_profile=fp)
        # cls.selenium = webdriver.Chrome()

        # Detect the type of screen being used
        cls.device_pixel_ratio = cls.selenium.execute_script(
            'return window.devicePixelRatio'
        )
        # print('Device Pixel Ratio: {0}'.format(cls.device_pixel_ratio))
        # print('Viewport width: {0}'.format(cls.viewport_width))
        # print('viewport height: {0}'.format(cls.viewport_height))

        cls.selenium.set_window_size(
            cls.viewport_width * cls.device_pixel_ratio,
            cls.viewport_height * cls.device_pixel_ratio)

        # After setting the window size, we need to update these values
        cls.viewport_height = cls.selenium.execute_script(
            'return window.innerHeight'
        )
        cls.viewport_width = cls.selenium.execute_script(
            'return window.innerWidth'
        )
        # cls.selenium.implicitly_wait(30)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def open(self, url):
        self.selenium.get('%s%s' % (self.live_server_url, url))

    def login(self, uemail):
        self.open(reverse('accounts:login'))
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username')))
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('id_username').send_keys(uemail)
        self.selenium.find_element_by_id('id_password').send_keys(boguspwd)
        self.selenium.find_element_by_id('submit-id-sign_in').click()
        # Wait for the user profile page
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="workflow-index"]')
            )
        )

        self.assertIn('reate a workflow', self.selenium.page_source)

    def logout(self):
        self.open(reverse('accounts:logout'))
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="div_id_username"]')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def wait_for_modal_open(self, xpath='//div[@id="modal-item"]//form'):
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def wait_for_modal_close(self):
        # Close modal (wail until the modal-open element disappears)
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

    def wait_for_id_and_spinner(self, table_id):
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
        self.wait_for_modal_close()
        # Wait for the table to be refreshed
        self.wait_for_id_and_spinner(table_id)

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
            '//div[@id="modal-item"]//button[@data-dismiss="modal"]'
        ).click()
        # Wail until the modal-open element disappears
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

    def click_dropdown_option(self, html_id: str, option_name: str):
        """
        Given a dropdown xpath, click to open and then click on the given option
        :param html_id: id to locate the dropdown element (top level)
        :param option_name: name of the option in the dropdown to click
        :return: Nothing
        """
        self.selenium.find_element_by_id(html_id).click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             '//*[@id="{0}"]//*[normalize-space() = "{1}"]'.format(
                 html_id,
                 option_name))
        ))
        self.selenium.find_element_by_xpath(
            '//*[@id="{0}"]//*[normalize-space() = "{1}"]'.format(
                html_id,
                option_name)).click()

    def click_dropdown_option_and_wait(
        self,
        html_id: str,
        option_name: str,
        wait_for: Optional[str] = None,
    ):
        """
        Given a dropdown xpath, click to open and then click on the given option
        :param html_id: id locate the dropdown element (top level)
        :param option_name: name of the option in the dropdown to click
        :param wait_for: @id to wait for, or modal open if none.
        :return: Nothing
        """
        self.click_dropdown_option(html_id, option_name)

        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            WebDriverWait(self.selenium, 10).until_not(
                EC.visibility_of_element_located((By.ID, 'div-spinner')))
        else:
            self.wait_for_modal_open()

    def click_dropdown_option_by_number(self, html_id: str, option_num: int):
        """Click the nth option in a dropdown menu.

        Given a dropdown xpath, click to open and then click on the given option

        :param html_id: id to locate the dropdown element (top level)
        :param option_num: position of the option in the dropdown to click
        :return: Nothing
        """
        self.selenium.find_element_by_id(html_id).click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             '//*[@id="{0}"]/div/*[{1}]'.format(html_id, option_num))))
        self.selenium.find_element_by_xpath(
            '//*[@id="{0}"]/div/*[{1}]'.format(html_id, option_num)
        ).click()

    def click_dropdown_option_num_and_wait(
        self,
        html_id: str,
        option_num: int,
        wait_for: Optional[str] = None,
    ):
        """Click the nth option in a dropdown menu and wait.

        Given a dropdown xpath, click to open and then click on the given option

        :param html_id: id to locate the dropdown element (top level)
        :param option_num: position of the option in the dropdown to click
        :param wait_for: @id to wait for, or modal open if none.
        :return: Nothing
        """
        self.click_dropdown_option_by_number(html_id, option_num)

        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            WebDriverWait(self.selenium, 10).until_not(
                EC.visibility_of_element_located((By.ID, 'div-spinner')))
        else:
            self.wait_for_modal_open()

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

        return self.selenium.find_element_by_xpath(
            '//table[@id="{0}"]/tbody/tr'
            '/td[{1}][starts-with(normalize-space(), "{2}")]/..'.format(
                table_id, colidx, value
            )
        )

    def search_action(self, action_name):
        return self.selenium.find_element_by_xpath(
            '//div[@id="action-cards"]//h5'
            '[starts-with(normalize-space(), "{0}")]/..'.format(action_name))

    def search_column(self, column_name):
        return self.search_table_row_by_string('column-table', 2, column_name)

    def access_workflow_from_home_page(self, wname):
        xpath = '//h5[contains(@class, "card-header") and ' \
                'normalize-space(text()) = "{0}"]'

        # Verify that this is the right page
        self.assertIn('New workflow', self.selenium.page_source)
        self.assertIn('Import workflow', self.selenium.page_source)

        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH, xpath.format(wname))
        ))
        self.selenium.find_element_by_xpath(xpath.format(wname)).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-index'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def go_to_home(self):
        # Goto the action page
        self.selenium.find_element_by_id('ontask-base-home').click()
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-index'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.assertIn('js-create-workflow', self.selenium.page_source)

    def go_to_actions(self):
        # Goto the action page
        self.selenium.find_element_by_id('ontask-base-actions').click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@class, "js-create-action")]')
            )
        )
        self.assertIn('js-create-action', self.selenium.page_source)

    def go_to_table(self):
        # Click in the top menu
        self.selenium.find_element_by_id('ontask-base-table').click()
        # Wait for the Full View to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'View data')
            )
        )
        # Click on the full view element
        self.selenium.find_element_by_link_text('View data').click()
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'table-content'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        element = self.selenium.find_element_by_id('table-data')
        if element:
            # The table is present!
            self.wait_for_id_and_spinner('table-data_previous')

        self.assertIn('CSV Download', self.selenium.page_source)

    def go_to_workflow_operations(self):
        # Goto the details page
        self.selenium.find_element_by_id('ontask-base-settings').click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             self.class_and_text_xpath.format(
                 'a',
                 'dropdown-item',
                 'Workflow operations'))
        ))
        self.selenium.find_element_by_id('ontask-base-workflow').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-detail'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.assertIn('js-workflow-clone', self.selenium.page_source)

    def go_to_details(self):
        # Goto the details page
        self.selenium.find_element_by_id('ontask-base-settings').click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             self.class_and_text_xpath.format(
                 'a',
                 'dropdown-item',
                 'Column operations'))
        ))
        self.selenium.find_element_by_id('ontask-base-columns').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-detail'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        element = self.selenium.find_element_by_id('column-table')
        if element:
            # The table is present!
            self.wait_for_id_and_spinner('column-table_previous')

        self.assertIn('Column Operations', self.selenium.page_source)

    def go_to_scheduler(self):
        self.selenium.find_element_by_id('ontask-base-settings').click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             self.class_and_text_xpath.format(
                 'a',
                 'dropdown-item',
                 'Scheduled operations'))
        ))
        self.selenium.find_element_by_id('ontask-base-scheduler').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'scheduler-index'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.assertIn('Scheduled Operations', self.selenium.page_source)

    def go_to_logs(self):
        self.selenium.find_element_by_id('ontask-base-settings').click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             self.class_and_text_xpath.format(
                 'a',
                 'dropdown-item',
                 'View logs'))
        ))
        self.selenium.find_element_by_id('ontask-base-logs').click()
        # Wait for ajax table to refresh
        element = self.selenium.find_element_by_id('log-table')
        if element:
            # Log table is present!
            self.wait_for_id_and_spinner('log-table_previous')
        self.assertIn('Logs', self.selenium.page_source)

    def go_to_sql_connections(self):
        # Click in the admin dropdown menu and then in the option
        self.click_dropdown_option('ontask-base-admin', 'SQL Connections')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'connection-admin-table'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def go_to_athena_connections(self):
        # Click in the admin dropdown menu and then in the option
        self.click_dropdown_option('ontask-base-admin', 'Athena Connections')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'connection-admin-table'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def go_to_upload_merge(self):
        # Click in the top menu
        self.selenium.find_element_by_id('ontask-base-table').click()
        # Wait for the Full View to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Upload or merge data')
            )
        )
        # Click on the upload and wait...
        self.selenium.find_element_by_link_text('Upload or merge data').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//table[@id="dataops-table"]')
            )
        )

    def go_to_csv_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]//a[normalize-space()="CSV"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form')
            )
        )

    def go_to_excel_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]'
            '//a[normalize-space()="Excel"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form')
            )
        )

    def go_to_google_sheet_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]//a[normalize-space()="Google '
            'Sheet"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form')
            )
        )

    def go_to_s3_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to S3 upload/merge
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]//a[normalize-space()="S3 Bucket '
            'CSV"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form')
            )
        )

    def go_to_sql_upload_merge(self):
        self.go_to_upload_merge()

        # Goto SQL option
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]//a[normalize-space()="SQL '
            'Connection"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id = "connection-instructor"]')
            )
        )

    def go_to_athena_upload_merge(self):
        self.go_to_upload_merge()

        # Goto Athena option
        self.selenium.find_element_by_xpath(
            '//table[@id="dataops-table"]//a[normalize-space()="Athena '
            'Connection"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id = "connection-instructor"]')
            )
        )

    def go_to_transform(self):
        # Click in the top menu
        self.selenium.find_element_by_id('ontask-base-table').click()
        # Wait for the Full View to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Run Transformation')
            )
        )
        # Click on the upload and wait...
        self.selenium.find_element_by_link_text('Run Transformation').click()
        self.wait_for_id_and_spinner('transform-table_previous')

    def go_to_model(self):
        # Click in the top menu
        self.selenium.find_element_by_id('ontask-base-table').click()
        # Wait for the Full View to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Run Model')
            )
        )
        # Click on the upload and wait...
        self.selenium.find_element_by_link_text('Run Model').click()
        self.wait_for_id_and_spinner('transform-table_previous')

    def go_to_attribute_page(self):
        self.selenium.find_element_by_id('ontask-base-settings').click()
        WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             self.class_and_text_xpath.format(
                 'a',
                 'dropdown-item',
                 'Workflow operations'))
        ))
        self.selenium.find_element_by_link_text('Workflow operations').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-attribute-create')))

    def go_to_workflow_share(self):
        # Go first to the attribute page (workflow)
        self.go_to_attribute_page()
        # Click on the share
        self.selenium.find_element_by_id('share-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-share-create'))
        )

    def go_to_workflow_export(self):
        self.go_to_workflow_operations()
        self.selenium.find_element_by_link_text('Export').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))

    def go_to_workflow_rename(self):
        # Click on the share
        self.go_to_workflow_operations()
        self.selenium.find_element_by_xpath(
            '//button[contains(@class, "js-workflow-update")]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def go_to_workflow_flush(self):
        # Click in the top menu
        self.selenium.find_element_by_id('ontask-base-table').click()
        # Wait for the Full View to be clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[normalize-space() = "Flush data table"]')
            )
        )
        # Click on the flush
        self.selenium.find_element_by_xpath(
            '//button[normalize-space() = "Flush data table"]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="modal-item"]//form')
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def go_to_workflow_delete(self):
        self.go_to_workflow_operations()
        self.selenium.find_element_by_xpath(
            '//button[contains(@class, "js-workflow-delete")]'
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="modal-item"]//form')
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def go_to_table_views(self):
        self.go_to_table()
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Views"]').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-view-add'))
        )

    def add_column(
        self,
        col_name,
        col_type,
        col_categories='',
        col_init='',
        index=None
    ):
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
            self.selenium.find_element_by_id('id_position').clear()
            self.selenium.find_element_by_id('id_position').send_keys(
                str(index)
            )

        # Click on the Submit button
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[normalize-space()="Add column"]'
        ).click()
        self.wait_close_modal_refresh_table('column-table_previous')

    def delete_column(self, col_name):
        xpath_txt = \
            '//table[@id="column-table"]' \
            '//tr/td[3][normalize-space() = "{0}"]/..'.format(
                col_name
            )
        # Click in the Delete button
        self.selenium.find_element_by_xpath(
            xpath_txt + '/td[2]/div/button[2]').click()
        self.wait_for_modal_open()

        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[@type="submit"]'
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
                (By.XPATH, '//table[@id="dataops-table"]')
            )
        )

    def create_new_action_out_basic(self, aname, action_type, adesc=''):
        # click on the create action button
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys(aname)
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(action_type)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="action-out-editor"]')
            )
        )

    def create_new_personalized_text_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.PERSONALIZED_TEXT,
            adesc)

    def create_new_rubric_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.RUBRIC_TEXT,
            adesc)

    def create_new_json_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.PERSONALIZED_JSON,
            adesc)

    def create_new_personalized_canvas_email_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.PERSONALIZED_CANVAS_EMAIL,
            adesc)

    def create_new_email_report_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.EMAIL_REPORT,
            adesc)

    def create_new_JSON_report_action(self, aname, adesc=''):
        self.create_new_action_out_basic(
            aname,
            models.Action.JSON_REPORT,
            adesc)

    def create_new_survey_action(self, aname, adesc=''):
        # click on the create action button
        self.selenium.find_element_by_class_name('js-create-action').click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element_by_id('id_name').send_keys(aname)
        desc = self.selenium.find_element_by_id('id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element_by_id('id_action_type'))
        select.select_by_value(models.Action.SURVEY)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="action-in-editor"]')
            )
        )

    def create_attribute(self, attribute_key, attribute_value):
        # Click in the new attribute dialog
        self.selenium.find_element_by_class_name('js-attribute-create').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'),
                'Create attribute'))

        # Fill out the form
        element = self.selenium.find_element_by_id('id_key')
        element.clear()
        element.send_keys(attribute_key)
        element = self.selenium.find_element_by_id('id_attr_value')
        element.clear()
        element.send_keys(attribute_value)

        # Click in the create attribute button
        self.selenium.find_element_by_xpath(
            '//div[@class="modal-footer"]/button[normalize-space()="Create '
            'attribute"]'
        ).click()

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

    def create_filter(self, cdesc, rule_tuples):
        # Make sure we are in the Filter tab
        self.select_filter_tab()

        self.create_condition_base(
            '//button[contains(@class, "js-filter-create")]',
            None,
            cdesc,
            rule_tuples)
        # Make sure the page refreshes and shows again the filter tab
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'filter-set-header')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def create_condition(self, cname, cdesc, rule_tuples):
        # Make sure we are in the Text Condition tab
        self.select_condition_tab()
        self.selenium.execute_script('window.scroll(0,0);')

        self.create_condition_base(
            '//button[contains(@class, "js-condition-create")]',
            cname,
            cdesc,
            rule_tuples)

        # Make sure the page refreshed
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-create')
            )
        )

    def create_condition_base(self, zone_xpath, cname, cdesc, rule_tuples):
        # Open the right modal
        self.open_condition(cname, zone_xpath)

        # Set the values of the condition
        if cname:
            form_field = self.selenium.find_element_by_xpath(
                '//div[@id="modal-item"]//input[@id="id_name"]'
            )
            form_field.clear()
            form_field.send_keys(cname)
        if cdesc:
            form_field = self.selenium.find_element_by_id(
                'id_description_text')
            form_field.click()
            form_field.clear()
            form_field.send_keys(cdesc)

        idx = 0
        for rule_filter, rule_operator, rule_value in rule_tuples:
            # Set the FILTER
            form_field = self.selenium.find_elements_by_name(
                'builder_rule_{0}_filter'.format(idx)
            )
            if not form_field:
                # Click in the Add rule of the filter builder button
                self.selenium.find_element_by_xpath(
                    '//div[@id="builder_group_0"]'
                    '//button[normalize-space()="Add rule"]'
                ).click()
                WebDriverWait(self.selenium, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '//select[@name="builder_rule_{0}_filter"]'.format(
                             idx))
                    )
                )
                form_field = self.selenium.find_element_by_name(
                    'builder_rule_{0}_filter'.format(idx)
                )
            else:
                form_field = form_field[0]

            form_field.click()
            Select(form_field).select_by_visible_text(rule_filter)

            # Set the operator
            if rule_operator:
                form_field = self.selenium.find_element_by_name(
                    'builder_rule_{0}_operator'.format(idx)
                )
                form_field.click()
                Select(form_field).select_by_visible_text(rule_operator)

            if rule_value is not None:
                # Set the value
                form_item = self.selenium.find_elements_by_name(
                    'builder_rule_{0}_value_0'.format(idx)
                )
                if len(form_item) == 1:
                    # There is a single place to put the value
                    form_item = form_item[0]
                    form_item.click()
                    if form_item.tag_name == 'select':
                        # It is a select element!
                        Select(form_item).select_by_value(rule_value)
                    else:
                        # It is a regular input value
                        form_item.clear()
                        form_item.send_keys(rule_value)
                else:
                    # The variable is a boolean. This breaks if the variable
                    # is an interval
                    if rule_value is True:
                        value_idx = 2
                    elif rule_value is False:
                        value_idx = 1
                    else:
                        raise Exception('Unexpected rule value')

                    self.selenium.find_element_by_xpath(
                        '(//input[@name="builder_rule_{0}_value_0"])'
                        '[{1}]'.format(
                            idx,
                            value_idx
                        )
                    ).click()
            idx += 1

        # Save the condition
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[@type="submit"]'
        ).click()

        # Close modal (wail until the modal-open element disappears)
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )
        # Spinner not visible
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        # Preview button clickable
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "js-action-preview")]'),
            )
        )

    def create_attachment(self, attachment_name):
        # Make sure we are in the Filter tab
        self.select_attachment_tab()

        self.click_dropdown_option('attachment-selector', attachment_name)

        # Make sure the page refreshes and shows again the filter tab
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'attachments')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def create_view(self, vname, vdesc, cols):
        self.go_to_table()

        # Button to dropdown the Views and click in create
        self.click_dropdown_option_num_and_wait('select-view-name', 1)

        # Wait for the form to create the derived column
        self.wait_for_modal_open()

        # Insert data to create the view
        element = self.selenium.find_element_by_id('id_name')
        element.click()
        element.clear()
        element.send_keys(vname)
        if vdesc:
            element = self.selenium.find_element_by_id('id_description_text')
            element.click()
            element.clear()
            element.send_keys(vdesc)

        # Focus on the column area
        self.selenium.find_element_by_xpath(
            '//*[@placeholder="Click here to search"]').click()
        options = self.selenium.find_element_by_xpath(
            '//*[@id="div_id_columns"]//div[@class="sol-selection"]'
        )
        for cname in cols:
            options.find_element_by_xpath(
                'div/label/div[normalize-space()="{0}"]'.format(cname)
            ).click()

        self.selenium.find_element_by_css_selector('div.modal-title').click()

        # Save the view
        self.selenium.find_element_by_xpath(
            '//button[normalize-space()="Add view"]'
        ).click()
        self.wait_close_modal_refresh_table('table-data_previous')

    def open_add_regular_column(self):
        # Click on the Add Column button
        self.click_dropdown_option_and_wait(
            'add-column-operations',
            'Regular column')

    def open_add_derived_column(self):
        # Click on the Add Column button
        self.click_dropdown_option_and_wait(
            'add-column-operations',
            'Formula-derived column')

    def open_column_edit(self, name):
        self.selenium.find_element_by_xpath(
            '//table[@id="column-table"]'
            '//td[3][normalize-space() = "{0}"]/'
            '../td[2]/div/button[1]'.format(name)).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//form[contains(@class, "js-column-edit-form")]')))

    def open_action_edit(self, name):
        self.selenium.find_element_by_xpath(
            '//div[@id="action-cards"]'
            '//h5[normalize-space() = "{0}"]'.format(name)).click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "js-action-preview")]')))
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def open_action_email(self, name):
        element = self.search_action(name)
        element.find_element_by_xpath('h5').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "js-action-preview")]')))

    def open_action_canvas_email(self, name):
        element = self.search_action(name)
        element.find_element_by_xpath('h5').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@class, "js-action-preview")]')))

    def open_action_operation(
        self,
        name: str,
        operation: str,
        wait_for: Optional[str] = None
    ):
        """Execute one operation for the given action"""
        xpath_str = \
            '//div[@id="action-cards"]' \
            '//h5[normalize-space() = "{0}"]/..'.format(name)
        try:
            elem = self.selenium.find_element_by_xpath(
                xpath_str
                + '/div/div/button/span[contains(@class, "{0}")]'.format(
                    operation))
        except NoSuchElementException:
            # Operation not found, so look in the pull down menu
            elem = self.selenium.find_element_by_xpath(
                xpath_str + '//*[contains(@class, "dropdown-toggle")]')

            elem.click()
            WebDriverWait(self.selenium, 10).until(EC.element_to_be_clickable(
                (By.XPATH,
                 xpath_str + '//span[contains(@class, "{0}")]'.format(
                     operation))))
            elem = self.selenium.find_element_by_xpath(
                xpath_str + '//span[contains(@class, "{0}")]'.format(
                    operation))

        # Click in the selected operation
        elem.click()
        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            WebDriverWait(self.selenium, 10).until_not(
                EC.visibility_of_element_located((By.ID, 'div-spinner')))
        else:
            self.wait_for_modal_open()

    def open_action_json_run(self, name):
        self.open_action_run(name)

    def open_action_run(self, name, is_action_in=False):
        element = self.search_action(name)
        element.find_element_by_xpath(
            'div/div/button/span[contains(@class, "fa-rocket")]').click()
        if is_action_in:
            self.wait_for_id_and_spinner('actioninrun-data_previous')
        else:
            # Preview button clickable
            WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@class, "js-action-preview")]'),
                )
            )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )

    def open_preview(self):
        self.selenium.find_element_by_xpath(
            '//button[contains(@class, "js-action-preview")]').click()
        # Wait for the modal to appear
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.ID, 'preview-body')
            )
        )
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def open_browse_preview(self, n=0, close=True):
        self.open_preview()

        for x in range(n):
            self.selenium.find_element_by_xpath(
                '//div[@id="modal-item"]'
                '//button[contains(@class, "js-action-preview-nxt")]'
            ).click()

            # Wait for the modal to appear
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located(
                    (By.ID, 'preview-body')
                )
            )
            WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'js-action-preview-nxt')
                )
            )

        if close:
            self.selenium.find_element_by_xpath(
                '//div[@id="modal-item"]//button[@data-dismiss="modal"]'
            ).click()
            # Close modal (wail until the modal-open element disappears)
            WebDriverWait(self.selenium, 10).until_not(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'modal-open')
                )
            )

    def open_condition(self, cname, xpath=None):
        # Select the right button element
        if not xpath:
            xpath = \
                '//div[@id="condition-set"]' \
                '/div/h5[contains(normalize-space(), "{0}")]' \
                '/../div/button[contains(@class, "js-condition-edit")]'.format(
                    cname
                )

        # Wait for the element to be clickable, and click
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        self.selenium.find_element_by_xpath(xpath).click()

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def open_filter(self):
        # Click on the right button
        self.selenium.find_element_by_xpath(
            '//button[contains(@class, "js-filter-edit")]',
        ).click()

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def open_view(self, vname):
        # Go to views first
        self.go_to_table()

        # Button to dropdown the Views
        self.click_dropdown_option_and_wait(
            'select-view-name',
            vname,
            'table-data_previous')

    def select_text_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'text-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('text-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "note-editable")]')
            )
        )

    def select_json_text_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'text-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('text-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//textarea[@id="id_target_url"]')
            )
        )

    def select_canvas_text_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'text-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('text-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//textarea[@id="id_text_content"]')
            )
        )

    def select_filter_tab(self):
        """
        Assuming we are in the action edit page, click on the link to open the
        filter tab
        :return:
        """
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'filter-tab'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('filter-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'filter-set-header')
            )
        )

    def select_condition_tab(self):
        """
        Assuming we are in the action edit page, click on the link to open the
        condition tab
        :return:
        """
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'conditions-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('conditions-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-condition-create')
            )
        )

    def select_attachment_tab(self):
        """
        Assuming we are editing an Email Report action, click on the link to
        open the attachment tab
        :return:
        """
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'attachments-tab'))
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('attachments-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'attachments')
            )
        )

    def select_share_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'share-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('share-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-share-create'))
        )

    def select_questions_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'questions-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('questions-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME,
                                        'js-action-question-add'))
        )

    def select_questions_condition(self, qname, cname):
        # Click in the pull down menu
        element = self.selenium.find_element_by_xpath(
            '//table[@id="column-selected-table"]'
            '//td[2][normalize-space() = "{0}"]/'
            '../td[5]/div/button'.format(qname))
        element.click()
        # Click in the condition name
        self.selenium.find_element_by_xpath(
            '//table[@id="column-selected-table"]'
            '//td[2][normalize-space() = "{0}"]/'
            '../td[5]/div/div/button[normalize-space() = "{1}"]'.format(
                qname,
                cname
            )
        ).click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@class, "js-action-question-add")]')
            )
        )

    def select_parameters_tab(self):
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'parameters-tab')
            )
        )
        self.selenium.find_element_by_id('parameters-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME,
                                        'js-description-edit'))
        )

    def select_rubric_tab(self):
        """
        Assuming we are in the action edit page, click on the link to open the
        rubric tab
        :return:
        """
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'rubric-tab')
            )
        )
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.selenium.find_element_by_id('rubric-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'js-workflow-criterion-add')
            )
        )

    def select_plugin_input_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'inputs-tab')
            )
        )
        self.selenium.find_element_by_id('inputs-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'sol-container'))
        )

    def select_plugin_output_tab(self):
        self.selenium.find_element_by_id('outputs-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'div_id_merge_key'))
        )

    def select_plugin_parameters_tab(self):
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.ID, 'parameters-tab')
            )
        )
        self.selenium.find_element_by_id('parameters-tab').click()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'parameters'))
        )

    def edit_condition(self, oldname, cname, cdesc, rule_tuples):
        self.select_condition_tab()
        self.create_condition_base(
            '//*[contains(@class, "card-header") and text() = "{0}"]/'
            '../div[@class = "cond-buttons"]/'
            'button[contains(@class, "js-condition-edit")]'.format(oldname),
            cname,
            cdesc,
            rule_tuples)

    def delete_condition(self, cname):
        """
        Given a condition name, search for it in the right DIV and click the
        buttons to remove it.
        :param cname: Condition name
        :return:
        """
        self.select_condition_tab()

        # Get the button for the condition
        self.selenium.find_element_by_xpath(
            '//*[contains(@class, "card-header") and text() = "{0}"]/'
            '../div[@class = "cond-buttons"]/'
            'button[contains(@class, "js-condition-delete")]'.format(cname),
        ).click()
        # Wait for the screen to delete the condition
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//div[@id="modal-item"]/div/div/form/div/h4'),
                'Confirm condition deletion')
        )

        # Click in the confirm button
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[normalize-space()="Delete '
            'condition"]'
        ).click()
        self.wait_for_page(element_id='edit-personalized-text-tab-content')

    def edit_filter(self, cname, cdesc, rule_tuples):
        self.select_filter_tab()
        self.create_condition_base(
            '//button[contains(@class, "js-filter-edit")]',
            cname,
            cdesc,
            rule_tuples)

    def delete_filter(self):
        # First make sure we are in the filter tab
        self.select_filter_tab()

        # Click in the delete Icon
        self.selenium.find_element_by_class_name('js-filter-delete').click()
        # Wait for the confirmation screen
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//div[@id="modal-item"]/div/div/form/div/h4'),
                'Confirm filter deletion')
        )

        # Click in the 'delete filter'
        self.selenium.find_element_by_xpath(
            '//div[@id="modal-item"]//button[normalize-space()="Delete filter"]'
        ).click()
        WebDriverWait(self.selenium, 10).until_not(
            EC.visibility_of_element_located((By.ID, 'div-spinner'))
        )
        self.wait_for_page(element_id='edit-personalized-text-tab-content')

    def edit_attribute(self, attribute_key, nkey, nvalue):
        self.selenium.find_element_by_xpath(
            '//table[@id="attribute-table"]'
            '//tr/td[2][normalize-space() = "{0}"]/'
            '../td[1]/div/button[1]'.format(attribute_key)
        ).click()
        self.wait_for_modal_open()

        # Fill out the form
        element = self.selenium.find_element_by_id('id_key')
        element.clear()
        element.send_keys(nkey)
        element = self.selenium.find_element_by_id('id_attr_value')
        element.clear()
        element.send_keys(nvalue)

        # Click in the create attribute button
        self.selenium.find_element_by_xpath(
            '//div[@class="modal-footer"]/button[normalize-space()="Update '
            'attribute"]'
        ).click()

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

    def assert_column_name_type(self, name, col_type, row_idx=None):
        """
        Assert that there is a column with the given name and with the given
        type
        :param name: Column name
        :param col_type: Type string (to check against the data-original-title)
        :param row_idx: Row index in the table (search if none is given)
        :return: Nothing
        """
        if row_idx:
            xpath_txt = \
                '//table[@id="column-table"]' \
                '//tr[{0}]/td[3][normalize-space() = "{1}"]' \
                '/../td[5][normalize-space() = "{2}"]'.format(
                    row_idx,
                    name,
                    col_type
                )
        else:
            xpath_txt = \
                '//table[@id="column-table"]' \
                '//tr/td[3][normalize-space() = "{0}"]' \
                '/../td[5][normalize-space() = "{1}"]'.format(
                    name,
                    col_type
                )

        self.assertIsNotNone(self.selenium.find_element_by_xpath(xpath_txt))


class ScreenTests(OnTaskLiveTestCase):
    viewport_width = 1040
    viewport_height = 1064
    prefix = ''
    workflow_name = 'BIOL1011'
    description = 'Course on Cell Biology'
    modal_xpath = '//div[@id="modal-item"]' \
                  '/div[contains(@class, "modal-dialog")]' \
                  '/div[@class="modal-content"]'

    img_path_prefix = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'images')

    def setUp(self):
        """Create the basic users"""
        super().setUp()
        self.create_users()

    def _img_path(self, image_file: str) -> str:
        return os.path.join(self.img_path_prefix, image_file)

    def _get_image(self, xpath):
        """
        Take the snapshot of the element with the given xpath and store it in
        the given filename
        :return: image object
        """

        if not xpath:
            raise Exception('Incorrect invocation of _get_image')

        img = Image.open(io.BytesIO(
            self.selenium.find_element_by_xpath(
                xpath
            ).screenshot_as_png)
        )

        return img

    def element_ss(self, xpath, ss_filename):
        """
        Take the snapshot of the element with the given xpath and store it in
        the given filename
        :return: Nothing
        """

        if not ss_filename:
            raise Exception('Incorrect invocation of element_ss')

        # Get the image
        img = self._get_image(xpath)

        img.save(self._img_path(self.prefix + ss_filename))

    def modal_ss(self, ss_filename):
        self.element_ss(self.modal_xpath, ss_filename)

    def body_ss(self, ss_filename):
        img = self._get_image('//body')

        try:
            body = self.selenium.find_element_by_id('base_footer')
            coord = body.location
            dims = body.size

            # If the bottom of the content is before the footer, crop
            if (
                coord['y'] + dims['height'] * self.device_pixel_ratio
            ) < self.viewport_height:
                img = img.crop(
                    (0,
                     0,
                     math.ceil(dims['width'] * self.device_pixel_ratio),
                     math.ceil((coord['y'] + dims['height'] + 5) *
                               self.device_pixel_ratio))
                )
        except NoSuchElementException:
            pass

        # If the height of the image is larger than the view_port, crop
        img_width, img_height = img.size
        if img_height > (self.viewport_height * self.device_pixel_ratio):
            img = img.crop((0,
                            0,
                            self.viewport_width * self.device_pixel_ratio,
                            self.viewport_height * self.device_pixel_ratio))

        img.save(self._img_path(self.prefix + ss_filename))
