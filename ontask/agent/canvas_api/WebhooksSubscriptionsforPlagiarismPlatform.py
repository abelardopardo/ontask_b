from .etc.conf import *
from .res import *

class WebhooksSubscriptionsforPlagiarismPlatform(Res):
    def create(self, params={}):
        """
        Source Code:
            Code: Lti::SubscriptionsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/subscriptions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/subscriptions_api.create
        
        Scope:
            url:POST|/api/lti/subscriptions

        
        Module: Webhooks Subscriptions for Plagiarism Platform
        Function Description: Create a Webhook Subscription

        Parameter Desc:
            subscription[ContextId]         |Required |string |The id of the context for the subscription.
            subscription[ContextType]       |Required |string |The type of context for the subscription. Must be ‘assignment’, ‘account’, or ‘course’.
            subscription[EventTypes]        |Required |Array  |Array of strings representing the event types for the subscription.
            subscription[Format]            |Required |string |Format to deliver the live events. Must be ‘live-event’ or ‘caliper’.
            subscription[TransportMetadata] |Required |Object |An object with a single key: ‘Url’. Example: { `Url`: `sqs.example` }
            subscription[TransportType]     |Required |string |Must be either ‘sqs’ or ‘https’.
        """
        method = "POST"
        api = f'/api/lti/subscriptions'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: Lti::SubscriptionsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/subscriptions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/subscriptions_api.destroy
        
        Scope:
            url:DELETE|/api/lti/subscriptions/:id

        
        Module: Webhooks Subscriptions for Plagiarism Platform
        Function Description: Delete a Webhook Subscription

        """
        method = "DELETE"
        api = f'/api/lti/subscriptions/{id}'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: Lti::SubscriptionsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/subscriptions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/subscriptions_api.show
        
        Scope:
            url:GET|/api/lti/subscriptions/:id

        
        Module: Webhooks Subscriptions for Plagiarism Platform
        Function Description: Show a single Webhook Subscription

        """
        method = "GET"
        api = f'/api/lti/subscriptions/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: Lti::SubscriptionsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/subscriptions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/subscriptions_api.update
        
        Scope:
            url:PUT|/api/lti/subscriptions/:id

        
        Module: Webhooks Subscriptions for Plagiarism Platform
        Function Description: Update a Webhook Subscription

        """
        method = "PUT"
        api = f'/api/lti/subscriptions/{id}'
        return self.request(method, api, params)
        
    def index(self, params={}):
        """
        Source Code:
            Code: Lti::SubscriptionsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/subscriptions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/subscriptions_api.index
        
        Scope:
            url:GET|/api/lti/subscriptions

        
        Module: Webhooks Subscriptions for Plagiarism Platform
        Function Description: List all Webhook Subscription for a tool proxy

        """
        method = "GET"
        api = f'/api/lti/subscriptions'
        return self.request(method, api, params)
        