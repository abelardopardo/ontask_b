from .etc.conf import *
from .res import *

class CommMessages(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: CommMessagesApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/comm_messages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.comm_messages_api.index
        
        Scope:
            url:GET|/api/v1/comm_messages

        
        Module: CommMessages
        Function Description: List of CommMessages for a user

        Parameter Desc:
            user_id    |Required |string   |The user id for whom you want to retrieve CommMessages
            start_time |         |DateTime |The beginning of the time range you want to retrieve message from. Up to a year prior to the current date is available.
            end_time   |         |DateTime |The end of the time range you want to retrieve messages for. Up to a year prior to the current date is available.
        """
        method = "GET"
        api = f'/api/v1/comm_messages'
        return self.request(method, api, params)
        