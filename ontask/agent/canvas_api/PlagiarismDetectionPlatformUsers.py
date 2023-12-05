from .etc.conf import *
from .res import *

class PlagiarismDetectionPlatformUsers(Res):
    def show(self, id, params={}):
        """
        Source Code:
            Code: Lti::UsersApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/users_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/users_api.show
        
        Scope:
            url:GET|/api/lti/users/:id

        
        Module: Plagiarism Detection Platform Users
        Function Description: Get a single user (lti)

        """
        method = "GET"
        api = f'/api/lti/users/{id}'
        return self.request(method, api, params)
        
    def group_index(self, group_id, params={}):
        """
        Source Code:
            Code: Lti::UsersApiController#group_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/users_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/users_api.group_index
        
        Scope:
            url:GET|/api/lti/groups/:group_id/users

        
        Module: Plagiarism Detection Platform Users
        Function Description: Get all users in a group (lti)

        """
        method = "GET"
        api = f'/api/lti/groups/{group_id}/users'
        return self.request(method, api, params)
        