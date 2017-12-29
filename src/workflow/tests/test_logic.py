# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import gzip
import os

from django.conf import settings
from django.urls import reverse
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import test
from dataops import pandas_db
from workflow.models import Workflow
from workflow.ops import do_export_workflow


class WorkflowImportExport(test.OntaskTestCase):
    fixtures = ['simple_workflow_export']
    filename = os.path.join(
        settings.BASE_DIR(),
        'workflow',
        'fixtures',
        'simple_workflow_export_df.sql'
    )

    def test_export(self):
        # Get the only workflow
        workflow = Workflow.objects.get(name='wflow1')

        # Export data only
        response = do_export_workflow(workflow,
                                      workflow.actions.all())

        self.assertEqual(response.get('Content-Encoding'),
                         'application/gzip')
        self.assertEqual(response.get('Content-Disposition'),
                         'attachment; filename="ontask_workflow.gz"')

        # Process the file
        data_in = gzip.GzipFile(fileobj=BytesIO(response.content))
        data = JSONParser().parse(data_in)

        # Compare the data with the current workflow
        self.assertEqual(workflow.actions.all().count(),
                         len(data['actions']))
        self.assertEqual(workflow.nrows,
                         data['nrows'])
        self.assertEqual(workflow.ncols,
                         data['ncols'])
        self.assertEqual(workflow.attributes, data['attributes'])
        self.assertEqual(workflow.query_builder_ops, data['query_builder_ops'])


class WorkflowImport(test.OntaskLiveTestCase):
    fixtures = ['simple_workflow_export']
    filename = os.path.join(
        settings.BASE_DIR(),
        'workflow',
        'fixtures',
        'simple_workflow_export_df.sql'
    )

    def setUp(self):
        super(WorkflowImport, self).setUp()
        pandas_db.pg_restore_table(self.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(WorkflowImport, self).tearDown()

    def test_import_complete(self):

        # Login and wait for the table of workflows
        self.login('instructor1@bogus.com')

        self.open(reverse('workflow:index'))
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//body/div/p/a"),
                'Import')
        )

        # Click in the import button and wait
        self.selenium.find_element_by_link_text('Import').click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'page-header'),
                                             'Import Workflow')
        )

        # Set the workflow name and file
        wname = self.selenium.find_element_by_id('id_name')
        wname.send_keys('newwf')
        wfile = self.selenium.find_element_by_id('id_file')
        wfile.send_keys(os.path.join(settings.BASE_DIR,
                                     'workflow',
                                     'fixtures',
                                     'ontask_workflow.gz'))

        # Click in the submit
        self.selenium.find_element_by_xpath(
            "//button[@type='Submit']"
        ).click()
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//table['workflow-table']/tbody/tr/td/a"),
                'newwf')
        )

        # Check elements in workflow and in newwf
        w1 = Workflow.objects.get(name=test.wflow_name)
        w2 = Workflow.objects.get(name='newwf')

        # Equal descriptions
        self.assertEqual(w1.description_text,
                         w2.description_text)

        # Equal number of columns
        self.assertEqual(w1.columns.all().count(), w2.columns.all().count())

        # Identical attributes
        self.assertEqual(w1.attributes, w2.attributes)

        # Equal number of rows and columns
        self.assertEqual(w1.nrows, w2.nrows)
        self.assertEqual(w1.ncols, w2.ncols)

        # Equal names and column types
        for x, y in zip(w1.columns.all(), w2.columns.all()):
            self.assertEqual(x.name, y.name)
            self.assertEqual(x.data_type, y.data_type)
            self.assertEqual(x.is_key, y.is_key)

        # Equal number of actions
        self.assertEqual(w1.actions.all().count(),
                         w2.actions.all().count())

        # Equal names and content in the conditions
        for x, y in zip(w1.actions.all(), w2.actions.all()):
            self.assertEqual(x.name, y.name)
            self.assertEqual(x.description_text, y.description_text)
            self.assertEqual(x.content, y.content)
            self.assertEqual(x.conditions.all().count(),
                             y.conditions.all().count())
            for c1, c2 in zip(x.conditions.all(), y.conditions.all()):
                self.assertEqual(c1.name, c2.name)
                self.assertEqual(c1.description_text,
                                 c2.description_text)
                self.assertEqual(c1.formula, c2.formula)
                self.assertEqual(c1.is_filter, c2.is_filter)

        # End of session
        self.logout()

        # Close the db_engine
        pandas_db.destroy_db_engine(pandas_db.engine)
