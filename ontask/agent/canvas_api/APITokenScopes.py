from .etc.conf import *
from .res import *

class APITokenScopes(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: ScopesApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/scopes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.scopes_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/scopes

        
        Module: API Token Scopes
        Function Description: List scopes

        Parameter Desc:
            group_by | |string |The attribute to group the scopes by. By default no grouping is done.                                Allowed values: resource_name
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/scopes'
        return self.request(method, api, params)
        