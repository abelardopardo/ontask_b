from .etc.conf import *
from .res import *

class Conferences(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: ConferencesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conferences.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/conferences
            url:GET|/api/v1/groups/:group_id/conferences

        
        Module: Conferences
        Function Description: List conferences

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/conferences'
        return self.request(method, api, params)
        
    def for_user(self, params={}):
        """
        Source Code:
            Code: ConferencesController#for_user,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/conferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.conferences.for_user
        
        Scope:
            url:GET|/api/v1/conferences

        
        Module: Conferences
        Function Description: List conferences for the current user

        Parameter Desc:
            state | |string |If set to `live`, returns only conferences that are live (i.e., have started and not finished yet). If omitted, returns all conferences for this user’s groups and courses.
        """
        method = "GET"
        api = f'/api/v1/conferences'
        return self.request(method, api, params)
        