from .etc.conf import *
from .res import *

class GradingStandards(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: GradingStandardsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_standards_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_standards_api.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/grading_standards
            url:POST|/api/v1/courses/:course_id/grading_standards

        
        Module: Grading Standards
        Function Description: Create a new grading standard

        Parameter Desc:
            title                         |Required |string  |The title for the Grading Standard.
            grading_scheme_entry[][name]  |Required |string  |The name for an entry value within a GradingStandard that describes the range of the value e.g. A-
            grading_scheme_entry[][value] |Required |integer |The value for the name of the entry within a GradingStandard. The entry represents the lower bound of the range for the entry. This range includes the value up to the next entry in the GradingStandard, or 100 if there is no upper bound. The lowest value will have a lower bound range of 0. e.g. 93

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/grading_standards \
              -X POST \
              -H 'Authorization: Bearer <token>' \
              -d 'title=New standard name' \
              -d 'grading_scheme_entry[][name]=A'
              -d 'grading_scheme_entry[][value]=90'
              -d 'grading_scheme_entry[][name]=B'
              -d 'grading_scheme_entry[][value]=80'

        Response Example: 
            {
              "title": "New standard name",
              "id": 1,
              "context_id": 1,
              "context_type": "Course",
              "grading_scheme": [
                {"name": "A", "value": 0.9},
                {"name": "B", "value": 0.8}
              ]
            }
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/grading_standards'
        return self.request(method, api, params)
        
    def context_index(self, course_id, params={}):
        """
        Source Code:
            Code: GradingStandardsApiController#context_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_standards_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_standards_api.context_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/grading_standards
            url:GET|/api/v1/accounts/:account_id/grading_standards

        
        Module: Grading Standards
        Function Description: List the grading standards available in a context.

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/grading_standards'
        return self.request(method, api, params)
        
    def context_show(self, course_id, grading_standard_id, params={}):
        """
        Source Code:
            Code: GradingStandardsApiController#context_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_standards_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_standards_api.context_show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/grading_standards/:grading_standard_id
            url:GET|/api/v1/accounts/:account_id/grading_standards/:grading_standard_id

        
        Module: Grading Standards
        Function Description: Get a single grading standard in a context.

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/grading_standards/{grading_standard_id}'
        return self.request(method, api, params)
        