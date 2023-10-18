from .etc.conf import *
from .res import *

class InstAccesstokens(Res):
    def create(self, params={}):
        """
        Source Code:
            Code: InstAccessTokensController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/inst_access_tokens_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.inst_access_tokens.create
        
        Scope:
            url:POST|/api/v1/inst_access_tokens

        
        Module: InstAccess tokens
        Function Description: Create InstAccess token

        """
        method = "POST"
        api = f'/api/v1/inst_access_tokens'
        return self.request(method, api, params)
        