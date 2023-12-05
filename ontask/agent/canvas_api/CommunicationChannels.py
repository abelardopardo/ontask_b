from .etc.conf import *
from .res import *

class CommunicationChannels(Res):
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: CommunicationChannelsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/communication_channels_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.communication_channels.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/communication_channels

        
        Module: Communication Channels
        Function Description: List user communication channels

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/communication_channels'
        return self.request(method, api, params)
        
    def create(self, user_id, params={}):
        """
        Source Code:
            Code: CommunicationChannelsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/communication_channels_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.communication_channels.create
        
        Scope:
            url:POST|/api/v1/users/:user_id/communication_channels

        
        Module: Communication Channels
        Function Description: Create a communication channel

        Parameter Desc:
            communication_channel[address] |Required |string  |An email address or SMS number. Not required for `push` type channels.
            communication_channel[type]    |Required |string  |The type of communication channel.                                                               In order to enable push notification support, the server must be properly configured (via ‘sns_creds` in Vault) to communicate with Amazon Simple Notification Services, and the developer key used to create the access token from this request must have an SNS ARN configured on it.                                                               Allowed values: email, sms, push
            communication_channel[token]   |         |string  |A registration id, device token, or equivalent token given to an app when registering with a push notification provider. Only valid for `push` type channels.
            skip_confirmation              |         |boolean |Only valid for site admins and account admins making requests; If true, the channel is automatically validated and no confirmation email or SMS is sent. Otherwise, the user must respond to a confirmation message to confirm the channel.
        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/communication_channels'
        return self.request(method, api, params)
        
    def destroy(self, user_id, id, params={}):
        """
        Source Code:
            Code: CommunicationChannelsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/communication_channels_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.communication_channels.destroy
        
        Scope:
            url:DELETE|/api/v1/users/:user_id/communication_channels/:id
            url:DELETE|/api/v1/users/:user_id/communication_channels/:type/:address

        
        Module: Communication Channels
        Function Description: Delete a communication channel

        """
        method = "DELETE"
        api = f'/api/v1/users/{user_id}/communication_channels/{id}'
        return self.request(method, api, params)
        
    def delete_push_token(self, params={}):
        """
        Source Code:
            Code: CommunicationChannelsController#delete_push_token,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/communication_channels_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.communication_channels.delete_push_token
        
        Scope:
            url:DELETE|/api/v1/users/self/communication_channels/push

        
        Module: Communication Channels
        Function Description: Delete a push notification endpoint

        """
        method = "DELETE"
        api = f'/api/v1/users/self/communication_channels/push'
        return self.request(method, api, params)
        