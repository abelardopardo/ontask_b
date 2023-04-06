"""Create screen captures for theAPI to include in the documentation."""

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ontask import models, tests


class ScreenAPITutorialTest(tests.InitialWorkflowFixture, tests.ScreenTests):
    def test(self):
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
