from .etc.conf import *
from .res import *

class OutcomeImports(Res):
    def create(self, account_id, learning_outcome_group_id, params={}):
        """
        Source Code:
            Code: OutcomeImportsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_imports_api.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/outcome_imports(/group/:learning_outcome_group_id)
            url:POST|/api/v1/courses/:course_id/outcome_imports(/group/:learning_outcome_group_id)

        
        Module: Outcome Imports
        Function Description: Import Outcomes

        Parameter Desc:
            import_type | |string |Choose the data format for reading outcome data. With a standard Canvas install, this option can only be ‘instructure_csv’, and if unprovided, will be assumed to be so. Can be part of the query string.
            attachment  | |string |There are two ways to post outcome import data - either via a multipart/form-data form-field-style attachment, or via a non-multipart raw post request.                                   ‘attachment’ is required for multipart/form-data style posts. Assumed to be outcome data from a file upload form field named ‘attachment’.                                   Examples:                                   curl -F attachment=@<filename> -H "Authorization: Bearer <token>" \                                       'https://<canvas>/api/v1/accounts/<account_id>/outcome_imports?import_type=instructure_csv'                                   curl -F attachment=@<filename> -H "Authorization: Bearer <token>" \                                       'https://<canvas>/api/v1/courses/<course_id>/outcome_imports?import_type=instructure_csv'                                   If you decide to do a raw post, you can skip the ‘attachment’ argument, but you will then be required to provide a suitable Content-Type header. You are encouraged to also provide the ‘extension’ argument.                                   Examples:                                   curl -H 'Content-Type: text/csv' --data-binary @<filename>.csv \                                       -H "Authorization: Bearer <token>" \                                       'https://<canvas>/api/v1/accounts/<account_id>/outcome_imports?import_type=instructure_csv'                                   curl -H 'Content-Type: text/csv' --data-binary @<filename>.csv \                                       -H "Authorization: Bearer <token>" \                                       'https://<canvas>/api/v1/courses/<course_id>/outcome_imports?import_type=instructure_csv'
            extension   | |string |Recommended for raw post request style imports. This field will be used to distinguish between csv and other file format extensions that would usually be provided with the filename in the multipart post request scenario. If not provided, this value will be inferred from the Content-Type, falling back to csv-file format if all else fails.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/outcome_imports(/group/{learning_outcome_group_id}'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: OutcomeImportsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_imports_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/outcome_imports/:id
            url:GET|/api/v1/courses/:course_id/outcome_imports/:id

        
        Module: Outcome Imports
        Function Description: Get Outcome import status

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/outcome_imports/{id}'
        return self.request(method, api, params)
        
    def created_group_ids(self, account_id, id, params={}):
        """
        Source Code:
            Code: OutcomeImportsApiController#created_group_ids,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_imports_api.created_group_ids
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/outcome_imports/:id/created_group_ids
            url:GET|/api/v1/courses/:course_id/outcome_imports/:id/created_group_ids

        
        Module: Outcome Imports
        Function Description: Get IDs of outcome groups created after successful import

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/outcome_imports/{id}/created_group_ids'
        return self.request(method, api, params)
        