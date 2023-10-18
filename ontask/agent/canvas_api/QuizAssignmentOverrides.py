from .etc.conf import *
from .res import *

class QuizAssignmentOverrides(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizAssignmentOverridesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_assignment_overrides.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/assignment_overrides

        
        Module: Quiz Assignment Overrides
        Function Description: Retrieve assignment-overridden dates for Classic Quizzes

        Parameter Desc:
            quiz_assignment_overrides[0][quiz_ids][] | |integer |An array of quiz IDs. If omitted, overrides for all quizzes available to the operating user will be returned.

        Response Example: 
            {
               "quiz_assignment_overrides": [{
                 "quiz_id": "1",
                 "due_dates": [QuizAssignmentOverride],
                 "all_dates": [QuizAssignmentOverride]
               },{
                 "quiz_id": "2",
                 "due_dates": [QuizAssignmentOverride],
                 "all_dates": [QuizAssignmentOverride]
               }]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/assignment_overrides'
        return self.request(method, api, params)
        
    def new_quizzes(self, course_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizAssignmentOverridesController#new_quizzes,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_assignment_overrides.new_quizzes
        
        Scope:
            url:GET|/api/v1/courses/:course_id/new_quizzes/assignment_overrides

        
        Module: Quiz Assignment Overrides
        Function Description: Retrieve assignment-overridden dates for New Quizzes

        Parameter Desc:
            quiz_assignment_overrides[0][quiz_ids][] | |integer |An array of quiz IDs. If omitted, overrides for all quizzes available to the operating user will be returned.

        Response Example: 
            {
               "quiz_assignment_overrides": [{
                 "quiz_id": "1",
                 "due_dates": [QuizAssignmentOverride],
                 "all_dates": [QuizAssignmentOverride]
               },{
                 "quiz_id": "2",
                 "due_dates": [QuizAssignmentOverride],
                 "all_dates": [QuizAssignmentOverride]
               }]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/new_quizzes/assignment_overrides'
        return self.request(method, api, params)
        