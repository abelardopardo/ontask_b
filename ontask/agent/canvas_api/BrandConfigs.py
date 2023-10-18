from .etc.conf import *
from .res import *

class BrandConfigs(Res):
    def show(self, params={}):
        """
        Source Code:
            Code: BrandConfigsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/brand_configs_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.brand_configs_api.show
        
        Scope:
            url:GET|/api/v1/brand_variables

        
        Module: Brand Configs
        Function Description: Get the brand config variables that should be used for this domain

        """
        method = "GET"
        api = f'/api/v1/brand_variables'
        return self.request(method, api, params)
        