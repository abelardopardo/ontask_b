"""Basic class definitions for testing."""
import io
import math
import os
import subprocess
from typing import Dict, Mapping, Optional
from importlib import import_module

from PIL import Image
from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import connection
from django.template.response import SimpleTemplateResponse
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

    secret_key = 'd$2Jpj*.1fV:0J-s_]1r+~!-X*"sWp:/(pd(7vf2b]{' \
                 'bl3*e`4\'oS/VDuO\\ZZ!b?u~K*]Tz?_Mgu-n6icWo9#Lv<82HapCkaI8Sp'

    @classmethod
    def setUpClass(cls):
        if cls.filename:
            cls._pg_restore_table(cls.filename)
        super().setUpClass()
        # Fix the secret key so that tests use the correct one
        settings.SECRET_KEY = cls.secret_key

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
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        session_engine = import_module(settings.SESSION_ENGINE)
        request.session = session_engine.SessionStore(session_key)

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

        response = resolve(url_str).func(self.last_request, **url_params)

        if isinstance(response, SimpleTemplateResponse):
            response.render()

        return response


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

    class_and_text_xpath = \
        '//{0}[contains(@class, "{1}") and normalize-space(text()) = "{2}"]'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.headless = settings.ONTASK_HEADLESS_TEST
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

    def wait_for_spinner(self):
        WebDriverWait(self.selenium, 10).until(
            EC.invisibility_of_element_located((By.ID, 'div-spinner'))
        )

    def click_on_element(self, by_string, string_value):
        """Wait for an element to be clickable and then click

        :by_string: String By.* to use in find_element
        :sring_value: String to use as find criteria
        :return: Element
        """
        element = self.selenium.find_element(by_string, string_value)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(element))
        element.click()
        return element

    def login(self, uemail):
        self.open(reverse('accounts:login'))
        self.wait_for_spinner()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'id_username')))
        self.selenium.find_element(By.ID, 'id_username').send_keys(uemail)
        self.selenium.find_element(By.ID, 'id_password').send_keys(boguspwd)
        self.selenium.find_element(By.ID, 'submit-id-sign_in').click()
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
        self.wait_for_spinner()

    def scroll_element_into_view(self, element):
        self.selenium.execute_script(
            "arguments[0].scrollIntoView("
            "{block: 'center', inline: 'nearest', behavior: 'instant'});",
            element)
        WebDriverWait(self.selenium, 10).until(EC.visibility_of(element))

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
        self.wait_for_spinner()

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
                EC.visibility_of_element_located((By.ID, element_id))
            )

    def cancel_modal(self):
        # Click in the cancel button
        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[@data-bs-dismiss="modal"]')
        # Wail until the modal-open element disappears
        WebDriverWait(self.selenium, 10).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'modal-open')
            )
        )

    def click_dropdown_option(self, ddown_id: str, option_name: str):
        """
        Given a dropdown id, click to open and then click on the given option
        :param ddown_id: id to locate the dropdown element (top level)
        :param option_name: name of the option in the dropdown to click
        :return: Nothing
        """
        self.click_on_element(By.ID, ddown_id)
        self.click_on_element(
            By.XPATH,
            '//*[@id="{0}"]//*[normalize-space() = "{1}"]'.format(
                 ddown_id,
                 option_name))

    def click_dropdown_option_and_wait(
        self,
        ddown_id: str,
        option_name: str,
        wait_for: Optional[str] = None,
    ):
        """
        Given a dropdown id, click to open and then click on the given option
        :param ddown_id: id locate the dropdown element (top level)
        :param option_name: name of the option in the dropdown to click
        :param wait_for: @id to wait for, or modal open if none.
        :return: Nothing
        """
        self.click_dropdown_option(ddown_id, option_name)

        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            self.wait_for_spinner()
        else:
            self.wait_for_modal_open()

    def click_dropdown_option_by_number(self, ddown_id: str, option_num: int):
        """Click the nth option in a dropdown menu.

        Given a dropdown xpath, click to open and then click on the given option

        :param ddown_id: id to locate the dropdown element (top level)
        :param option_num: position of the option in the dropdown to click
        :return: Nothing
        """
        self.click_on_element(By.ID, ddown_id)
        self.click_on_element(
            By.XPATH,
            '//*[@id="{0}"]/div/*[{1}]'.format(ddown_id, option_num))

    def click_dropdown_option_num_and_wait(
        self,
        ddown_id: str,
        option_num: int,
        wait_for: Optional[str] = None,
    ):
        """Click the nth option in a dropdown menu and wait.

        Given a dropdown xpath, click to open and then click on the given option

        :param ddown_id: id to locate the dropdown element (top level)
        :param option_num: position of the option in the dropdown to click
        :param wait_for: @id to wait for, or modal open if none.
        :return: Nothing
        """
        self.click_dropdown_option_by_number(ddown_id, option_num)

        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            self.wait_for_spinner()
        else:
            self.wait_for_modal_open()

    def search_table_row_by_string(self, table_id, col_index, value):
        """
        Given a table id and a column index, it traverses the table searching
        for the given value in the column.
        :param table_id: ID of the HTML table element
        :param col_index: Column index
        :param value: Value to search
        :return: Row Element
        """
        # Table ID must be in the page
        self.assertIn(table_id, self.selenium.page_source)

        return self.selenium.find_element(
            By.XPATH,
            '//table[@id="{0}"]/tbody/tr'
            '/td[{1}][starts-with(normalize-space(), "{2}")]/..'.format(
                table_id, col_index, value
            )
        )

    def search_action(self, action_name):
        return self.selenium.find_element(
            By.XPATH,
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

        self.click_on_element(By.XPATH, xpath.format(wname))
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'action-index'))
        )
        self.wait_for_spinner()

    def go_to_home(self):
        # Goto the action page
        self.click_on_element(By.ID, 'ontask-base-home')
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-index'))
        )
        self.wait_for_spinner()
        self.assertIn('js-create-workflow', self.selenium.page_source)

    def go_to_actions(self):
        # Goto the action page
        self.click_on_element(By.ID, 'ontask-base-actions')
        self.wait_for_spinner()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@class, "js-create-action")]')
            )
        )
        self.assertIn('js-create-action', self.selenium.page_source)

    def go_to_table(self):
        # Click in the top menu
        self.click_on_element(By.ID, 'ontask-base-table')
        # Click on the full view element
        self.click_on_element(By.LINK_TEXT, 'View data')
        # Wait for page to refresh
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'table-content'))
        )
        self.wait_for_spinner()
        element = self.selenium.find_element(By.ID, 'table-data')
        if element:
            # The table is present!
            self.wait_for_id_and_spinner('table-data_previous')

        self.assertIn('CSV Download', self.selenium.page_source)

    def go_to_workflow_operations(self):
        # Goto the details page
        self.click_on_element(By.ID, 'ontask-base-settings')
        self.click_on_element(By.ID, 'ontask-base-workflow')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-detail'))
        )
        self.wait_for_spinner()
        self.assertIn('js-workflow-clone', self.selenium.page_source)

    def go_to_details(self):
        # Goto the details page
        self.click_on_element(By.ID, 'ontask-base-settings')
        self.click_on_element(By.ID, 'ontask-base-columns')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'workflow-detail'))
        )
        self.wait_for_spinner()
        element = self.selenium.find_element(By.ID, 'column-table')
        if element:
            # The table is present!
            self.wait_for_id_and_spinner('column-table_previous')

        self.assertIn('Column Operations', self.selenium.page_source)

    def go_to_scheduler(self):
        self.click_on_element(By.ID, 'ontask-base-settings')
        self.click_on_element(By.ID, 'ontask-base-scheduler')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'scheduler-index'))
        )
        self.wait_for_spinner()
        self.assertIn('Scheduled Operations', self.selenium.page_source)

    def go_to_logs(self):
        self.click_on_element(By.ID, 'ontask-base-settings')
        self.click_on_element(By.ID, 'ontask-base-logs')
        # Wait for ajax table to refresh
        element = self.selenium.find_element(By.ID, 'log-table')
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
        self.wait_for_spinner()

    def go_to_athena_connections(self):
        # Click in the admin dropdown menu and then in the option
        self.click_dropdown_option('ontask-base-admin', 'Athena Connections')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'connection-admin-table'))
        )
        self.wait_for_spinner()

    def go_to_upload_merge(self):
        # Click in the top menu
        self.click_on_element(By.ID, 'ontask-base-table')
        # Wait for the Full View to be clickable
        self.click_on_element(By.LINK_TEXT, 'Upload or merge data')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//table[@id="dataops-table"]')))

    def go_to_csv_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]//a[normalize-space()="CSV"]')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//form')))

    def go_to_excel_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]'
            '//a[normalize-space()="Excel"]')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//form')))

    def go_to_google_sheet_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to CSV Upload/Merge
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]//a[normalize-space()="Google Sheet"]')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//form')))

    def go_to_s3_upload_merge_step_1(self):
        self.go_to_upload_merge()

        # Go to S3 upload/merge
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]//a[normalize-space()="S3 Bucket '
            'CSV"]')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//form')))

    def go_to_sql_upload_merge(self):
        self.go_to_upload_merge()

        # Goto SQL option
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]//a[normalize-space()="SQL '
            'Connection"]')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id = "connection-instructor"]')))

    def go_to_athena_upload_merge(self):
        self.go_to_upload_merge()

        # Goto Athena option
        self.click_on_element(
            By.XPATH,
            '//table[@id="dataops-table"]//a[normalize-space()="Athena '
            'Connection"]')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id = "connection-instructor"]')))

    def go_to_transform(self):
        # Click in the top menu
        self.click_on_element(By.ID, 'ontask-base-table')
        self.click_on_element(By.LINK_TEXT, 'Run Transformation')
        self.wait_for_id_and_spinner('transform-table_previous')

    def go_to_model(self):
        # Click in the top menu
        self.click_on_element(By.ID, 'ontask-base-table')
        self.click_on_element(By.LINK_TEXT, 'Run Model')
        self.wait_for_id_and_spinner('transform-table_previous')

    def go_to_attribute_page(self):
        self.click_on_element(By.ID, 'ontask-base-settings')
        self.click_on_element(By.LINK_TEXT, 'Workflow operations')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'js-attribute-create')))

    def go_to_workflow_share(self):
        # Go first to the attribute page (workflow)
        self.go_to_attribute_page()
        # Click on the share
        self.click_on_element(By.ID, 'share-tab')
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-share-create'))
        )

    def go_to_workflow_export(self):
        self.go_to_workflow_operations()
        self.click_on_element(By.LINK_TEXT, 'Export')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))

    def go_to_workflow_rename(self):
        # Click on the share
        self.go_to_workflow_operations()
        self.click_on_element(
            By.XPATH,
            '//button[contains(@class, "js-workflow-update")]')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def go_to_workflow_flush(self):
        # Go to workflow ops first
        self.go_to_workflow_operations()
        self.click_on_element(
            By.XPATH,
            '//button[contains(@class, "js-workflow-flush")]')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//form')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def go_to_workflow_delete(self):
        self.go_to_workflow_operations()
        self.click_on_element(
            By.XPATH,
            '//button[contains(@class, "js-workflow-delete")]')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="modal-item"]//form')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]')))

    def go_to_table_views(self):
        self.go_to_table()
        self.click_on_element(
            By.XPATH,
            '//button[normalize-space()="Views"]')
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
        self.selenium.find_element(By.ID, 'id_name').send_keys(col_name)
        select = Select(self.selenium.find_element(
            By.ID,
            'id_data_type'))
        select.select_by_value(col_type)
        if col_categories:
            self.selenium.find_element(
                By.ID,
                'id_raw_categories').send_keys(col_categories)
        if col_init:
            self.selenium.find_element(
                By.ID,
                'id_initial_value'
            ).send_keys(col_init)
        if index:
            self.selenium.find_element(By.ID, 'id_position').clear()
            self.selenium.find_element(By.ID, 'id_position').send_keys(
                str(index)
            )

        # Click on the Submit button
        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[normalize-space()="Add column"]')
        self.wait_close_modal_refresh_table('column-table_previous')

    def delete_column(self, col_name):
        xpath_txt = \
            '//table[@id="column-table"]' \
            '//tr/td[3][normalize-space() = "{0}"]/..'.format(
                col_name
            )
        # Click in the Delete button
        self.click_on_element(By.XPATH, xpath_txt + '/td[2]/div/button[2]')
        self.wait_for_modal_open()

        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[@type="submit"]')

        # Wait for modal to close and refresh the table
        self.wait_close_modal_refresh_table('column-table_previous')

    def create_new_workflow(self, wname, wdesc=''):
        # Create the workflow
        self.click_on_element(By.CLASS_NAME, 'js-create-workflow')
        self.wait_for_modal_open()

        self.selenium.find_element(By.ID, 'id_name').send_keys(wname)
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        desc.send_keys(wdesc)
        desc.send_keys(Keys.RETURN)

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//table[@id="dataops-table"]')))

    def create_new_action_out_basic(self, aname, action_type, adesc=''):
        # click on the create action button
        self.click_on_element(By.CLASS_NAME, 'js-create-action')
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(aname)
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(action_type)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        self.wait_for_spinner()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="action-out-editor"]')))

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
        self.click_on_element(By.CLASS_NAME, 'js-create-action')
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'id_name')))

        # Set the name, description and type of the action
        self.selenium.find_element(By.ID, 'id_name').send_keys(aname)
        desc = self.selenium.find_element(By.ID, 'id_description_text')
        # Select the action type
        select = Select(self.selenium.find_element(By.ID, 'id_action_type'))
        select.select_by_value(models.Action.SURVEY)
        desc.send_keys(adesc)
        desc.send_keys(Keys.RETURN)
        # Wait for the spinner to disappear, and then for the button to be
        # clickable
        self.wait_for_spinner()
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="action-in-editor"]')))

    def create_attribute(self, attribute_key, attribute_value):
        # Click in the new attribute dialog
        self.click_on_element(By.CLASS_NAME, 'js-attribute-create')
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'modal-title'),
                'Create attribute'))

        # Fill out the form
        element = self.selenium.find_element(By.ID, 'id_key')
        element.clear()
        element.send_keys(attribute_key)
        element = self.selenium.find_element(By.ID, 'id_attr_value')
        element.clear()
        element.send_keys(attribute_value)

        # Click in the create attribute button
        self.click_on_element(
            By.XPATH,
            '//div[@class="modal-footer"]/button[normalize-space()="Create '
            'attribute"]')

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

    def create_attachment(self, attachment_name):
        # Make sure we are in the Filter tab
        self.select_tab('attachments-tab')

        self.click_dropdown_option('attachment-selector', attachment_name)

        # Make sure the page refreshes and shows again the filter tab
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'attachments')))
        self.wait_for_spinner()

    def create_view(self, vname, vdesc, cols):
        self.go_to_table()

        # Button to drop down the Views and click in create
        self.click_dropdown_option_num_and_wait('select-view-name', 1)

        # Wait for the form to create the derived column
        self.wait_for_modal_open()

        # Insert data to create the view
        element = self.click_on_element(By.ID, 'id_name')
        element.clear()
        element.send_keys(vname)
        if vdesc:
            element = self.click_on_element(By.ID, 'id_description_text')
            element.clear()
            element.send_keys(vdesc)

        # Focus on the column area
        self.click_on_element(
            By.XPATH,
            '//*[@placeholder="Click here to search"]')
        options = self.selenium.find_element(
            By.XPATH,
            '//*[@id="div_id_columns"]//div[@class="sol-selection"]'
        )
        for cname in cols:
            options.find_element(
                By.XPATH,
                'div/label/div[normalize-space()="{0}"]'.format(cname)
            ).click()

        self.click_on_element(By.CSS_SELECTOR, 'div.modal-title')

        # Save the view
        self.click_on_element(
            By.XPATH,
            '//button[normalize-space()="Add view"]')
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
        self.click_on_element(
            By.XPATH,
            '//table[@id="column-table"]'
            '//td[3][normalize-space() = "{0}"]/'
            '../td[2]/div/button[1]'.format(name))
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//form[contains(@class, "js-column-edit-form")]')))

    def open_action_edit(self, name: str, wait_id: str = 'text') -> None:
        self.click_on_element(
            By.XPATH,
            '//div[@id="action-cards"]'
            '//h5[normalize-space() = "{0}"]'.format(name))
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "js-action-preview")]')))
        self.wait_for_page(element_id=wait_id)

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
            elem = self.click_on_element(
                By.XPATH,
                xpath_str
                + '/div/div/button/i[contains(@class, "{0}")]'.format(
                    operation))
        except NoSuchElementException:
            # Operation not found, so look in the pull down menu
            self.click_on_element(
                By.XPATH,
                xpath_str + '//*[contains(@class, "dropdown-toggle")]')
            self.click_on_element(
                By.XPATH,
                xpath_str + '//i[contains(@class, "{0}")]'.format(operation))

        if wait_for:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, wait_for)))
            self.wait_for_spinner()
        else:
            self.wait_for_modal_open()

    def open_action_json_run(self, name):
        self.open_action_run(name)

    def open_action_run(self, name, is_action_in=False):
        element = self.search_action(name)
        element.find_element(
            By.XPATH,
            'div/div/button/i[contains(@class, "bi-rocket-takeoff-fill")]'
        ).click()
        if is_action_in:
            self.wait_for_id_and_spinner('actioninrun-data_previous')
        else:
            # Preview button clickable
            WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@class, "js-action-preview")]')))
        self.wait_for_spinner()

    def open_preview(self):
        preview_button = self.selenium.find_element(
            By.XPATH,
            '//button[contains(@class, "js-action-preview")]')
        self.scroll_element_into_view(preview_button)
        preview_button.click()
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
            self.click_on_element(
                By.XPATH,
                '//div[@id="modal-item"]'
                '//button[contains(@class, "js-action-preview-nxt")]'
            )

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
            self.click_on_element(
                By.XPATH,
                '//div[@id="modal-item"]//button[@data-bs-dismiss="modal"]')
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
        self.click_on_element(By.XPATH, xpath)

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def open_filter(self):
        # Click on the right button
        self.click_on_element(
            By.XPATH,
            '//button[contains(@class, "js-filter-edit")]')

        # Wait for the modal to open
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'id_description_text')))
        WebDriverWait(self.selenium, 10).until(
            ElementHasFullOpacity((By.XPATH, '//div[@id="modal-item"]'))
        )

    def open_view(self, vname) -> None:
        # Go to views first
        self.go_to_table()

        # Button to drop down the Views
        self.click_dropdown_option_and_wait(
            'select-view-name',
            vname,
            'table-data_previous')

    def select_tab(self, tab_id) -> None:
        """Given a tab_id, click and wait for it to be the only one visible."""
        tab_element = self.click_on_element(By.ID, tab_id)

        # Obtain all tab-pane elements and wait for the proper visibility
        tab_body_id = tab_element.get_dom_attribute('href')[1:]
        tab_hrefs = [
            x.get_dom_attribute('href')[1:]
            for x in tab_element.find_elements(
                By.XPATH,
                'parent::*/parent::*/li/a')]
        assert tab_body_id in tab_hrefs
        tab_hrefs.remove(tab_body_id)
        for t in tab_hrefs:
            WebDriverWait(self.selenium, 10).until(
                EC.invisibility_of_element_located((By.ID, t)))
        WebDriverWait(self.selenium, 10).until_not(
            EC.invisibility_of_element_located((By.ID, tab_body_id)))

    def select_questions_condition(self, qname, cname):
        # Click in the pull down menu
        self.click_on_element(
            By.XPATH,
            '//table[@id="column-selected-table"]'
            '//td[2][normalize-space() = "{0}"]/'
            '../td[5]/div/button'.format(qname))
        # Click in the condition name
        self.click_on_element(
            By.XPATH,
            '//table[@id="column-selected-table"]'
            '//td[2][normalize-space() = "{0}"]/'
            '../td[5]/div/div/button[normalize-space() = "{1}"]'.format(
                qname,
                cname))
        self.wait_for_spinner()
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@class, "js-action-question-add")]')))

    def create_condition_base(self, zone_xpath, cname, cdesc, rule_tuples):
        # Open the right modal
        self.open_condition(cname, zone_xpath)

        # Set the values of the condition
        if cname:
            form_field = self.selenium.find_element(
                By.XPATH,
                '//div[@id="modal-item"]//input[@id="id_name"]')
            form_field.clear()
            form_field.send_keys(cname)
        if cdesc:
            form_field = self.click_on_element(By.ID, 'id_description_text')
            form_field.clear()
            form_field.send_keys(cdesc)

        idx = 0
        for rule_filter, rule_operator, rule_value in rule_tuples:
            # Set the FILTER
            form_field = self.selenium.find_elements(
                By.NAME,
                'builder_rule_{0}_filter'.format(idx)
            )
            if not form_field:
                # Click in the Add rule of the filter builder button
                self.click_on_element(
                    By.XPATH,
                    '//div[@id="builder_group_0"]'
                    '//button[normalize-space()="Add rule"]')
                WebDriverWait(self.selenium, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '//select[@name="builder_rule_{0}_filter"]'.format(
                             idx))))
                form_field = self.selenium.find_element(
                    By.NAME,
                    'builder_rule_{0}_filter'.format(idx))
            else:
                form_field = form_field[0]

            form_field.click()
            Select(form_field).select_by_visible_text(rule_filter)

            # Set the operator
            if rule_operator:

                form_field = self.click_on_element(
                    By.NAME,
                    'builder_rule_{0}_operator'.format(idx))
                Select(form_field).select_by_visible_text(rule_operator)

            if rule_value is not None:
                # Set the value
                form_item = self.selenium.find_elements(
                    By.NAME,
                    'builder_rule_{0}_value_0'.format(idx))
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

                    self.click_on_element(
                        By.XPATH,
                        '(//input[@name="builder_rule_{0}_value_0"])'
                        '[{1}]'.format(idx, value_idx))
            idx += 1

        # Save the condition
        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[@type="submit"]')

        # Wait for modal close
        self.wait_for_modal_close()

    def create_condition(self, cname, cdesc, rule_tuples):
        # Switch to the condition tab
        self.select_tab('conditions-tab')

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
        self.wait_for_page(element_id='conditions')

    def edit_condition(self, oldname, cname, cdesc, rule_tuples):
        self.select_tab('conditions-tab')
        self.create_condition_base(
            '//*[contains(@class, "card-header") and text() = "{0}"]/'
            '../div[@class = "cond-buttons"]/'
            'button[contains(@class, "js-condition-edit")]'.format(oldname),
            cname,
            cdesc,
            rule_tuples)
        self.wait_for_page(element_id='conditions')

    def delete_condition(self, cname):
        """
        Given a condition name, search for it in the right DIV and click the
        buttons to remove it.
        :param cname: Condition name
        :return:
        """
        self.select_tab('conditions-tab')

        # Get the button for the condition
        self.click_on_element(
            By.XPATH,
            '//*[contains(@class, "card-header") and text() = "{0}"]/'
            '../div[@class = "cond-buttons"]/'
            'button[contains(@class, "js-condition-delete")]'.format(cname))
        # Wait for the screen to delete the condition
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//div[@id="modal-item"]/div/div/form/div/h4'),
                'Confirm condition deletion'))

        # Click in the confirm button
        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[normalize-space()="Delete '
            'condition"]')
        self.wait_for_page(element_id='conditions')

    def create_filter(self, cdesc, rule_tuples):
        # Make sure we are in the Filter tab
        self.select_tab('filter-tab')

        self.create_condition_base(
            '//button[contains(@class, "js-filter-create")]',
            None,
            cdesc,
            rule_tuples)
        # Make sure the page refreshes and shows again the filter tab
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'filter-set-header')))
        self.wait_for_page(element_id='filter')

    def edit_filter(self, cname, cdesc, rule_tuples):
        self.select_tab('filter-tab')
        self.create_condition_base(
            '//button[contains(@class, "js-filter-edit")]',
            cname,
            cdesc,
            rule_tuples)
        self.wait_for_page(element_id='filter')

    def delete_filter(self):
        # First make sure we are in the filter tab
        self.select_tab('filter-tab')

        # Click in the delete Icon
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'js-filter-delete')))
        self.click_on_element(By.CLASS_NAME, 'js-filter-delete')
        # Wait for the confirmation screen
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//div[@id="modal-item"]/div/div/form/div/h4'),
                'Confirm filter deletion'))

        # Click in the 'delete filter'
        self.click_on_element(
            By.XPATH,
            '//div[@id="modal-item"]//button[normalize-space()='
            '"Delete filter"]')
        self.wait_for_page(element_id='filter')

    def edit_attribute(self, attribute_key, nkey, nvalue):
        self.click_on_element(
            By.XPATH,
            '//table[@id="attribute-table"]'
            '//tr/td[2][normalize-space() = "{0}"]/'
            '../td[1]/div/button[1]'.format(attribute_key))
        self.wait_for_modal_open()

        # Fill out the form
        element = self.selenium.find_element(By.ID, 'id_key')
        element.clear()
        element.send_keys(nkey)
        element = self.selenium.find_element(By.ID, 'id_attr_value')
        element.clear()
        element.send_keys(nvalue)

        # Click in the create attribute button
        self.click_on_element(
            By.XPATH,
            '//div[@class="modal-footer"]/button[normalize-space()="Update '
            'attribute"]')

        # Wait for modal to close and for table to refresh
        self.wait_close_modal_refresh_table('attribute-table_previous')

    def insert_string_in_text_editor(self, id: str, message: str):
        """Given text editor ID insert the string in the text editor"""
        self.selenium.execute_script(
            """tinymce.get('{0}').execCommand('mceInsertContent', 
            false, '{1}')""".format(id, message))

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

        self.assertIsNotNone(self.selenium.find_element(By.XPATH, xpath_txt))


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
            self.selenium.find_element(
                By.XPATH,
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
            body = self.selenium.find_element(By.ID, 'base_footer')
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
