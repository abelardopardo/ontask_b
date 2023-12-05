from .etc.conf import *
from .res import *

class Accounts_LTI(Res):
    def show(self, account_id, params={}):
        """
        Source Code:
            Code: Lti::AccountLookupController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/account_lookup_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/account_lookup.show
        
        Scope:
            url:GET|/api/lti/accounts/:account_id

        
        Module: Accounts (LTI)
        Function Description: Get account

        """
        method = "GET"
        api = f'/api/lti/accounts/{account_id}'
        return self.request(method, api, params)
        