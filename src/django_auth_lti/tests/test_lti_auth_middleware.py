import unittest
import mock
from mock import patch
from django.test import RequestFactory
from django.contrib.auth import models
from django_auth_lti.middleware_patched import MultiLTILaunchAuthMiddleware


@patch('django_auth_lti.middleware.logger')
class TestLTIAuthMiddleware(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mw = MultiLTILaunchAuthMiddleware()

    def build_lti_launch_request(self, post_data):
        """
        Utility method that builds a fake lti launch request with custom data.
        """
        # Add message type to post data
        post_data.update(lti_message_type='basic-lti-launch-request')
        # Add resource_link_id to post data
        post_data.update(resource_link_id='d202fb112a14f27107149ed874bf630aa8e029a5')

        request = RequestFactory().post('/fake/lti/launch', post_data)
        request.user = mock.Mock(name='User', spec=models.User)
        request.session = {}
        return request

    @patch('django_auth_lti.middleware.auth')
    def test_roles_merged_with_custom_roles(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains merged set of roles when custom role key is
        defined and values have been passed in.
        """
        request = self.build_lti_launch_request({
            'roles': 'RoleOne,RoleTwo',
            'test_custom_role_key': 'My,Custom,Roles',
        })
        with patch('django_auth_lti.middleware.settings', LTI_CUSTOM_ROLE_KEY='test_custom_role_key'):
            self.mw.process_request(request)
        self.assertEqual(request.LTI.get('roles'), ['RoleOne', 'RoleTwo', 'My', 'Custom', 'Roles'])

    @patch('django_auth_lti.middleware.auth')
    def test_roles_merge_with_empty_custom_roles(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains original set when custom role key is defined with empty data.
        """
        request = self.build_lti_launch_request({
            'roles': 'RoleOne,RoleTwo',
            'test_custom_role_key': '',
        })
        with patch('django_auth_lti.middleware.settings', LTI_CUSTOM_ROLE_KEY='test_custom_role_key'):
            self.mw.process_request(request)
        self.assertEqual(request.LTI.get('roles'), ['RoleOne', 'RoleTwo'])

    @patch('django_auth_lti.middleware.auth')
    def test_roles_not_merged_with_no_role_key(self, mock_auth, mock_logger):
        """
        Assert that 'roles' list in session contains original set when no custom role key is defined.
        """
        request = self.build_lti_launch_request({
            'roles': 'RoleOne,RoleTwo',
            'test_custom_role_key': 'My,Custom,Roles',
        })
        self.mw.process_request(request)
        self.assertEqual(request.LTI.get('roles'), ['RoleOne', 'RoleTwo'])
