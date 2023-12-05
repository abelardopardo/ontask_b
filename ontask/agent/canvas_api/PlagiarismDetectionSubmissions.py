from .etc.conf import *
from .res import *

class PlagiarismDetectionSubmissions(Res):
    def show(self, assignment_id, submission_id, params={}):
        """
        Source Code:
            Code: Lti::SubmissionsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/submissions_api.show
        
        Scope:
            url:GET|/api/lti/assignments/:assignment_id/submissions/:submission_id

        
        Module: Plagiarism Detection Submissions
        Function Description: Get a single submission

        """
        method = "GET"
        api = f'/api/lti/assignments/{assignment_id}/submissions/{submission_id}'
        return self.request(method, api, params)
        
    def history(self, assignment_id, submission_id, params={}):
        """
        Source Code:
            Code: Lti::SubmissionsApiController#history,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/submissions_api.history
        
        Scope:
            url:GET|/api/lti/assignments/:assignment_id/submissions/:submission_id/history

        
        Module: Plagiarism Detection Submissions
        Function Description: Get the history of a single submission

        """
        method = "GET"
        api = f'/api/lti/assignments/{assignment_id}/submissions/{submission_id}/history'
        return self.request(method, api, params)
        