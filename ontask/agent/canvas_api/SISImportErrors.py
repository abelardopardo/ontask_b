from .etc.conf import *
from .res import *

class SISImportErrors(Res):
    def index(self, account_id, id, params={}):
        """
        Source Code:
            Code: SisImportErrorsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_import_errors_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_import_errors_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sis_imports/:id/errors
            url:GET|/api/v1/accounts/:account_id/sis_import_errors

        
        Module: SIS Import Errors
        Function Description: Get SIS import error list

        Parameter Desc:
            failure | |boolean |If set, only shows errors on a sis import that would cause a failure.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sis_imports/{id}/errors'
        return self.request(method, api, params)
        