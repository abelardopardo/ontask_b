from .etc.conf import *
from .res import *

class AuthenticationsLog(Res):
    def for_login(self, login_id, params={}):
        """
        Source Code:
            Code: AuthenticationAuditApiController#for_login,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_audit_api.for_login
        
        Scope:
            url:GET|/api/v1/audit/authentication/logins/:login_id

        
        Module: Authentications Log
        Function Description: Query by login.

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events. Events are stored for one year.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/authentication/logins/{login_id}'
        return self.request(method, api, params)
        
    def for_account(self, account_id, params={}):
        """
        Source Code:
            Code: AuthenticationAuditApiController#for_account,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_audit_api.for_account
        
        Scope:
            url:GET|/api/v1/audit/authentication/accounts/:account_id

        
        Module: Authentications Log
        Function Description: Query by account.

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events. Events are stored for one year.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/authentication/accounts/{account_id}'
        return self.request(method, api, params)
        
    def for_user(self, user_id, params={}):
        """
        Source Code:
            Code: AuthenticationAuditApiController#for_user,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_audit_api.for_user
        
        Scope:
            url:GET|/api/v1/audit/authentication/users/:user_id

        
        Module: Authentications Log
        Function Description: Query by user.

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events. Events are stored for one year.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/authentication/users/{user_id}'
        return self.request(method, api, params)
        