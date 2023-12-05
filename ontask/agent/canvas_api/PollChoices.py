from .etc.conf import *
from .res import *

class PollChoices(Res):
    def index(self, poll_id, params={}):
        """
        Source Code:
            Code: Polling::PollChoicesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_choices_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_choices.index
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_choices

        
        Module: PollChoices
        Function Description: List poll choices in a poll


        Response Example: 
            {
              "poll_choices": [PollChoice]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_choices'
        return self.request(method, api, params)
        
    def show(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollChoicesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_choices_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_choices.show
        
        Scope:
            url:GET|/api/v1/polls/:poll_id/poll_choices/:id

        
        Module: PollChoices
        Function Description: Get a single poll choice


        Response Example: 
            {
              "poll_choices": [PollChoice]
            }
        """
        method = "GET"
        api = f'/api/v1/polls/{poll_id}/poll_choices/{id}'
        return self.request(method, api, params)
        
    def create(self, poll_id, params={}):
        """
        Source Code:
            Code: Polling::PollChoicesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_choices_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_choices.create
        
        Scope:
            url:POST|/api/v1/polls/:poll_id/poll_choices

        
        Module: PollChoices
        Function Description: Create a single poll choice

        Parameter Desc:
            poll_choices[][text]       |Required |string  |The descriptive text of the poll choice.
            poll_choices[][is_correct] |         |boolean |Whether this poll choice is considered correct or not. Defaults to false.
            poll_choices[][position]   |         |integer |The order this poll choice should be returned in the context it’s sibling poll choices.

        Response Example: 
            {
              "poll_choices": [PollChoice]
            }
        """
        method = "POST"
        api = f'/api/v1/polls/{poll_id}/poll_choices'
        return self.request(method, api, params)
        
    def update(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollChoicesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_choices_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_choices.update
        
        Scope:
            url:PUT|/api/v1/polls/:poll_id/poll_choices/:id

        
        Module: PollChoices
        Function Description: Update a single poll choice

        Parameter Desc:
            poll_choices[][text]       |Required |string  |The descriptive text of the poll choice.
            poll_choices[][is_correct] |         |boolean |Whether this poll choice is considered correct or not.  Defaults to false.
            poll_choices[][position]   |         |integer |The order this poll choice should be returned in the context it’s sibling poll choices.

        Response Example: 
            {
              "poll_choices": [PollChoice]
            }
        """
        method = "PUT"
        api = f'/api/v1/polls/{poll_id}/poll_choices/{id}'
        return self.request(method, api, params)
        
    def destroy(self, poll_id, id, params={}):
        """
        Source Code:
            Code: Polling::PollChoicesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/polling/poll_choices_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.polling/poll_choices.destroy
        
        Scope:
            url:DELETE|/api/v1/polls/:poll_id/poll_choices/:id

        
        Module: PollChoices
        Function Description: Delete a poll choice

        """
        method = "DELETE"
        api = f'/api/v1/polls/{poll_id}/poll_choices/{id}'
        return self.request(method, api, params)
        