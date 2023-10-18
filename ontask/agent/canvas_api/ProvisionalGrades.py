from .etc.conf import *
from .res import *

class ProvisionalGrades(Res):
    def bulk_select(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: ProvisionalGradesController#bulk_select,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/provisional_grades_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.provisional_grades.bulk_select
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/provisional_grades/bulk_select

        
        Module: Provisional Grades
        Function Description: Bulk select provisional grades


        Response Example: 
            [{
              "assignment_id": 867,
              "student_id": 5309,
              "selected_provisional_grade_id": 53669
            }]
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/provisional_grades/bulk_select'
        return self.request(method, api, params)
        
    def status(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: ProvisionalGradesController#status,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/provisional_grades_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.provisional_grades.status
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/provisional_grades/status

        
        Module: Provisional Grades
        Function Description: Show provisional grade status for a student

        Parameter Desc:
            student_id | |integer |The id of the student to show the status for

        Request Example: 
            curl 'https://<canvas>/api/v1/courses/1/assignments/2/provisional_grades/status?student_id=1'

        Response Example: 
            { "needs_provisional_grade": false }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/provisional_grades/status'
        return self.request(method, api, params)
        
    def select(self, course_id, assignment_id, provisional_grade_id, params={}):
        """
        Source Code:
            Code: ProvisionalGradesController#select,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/provisional_grades_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.provisional_grades.select
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/provisional_grades/:provisional_grade_id/select

        
        Module: Provisional Grades
        Function Description: Select provisional grade


        Response Example: 
            {
              "assignment_id": 867,
              "student_id": 5309,
              "selected_provisional_grade_id": 53669
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/provisional_grades/{provisional_grade_id}/select'
        return self.request(method, api, params)
        
    def publish(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: ProvisionalGradesController#publish,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/provisional_grades_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.provisional_grades.publish
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/provisional_grades/publish

        
        Module: Provisional Grades
        Function Description: Publish provisional grades for an assignment

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/provisional_grades/publish'
        return self.request(method, api, params)
        