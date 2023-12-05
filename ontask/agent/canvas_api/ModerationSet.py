from .etc.conf import *
from .res import *

class ModerationSet(Res):
    def index(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: ModerationSetController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/moderation_set_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.moderation_set.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/moderated_students

        
        Module: Moderation Set
        Function Description: List students selected for moderation

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/moderated_students'
        return self.request(method, api, params)
        
    def create(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: ModerationSetController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/moderation_set_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.moderation_set.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/moderated_students

        
        Module: Moderation Set
        Function Description: Select students for moderation

        Parameter Desc:
            student_ids[] | |number |user ids for students to select for moderation
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/moderated_students'
        return self.request(method, api, params)
        