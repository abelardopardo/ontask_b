from .etc.conf import *
from .res import *

class History(Res):
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: HistoryController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/history_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.history.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/history

        
        Module: History
        Function Description: List recent history for a user

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/history'
        return self.request(method, api, params)
        