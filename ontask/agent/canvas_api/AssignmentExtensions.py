from .etc.conf import *
from .res import *

class AssignmentExtensions(Res):
    def create(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentExtensionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_extensions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_extensions.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/extensions

        
        Module: Assignment Extensions
        Function Description: Set extensions for student assignment submissions

        Parameter Desc:
            assignment_extensions[][user_id]        |Required |integer |The ID of the user we want to add assignment extensions for.
            assignment_extensions[][extra_attempts] |Required |integer |Number of times the student is allowed to re-take the assignment over the limit.

        Request Example: 
            {
              "assignment_extensions": [{
                "user_id": 3,
                "extra_attempts": 2
              },{
                "user_id": 2,
                "extra_attempts": 2
              }]
            }

        Response Example: 
            {
              "assignment_extensions": [AssignmentExtension]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/extensions'
        return self.request(method, api, params)
        