# -*- coding: utf-8 -*-


from rest_framework import status

import test


class APIDocumentationTest(test.OnTaskTestCase):
    fixtures = ['initial_db']

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow = None

    def test_api_doc(self):
        """Test the availability of the API doc."""

        resp = self.get_response('ontask-api-doc')
        resp.render()
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('OnTask API', str(resp.content))
