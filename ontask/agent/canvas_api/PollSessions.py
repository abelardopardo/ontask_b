from .etc.conf import *
from .res import *

class PollSessions(Res):
    def index(self, poll_id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.index
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_sessions

        
        Module: Poll Sessions
        Function Description: List poll sessions for a poll


        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_sessions'
        return self.request(method, api, params)
        
    def show(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.show
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_sessions/:id

        
        Module: Poll Sessions
        Function Description: Get the results for a single poll session


        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{id}'
        return self.request(method, api, params)
        
    def create(self, poll_id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.create
        
        Scope:
            url:POST|/api/v1/polls/:poll_id/poll_sessions

        
        Module: Poll Sessions
        Function Description: Create a single poll session

        Parameter Desc:
            poll_sessions[][course_id]          |Required |integer |The id of the course this session is associated with.
            poll_sessions[][course_section_id]  |         |integer |The id of the course section this session is associated with.
            poll_sessions[][has_public_results] |         |boolean |Whether or not results are viewable by students.

        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "POST"
        api = f'/api/v1/polls/{poll_id}/poll_sessions'
        return self.request(method, api, params)
        
    def update(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.update
        
        Scope:
            url:PUT|/api/v1/polls/:poll_id/poll_sessions/:id

        
        Module: Poll Sessions
        Function Description: Update a single poll session

        Parameter Desc:
            poll_sessions[][course_id]          | |integer |The id of the course this session is associated with.
            poll_sessions[][course_section_id]  | |integer |The id of the course section this session is associated with.
            poll_sessions[][has_public_results] | |boolean |Whether or not results are viewable by students.

        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "PUT"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{id}'
        return self.request(method, api, params)
        
    def destroy(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.destroy
        
        Scope:
            url:DELETE|/api/v1/polls/:poll_id/poll_sessions/:id

        
        Module: Poll Sessions
        Function Description: Delete a poll session

        """
        method = "DELETE"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{id}'
        return self.request(method, api, params)
        
    def open(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#open,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.open
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_sessions/:id/open

        
        Module: Poll Sessions
        Function Description: Open a poll session

        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{id}/open'
        return self.request(method, api, params)
        
    def close(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#close,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.close
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_sessions/:id/close

        
        Module: Poll Sessions
        Function Description: Close an opened poll session

        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_sessions/{id}/close'
        return self.request(method, api, params)
        
    def opened(self, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#opened,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.opened
        
        Scope:
            url:GET|/api/v1/poll_sessions/opened

        
        Module: Poll Sessions
        Function Description: List opened poll sessions


        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "GET"
        api = f'/api/v1/poll_sessions/opened'
        return self.request(method, api, params)
        
    def closed(self, params={}):
        """
        Source Code:
            Code: Polling::PollSessionsController#closed,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_sessions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_sessions.closed
        
        Scope:
            url:GET|/api/v1/poll_sessions/closed

        
        Module: Poll Sessions
        Function Description: List closed poll sessions


        Response Example: 
            {
              "poll_sessions": [PollSession]
            }
        """
        method = "GET"
        api = f'/api/v1/poll_sessions/closed'
        return self.request(method, api, params)
        