from .etc.conf import *
from .res import *

class Admins(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: AdminsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/admins_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.admins.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/admins

        
        Module: Admins
        Function Description: Make an account admin

        Parameter Desc:
            user_id           |Required |integer |The id of the user to promote.
            role              |         |string  |DEPRECATED                                                  The user’s admin relationship with the account will be                                                  created with the given role. Defaults to ‘AccountAdmin’.
            role_id           |         |integer |The user’s admin relationship with the account will be created with the given role. Defaults to the built-in role for ‘AccountAdmin’.
            send_confirmation |         |boolean |Send a notification email to the new admin if true. Default is true.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/admins'
        return self.request(method, api, params)
        
    def destroy(self, account_id, user_id, params={}):
        """
        Source Code:
            Code: AdminsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/admins_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.admins.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/admins/:user_id

        
        Module: Admins
        Function Description: Remove account admin

        Parameter Desc:
            role    |         |string  |DEPRECATED                                        Account role to remove from the user.
            role_id |Required |integer |The id of the role representing the user’s admin relationship with the account.
        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/admins/{user_id}'
        return self.request(method, api, params)
        
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: AdminsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/admins_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.admins.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/admins

        
        Module: Admins
        Function Description: List account admins

        Parameter Desc:
            user_id[] | |[Integer] |Scope the results to those with user IDs equal to any of the IDs specified here.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/admins'
        return self.request(method, api, params)
        