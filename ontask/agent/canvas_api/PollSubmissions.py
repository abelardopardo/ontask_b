from .etc.conf import *
from .res import *

class PollSubmissions(Res):
    def show(self, poll_id, poll_session_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSubmissionsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_submissions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_submissions.show
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_sessions/:poll_session_id/poll_submissions/:id

        
        Module: PollSubmissions
        Function Description: Get a single poll submission


        Response Example: 
            {
              "poll_submissions": [PollSubmission]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{poll_session_id}/poll_submissions/{id}'
        return self.request(method, api, params)
        
    def create(self, poll_id, poll_session_id, params={}):
        """
        Source Code:
            Code: Polling::PollSubmissionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_submissions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_submissions.create
        
        Scope:
            url:POST|/api/v1/polls/:poll_id/poll_sessions/:poll_session_id/poll_submissions

        
        Module: PollSubmissions
        Function Description: Create a single poll submission

        Parameter Desc:
            poll_submissions[][poll_choice_id] |Required |integer |The chosen poll choice for this submission.

        Response Example: 
            {
              "poll_submissions": [PollSubmission]
            }
        """
        method = "POST"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{poll_session_id}/poll_submissions'
        return self.request(method, api, params)
        