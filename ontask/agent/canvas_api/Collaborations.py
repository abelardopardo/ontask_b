from .etc.conf import *
from .res import *

class Collaborations(Res):
    def api_index(self, course_id, params={}):
        """
        Source Code:
            Code: CollaborationsController#api_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/collaborations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.collaborations.api_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/collaborations
            url:GET|/api/v1/groups/:group_id/collaborations

        
        Module: Collaborations
        Function Description: List collaborations

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/collaborations'
        return self.request(method, api, params)
        
    def members(self, id, params={}):
        """
        Source Code:
            Code: CollaborationsController#members,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/collaborations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.collaborations.members
        
        Scope:
            url:GET|/api/v1/collaborations/:id/members

        
        Module: Collaborations
        Function Description: List members of a collaboration.

        Parameter Desc:
            include[] | |string |`collaborator_lti_id`: Optional information to include with each member. Represents an identifier to be used for the member in an LTI context.                                 `avatar_image_url`: Optional information to include with each member. The url for the avatar of a collaborator with type ‘user’.                                 Allowed values: collaborator_lti_id, avatar_image_url
        """
        method = "GET"
        api = f'/api/v1/collaborations/{id}/members'
        return self.request(method, api, params)
        
    def potential_collaborators(self, course_id, params={}):
        """
        Source Code:
            Code: CollaborationsController#potential_collaborators,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/collaborations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.collaborations.potential_collaborators
        
        Scope:
            url:GET|/api/v1/courses/:course_id/potential_collaborators
            url:GET|/api/v1/groups/:group_id/potential_collaborators

        
        Module: Collaborations
        Function Description: List potential members

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/potential_collaborators'
        return self.request(method, api, params)
        