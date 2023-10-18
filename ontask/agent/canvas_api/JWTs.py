from .etc.conf import *
from .res import *

class JWTs(Res):
    def create(self, params={}):
        """
        Source Code:
            Code: JwtsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/jwts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.jwts.create
        
        Scope:
            url:POST|/api/v1/jwts

        
        Module: JWTs
        Function Description: Create JWT

        Parameter Desc:
            workflows[]  | |string  |Adds additional data to the JWT to be used by the consuming service workflow
            context_type | |string  |The type of the context in case a specified workflow uses it to consuming the service. Case insensitive.                                     Allowed values: Course, User, Account
            context_id   | |integer |The id of the context in case a specified workflow uses it to consuming the service.
            context_uuid | |string  |The uuid of the context in case a specified workflow uses it to consuming the service.
        """
        method = "POST"
        api = f'/api/v1/jwts'
        return self.request(method, api, params)
        
    def refresh(self, params={}):
        """
        Source Code:
            Code: JwtsController#refresh,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/jwts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.jwts.refresh
        
        Scope:
            url:POST|/api/v1/jwts/refresh

        
        Module: JWTs
        Function Description: Refresh JWT

        Parameter Desc:
            jwt |Required |string |An existing JWT token to be refreshed. The new token will have the same context and workflows as the existing token.
        """
        method = "POST"
        api = f'/api/v1/jwts/refresh'
        return self.request(method, api, params)
        