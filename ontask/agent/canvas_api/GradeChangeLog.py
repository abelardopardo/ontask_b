from .etc.conf import *
from .res import *

class GradeChangeLog(Res):
    def for_assignment(self, assignment_id, params={}):
        """
        Source Code:
            Code: GradeChangeAuditApiController#for_assignment,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grade_change_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grade_change_audit_api.for_assignment
        
        Scope:
            url:GET|/api/v1/audit/grade_change/assignments/:assignment_id

        
        Module: Grade Change Log
        Function Description: Query by assignment

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/grade_change/assignments/{assignment_id}'
        return self.request(method, api, params)
        
    def for_course(self, course_id, params={}):
        """
        Source Code:
            Code: GradeChangeAuditApiController#for_course,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grade_change_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grade_change_audit_api.for_course
        
        Scope:
            url:GET|/api/v1/audit/grade_change/courses/:course_id

        
        Module: Grade Change Log
        Function Description: Query by course

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/grade_change/courses/{course_id}'
        return self.request(method, api, params)
        
    def for_student(self, student_id, params={}):
        """
        Source Code:
            Code: GradeChangeAuditApiController#for_student,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grade_change_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grade_change_audit_api.for_student
        
        Scope:
            url:GET|/api/v1/audit/grade_change/students/:student_id

        
        Module: Grade Change Log
        Function Description: Query by student

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/grade_change/students/{student_id}'
        return self.request(method, api, params)
        
    def for_grader(self, grader_id, params={}):
        """
        Source Code:
            Code: GradeChangeAuditApiController#for_grader,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grade_change_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grade_change_audit_api.for_grader
        
        Scope:
            url:GET|/api/v1/audit/grade_change/graders/:grader_id

        
        Module: Grade Change Log
        Function Description: Query by grader

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want events.
            end_time   | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/grade_change/graders/{grader_id}'
        return self.request(method, api, params)
        
    def query(self, params={}):
        """
        Source Code:
            Code: GradeChangeAuditApiController#query,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grade_change_audit_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grade_change_audit_api.query
        
        Scope:
            url:GET|/api/v1/audit/grade_change

        
        Module: Grade Change Log
        Function Description: Advanced query

        Parameter Desc:
            course_id     | |integer  |Restrict query to events in the specified course.
            assignment_id | |integer  |Restrict query to the given assignment. If `override` is given, query the course final grade override instead.
            student_id    | |integer  |User id of a student to search grading events for.
            grader_id     | |integer  |User id of a grader to search grading events for.
            start_time    | |DateTime |The beginning of the time range from which you want events.
            end_time      | |DateTime |The end of the time range from which you want events.
        """
        method = "GET"
        api = f'/api/v1/audit/grade_change'
        return self.request(method, api, params)
        