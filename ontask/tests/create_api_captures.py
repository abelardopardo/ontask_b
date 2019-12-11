# -*- coding: utf-8 -*-

"""Create screen captures for theAPI to include in the documentation."""
import os

from django.conf import settings
from django.urls import reverse
from future import standard_library
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ontask import models
from ontask.tests import ScreenTests

standard_library.install_aliases()


class ScreenAPITutorialTest(ScreenTests):
    fixtures = ['ontask/tests/initial_workflow/initial_workflow.json']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql'
    )

    def test_api(self):
        # Login
        self.login('instructor01@bogus.com')

        self.open(reverse('ontask-api-doc'))
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="django-session-auth"]')
            )
        )
        self.body_ss('api_documentation.png')

        self.open('/workflow/workflows/')
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="content"]')
            )
        )
        self.body_ss('api_workflow_list.png')

        workflow = models.Workflow.objects.all()[0]

        self.open('/workflow/{0}/rud/'.format(workflow.id))
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//form[@id="get-form"]')
            )
        )
        self.body_ss('api_workflow_detail.png')


        self.open('/table/{0}/ops/'.format(workflow.id))
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[@id="content"]')
            )
        )
        self.body_ss('api_table.png')


        # End of session
        self.logout()
