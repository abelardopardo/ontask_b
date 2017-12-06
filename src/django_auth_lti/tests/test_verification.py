from unittest import TestCase
from mock import MagicMock
from django_auth_lti.verification import is_allowed
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

class TestVerification(TestCase):
    
    def test_is_allowed_config_failure(self):
        request = MagicMock(LTI={})
        allowed_roles = ["admin", "student"]
        self.assertRaises(ImproperlyConfigured, is_allowed,
                          request, allowed_roles, False)
    
    def test_is_allowed_success(self):
        request = MagicMock(LTI={"roles": ["admin"]})
        allowed_roles = ["admin", "student"]
        user_is_allowed = is_allowed(request, allowed_roles, False)
        self.assertTrue(user_is_allowed)
    
    def test_is_allowed_success_one_role(self):
        request = MagicMock(LTI={"roles": ["admin"]})
        allowed_roles = "admin"
        user_is_allowed = is_allowed(request, allowed_roles, False)
        self.assertTrue(user_is_allowed)
    
    def test_is_allowed_failure(self):
        request = MagicMock(LTI={"roles":[]})
        allowed_roles = ["admin", "student"]
        user_is_allowed = is_allowed(request, allowed_roles, False)
        self.assertFalse(user_is_allowed)
    
    def test_is_allowed_failure_one_role(self):
        request = MagicMock(LTI={"roles":[]})
        allowed_roles = "admin"
        user_is_allowed = is_allowed(request, allowed_roles, False)
        self.assertFalse(user_is_allowed)
    
    def test_is_allowed_exception(self):
        request = MagicMock(LTI={"roles":["TF"]})
        allowed_roles = ["admin", "student"]
        self.assertRaises(PermissionDenied, is_allowed,
                          request, allowed_roles, True)
