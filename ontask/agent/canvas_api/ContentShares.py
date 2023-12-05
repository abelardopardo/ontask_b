from .etc.conf import *
from .res import *

class ContentShares(Res):
    def create(self, user_id, params={}):
        """
        Source Code:
            Code: ContentSharesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.create
        
        Scope:
            url:POST|/api/v1/users/:user_id/content_shares

        
        Module: Content Shares
        Function Description: Create a content share

        Parameter Desc:
            receiver_ids |Required |Array   |IDs of users to share the content with.
            content_type |Required |string  |Type of content you are sharing.                                             Allowed values: assignment, discussion_topic, page, quiz, module, module_item
            content_id   |Required |integer |The id of the content that you are sharing
        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/content_shares'
        return self.request(method, api, params)
        
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: ContentSharesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/content_shares/sent
            url:GET|/api/v1/users/:user_id/content_shares/received

        
        Module: Content Shares
        Function Description: List content shares

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/content_shares/sent'
        return self.request(method, api, params)
        
    def unread_count(self, user_id, params={}):
        """
        Source Code:
            Code: ContentSharesController#unread_count,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.unread_count
        
        Scope:
            url:GET|/api/v1/users/:user_id/content_shares/unread_count

        
        Module: Content Shares
        Function Description: Get unread shares count

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/content_shares/unread_count'
        return self.request(method, api, params)
        
    def show(self, user_id, id, params={}):
        """
        Source Code:
            Code: ContentSharesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.show
        
        Scope:
            url:GET|/api/v1/users/:user_id/content_shares/:id

        
        Module: Content Shares
        Function Description: Get content share

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/content_shares/{id}'
        return self.request(method, api, params)
        
    def destroy(self, user_id, id, params={}):
        """
        Source Code:
            Code: ContentSharesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.destroy
        
        Scope:
            url:DELETE|/api/v1/users/:user_id/content_shares/:id

        
        Module: Content Shares
        Function Description: Remove content share

        """
        method = "DELETE"
        api = f'/api/v1/users/{user_id}/content_shares/{id}'
        return self.request(method, api, params)
        
    def add_users(self, user_id, id, params={}):
        """
        Source Code:
            Code: ContentSharesController#add_users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.add_users
        
        Scope:
            url:POST|/api/v1/users/:user_id/content_shares/:id/add_users

        
        Module: Content Shares
        Function Description: Add users to content share

        Parameter Desc:
            receiver_ids | |Array |IDs of users to share the content with.
        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/content_shares/{id}/add_users'
        return self.request(method, api, params)
        
    def update(self, user_id, id, params={}):
        """
        Source Code:
            Code: ContentSharesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_shares_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_shares.update
        
        Scope:
            url:PUT|/api/v1/users/:user_id/content_shares/:id

        
        Module: Content Shares
        Function Description: Update a content share

        Parameter Desc:
            read_state | |string |Read state for the content share                                  Allowed values: read, unread
        """
        method = "PUT"
        api = f'/api/v1/users/{user_id}/content_shares/{id}'
        return self.request(method, api, params)
        