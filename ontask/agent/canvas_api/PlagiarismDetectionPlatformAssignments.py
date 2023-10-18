from .etc.conf import *
from .res import *

class PlagiarismDetectionPlatformAssignments(Res):
    def show(self, assignment_id, params={}):
        """
        Source Code:
            Code: Lti::PlagiarismAssignmentsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/plagiarism_assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/plagiarism_assignments_api.show
        
        Scope:
            url:GET|/api/lti/assignments/:assignment_id

        
        Module: Plagiarism Detection Platform Assignments
        Function Description: Get a single assignment (lti)

        Parameter Desc:
            user_id | |string |The id of the user. Can be a Canvas or LTI id for the user.
        """
        method = "GET"
        api = f'/api/lti/assignments/{assignment_id}'
        return self.request(method, api, params)
        