from .etc.conf import *
from .res import *

class CourseAuditlog(Res):
    def for_course(self, course_id, params={}):
        """
        Source Code:
            Code: CourseAuditApiController#for_course,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_audit_api.for_course
        
        Scope:
            url:GET|/api/v1/audit/course/courses/:course_id

        
        Module: Course Audit log
        Function Description: Query by course.

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/course/courses/{course_id}'
        return self.request(method, api, params)
        
    def for_account(self, account_id, params={}):
        """
        Source Code:
            Code: CourseAuditApiController#for_account,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_audit_api.for_account
        
        Scope:
            url:GET|/api/v1/audit/course/accounts/:account_id

        
        Module: Course Audit log
        Function Description: Query by account.

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/course/accounts/{account_id}'
        return self.request(method, api, params)
        