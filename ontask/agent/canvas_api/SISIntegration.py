from .etc.conf import *
from .res import *

class SISIntegration(Res):
    def sis_assignments(self, account_id, params={}):
        """
        Source Code:
            Code: SisApiController#sis_assignments,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_api.sis_assignments
        
        Scope:
            url:GET|/api/sis/accounts/:account_id/assignments
            url:GET|/api/sis/courses/:course_id/assignments

        
        Module: SIS Integration
        Function Description: Retrieve assignments enabled for grade export to SIS

        Parameter Desc:
            account_id    | |integer  |The ID of the account to query.
            course_id     | |integer  |The ID of the course to query.
            starts_before | |DateTime |When searching on an account,
            ends_after    | |DateTime |When searching on an account,
            include       | |string   |Array of additional                                       Allowed values: student_overrides
        """
        method = "GET"
        api = f'/api/sis/accounts/{account_id}/assignments'
        return self.request(method, api, params)
        
    def disable_post_to_sis(self, course_id, params={}):
        """
        Source Code:
            Code: DisablePostToSisApiController#disable_post_to_sis,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/disable_post_to_sis_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.disable_post_to_sis_api.disable_post_to_sis
        
        Scope:
            url:PUT|/api/sis/courses/:course_id/disable_post_to_sis

        
        Module: SIS Integration
        Function Description: Disable assignments currently enabled for grade export to SIS

        Parameter Desc:
            course_id         | |integer |The ID of the course.
            grading_period_id | |integer |The ID of the grading period.
        """
        method = "PUT"
        api = f'/api/sis/courses/{course_id}/disable_post_to_sis'
        return self.request(method, api, params)
        