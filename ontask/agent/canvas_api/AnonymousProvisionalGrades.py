from .etc.conf import *
from .res import *

class AnonymousProvisionalGrades(Res):
    def status(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: AnonymousProvisionalGradesController#status,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/anonymous_provisional_grades_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.anonymous_provisional_grades.status
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/anonymous_provisional_grades/status

        
        Module: Anonymous Provisional Grades
        Function Description: Show provisional grade status for a student

        Parameter Desc:
            anonymous_id | |string |The id of the student to show the status for

        Request Example: 
            curl 'https://<canvas>/api/v1/courses/1/assignments/2/anonymous_provisional_grades/status?anonymous_id=1'

        Response Example: 
            { "needs_provisional_grade": false }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/anonymous_provisional_grades/status'
        return self.request(method, api, params)
        