from .etc.conf import *
from .res import *

class ContentSecurityPolicySettings(Res):
    def get_csp_settings(self, course_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#get_csp_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.get_csp_settings
        
        Scope:
            url:GET|/api/v1/courses/:course_id/csp_settings
            url:GET|/api/v1/accounts/:account_id/csp_settings

        
        Module: Content Security Policy Settings
        Function Description: Get current settings for account or course

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/csp_settings'
        return self.request(method, api, params)
        
    def set_csp_setting(self, course_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#set_csp_setting,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.set_csp_setting
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/csp_settings
            url:PUT|/api/v1/accounts/:account_id/csp_settings

        
        Module: Content Security Policy Settings
        Function Description: Enable, disable, or clear explicit CSP setting

        Parameter Desc:
            status |Required |string |If set to `enabled` for an account, CSP will be enabled for all its courses and sub-accounts (that have not explicitly enabled or disabled it), using the allowed domains set on this account. If set to `disabled`, CSP will be disabled for this account or course and for all sub-accounts that have not explicitly re-enabled it. If set to `inherited`, this account or course will reset to the default state where CSP settings are inherited from the first parent account to have them explicitly set.                                      Allowed values: enabled, disabled, inherited
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/csp_settings'
        return self.request(method, api, params)
        
    def set_csp_lock(self, account_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#set_csp_lock,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.set_csp_lock
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/csp_settings/lock

        
        Module: Content Security Policy Settings
        Function Description: Lock or unlock current CSP settings for sub-accounts and courses

        Parameter Desc:
            settings_locked |Required |boolean |Whether sub-accounts and courses will be prevented from overriding settings inherited from this account.
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/csp_settings/lock'
        return self.request(method, api, params)
        
    def add_domain(self, account_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#add_domain,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.add_domain
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/csp_settings/domains

        
        Module: Content Security Policy Settings
        Function Description: Add an allowed domain to account

        Parameter Desc:
            domain |Required |string |no description
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/csp_settings/domains'
        return self.request(method, api, params)
        
    def add_multiple_domains(self, account_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#add_multiple_domains,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.add_multiple_domains
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/csp_settings/domains/batch_create

        
        Module: Content Security Policy Settings
        Function Description: Add multiple allowed domains to an account

        Parameter Desc:
            domains |Required |Array |no description
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/csp_settings/domains/batch_create'
        return self.request(method, api, params)
        
    def csp_log(self, account_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#csp_log,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.csp_log
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/csp_log

        
        Module: Content Security Policy Settings
        Function Description: Retrieve reported CSP Violations for account

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/csp_log'
        return self.request(method, api, params)
        
    def remove_domain(self, account_id, params={}):
        """
        Source Code:
            Code: CspSettingsController#remove_domain,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/csp_settings_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.csp_settings.remove_domain
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/csp_settings/domains

        
        Module: Content Security Policy Settings
        Function Description: Remove a domain from account

        Parameter Desc:
            domain |Required |string |no description
        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/csp_settings/domains'
        return self.request(method, api, params)
        