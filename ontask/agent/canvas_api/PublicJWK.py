from .etc.conf import *
from .res import *

class PublicJWK(Res):
    def update(self, params={}):
        """
        Source Code:
            Code: Lti::PublicJwkController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/public_jwk_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/public_jwk.update
        
        Scope:
            url:PUT|/api/lti/developer_key/update_public_jwk

        
        Module: Public JWK
        Function Description: Update Public JWK

        Parameter Desc:
            public_jwk |Required |json |The new public jwk that will be set to the tools current public jwk.
        """
        method = "PUT"
        api = f'/api/lti/developer_key/update_public_jwk'
        return self.request(method, api, params)
        