from .etc.conf import *
from .res import *

class Subaccounts(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: SubAccountsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sub_accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sub_accounts.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/sub_accounts

        
        Module: Subaccounts
        Function Description: Create a new sub-account

        Parameter Desc:
            account[name]                           |Required |string  |The name of the new sub-account.
            account[sis_account_id]                 |         |string  |The account’s identifier in the Student Information System.
            account[default_storage_quota_mb]       |         |integer |The default course storage quota to be used, if not otherwise specified.
            account[default_user_storage_quota_mb]  |         |integer |The default user storage quota to be used, if not otherwise specified.
            account[default_group_storage_quota_mb] |         |integer |The default group storage quota to be used, if not otherwise specified.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/sub_accounts'
        return self.request(method, api, params)
        
    def destroy(self, account_id, id, params={}):
        """
        Source Code:
            Code: SubAccountsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sub_accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sub_accounts.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/sub_accounts/:id

        
        Module: Subaccounts
        Function Description: Delete a sub-account

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/sub_accounts/{id}'
        return self.request(method, api, params)
        