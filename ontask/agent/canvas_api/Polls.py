from .etc.conf import *
from .res import *

class Polls(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: Polling::PollsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/polls_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/polls.index
        
        Scope:
            url:GET|/api/v1/polls

        
        Module: Polls
        Function Description: List polls


        Response Example: 
            {
              "polls": [Poll]
            }
        """
        method = "GET"
        api = f'/api/v1/polls'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: Polling::PollsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/polls_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/polls.show
        
        Scope:
            url:GET|/api/v1/polls/:id

        
        Module: Polls
        Function Description: Get a single poll


        Response Example: 
            {
              "polls": [Poll]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{id}'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: Polling::PollsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/polls_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/polls.create
        
        Scope:
            url:POST|/api/v1/polls

        
        Module: Polls
        Function Description: Create a single poll

        Parameter Desc:
            polls[][question]    |Required |string |The title of the poll.
            polls[][description] |         |string |A brief description or instructions for the poll.

        Response Example: 
            {
              "polls": [Poll]
            }
        """
        method = "POST"
        api = f'/api/v1/polls'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: Polling::PollsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/polls_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/polls.update
        
        Scope:
            url:PUT|/api/v1/polls/:id

        
        Module: Polls
        Function Description: Update a single poll

        Parameter Desc:
            polls[][question]    |Required |string |The title of the poll.
            polls[][description] |         |string |A brief description or instructions for the poll.

        Response Example: 
            {
              "polls": [Poll]
            }
        """
        method = "PUT"
        api = f'/api/v1/polls/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: Polling::PollsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/polls_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/polls.destroy
        
        Scope:
            url:DELETE|/api/v1/polls/:id

        
        Module: Polls
        Function Description: Delete a poll

        """
        method = "DELETE"
        api = f'/api/v1/polls/{id}'
        return self.request(method, api, params)
        