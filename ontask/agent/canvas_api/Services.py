from .etc.conf import *
from .res import *

class Services(Res):
    def show_kaltura_config(self, params={}):
        """
        Source Code:
            Code: ServicesApiController#show_kaltura_config,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/services_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.services_api.show_kaltura_config
        
        Scope:
            url:GET|/api/v1/services/kaltura

        
        Module: Services
        Function Description: Get Kaltura config


        Response Example: 
            # For an enabled Kaltura plugin:
            {
              'domain': 'kaltura.example.com',
              'enabled': true,
              'partner_id': '123456',
              'resource_domain': 'cdn.kaltura.example.com',
              'rtmp_domain': 'rtmp.example.com'
            }
            
            # For a disabled or unconfigured Kaltura plugin:
            {
              'enabled': false
            }
        """
        method = "GET"
        api = f'/api/v1/services/kaltura'
        return self.request(method, api, params)
        
    def start_kaltura_session(self, params={}):
        """
        Source Code:
            Code: ServicesApiController#start_kaltura_session,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/services_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.services_api.start_kaltura_session
        
        Scope:
            url:POST|/api/v1/services/kaltura_session

        
        Module: Services
        Function Description: Start Kaltura session


        Response Example: 
            {
              'ks': '1e39ad505f30c4fa1af5752b51bd69fe'
            }
        """
        method = "POST"
        api = f'/api/v1/services/kaltura_session'
        return self.request(method, api, params)
        