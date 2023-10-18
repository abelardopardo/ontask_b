from .etc.conf import *
from .res import *

class Logins(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: PseudonymsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/pseudonyms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.pseudonyms.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/logins
            url:GET|/api/v1/users/:user_id/logins

        
        Module: Logins
        Function Description: List user logins


        Response Example: 
            [
              {
                "account_id": 1,
                "id" 2,
                "sis_user_id": null,
                "unique_id": "belieber@example.com",
                "user_id": 2,
                "authentication_provider_id": 1,
                "authentication_provider_type": "facebook",
                "workflow_state": "active",
                "declared_user_type": null,
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/logins'
        return self.request(method, api, params)
        
    def forgot_password(self, params={}):
        """
        Source Code:
            Code: PseudonymsController#forgot_password,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/pseudonyms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.pseudonyms.forgot_password
        
        Scope:
            url:POST|/api/v1/users/reset_password

        
        Module: Logins
        Function Description: Kickoff password recovery flow


        Response Example: 
            {
              "requested": true
            }
        """
        method = "POST"
        api = f'/api/v1/users/reset_password'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: PseudonymsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/pseudonyms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.pseudonyms.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/logins

        
        Module: Logins
        Function Description: Create a user login

        Parameter Desc:
            user[id]                          |Required |string |The ID of the user to create the login for.
            login[unique_id]                  |Required |string |The unique ID for the new login.
            login[password]                   |         |string |The new login’s password.
            login[sis_user_id]                |         |string |SIS ID for the login. To set this parameter, the caller must be able to manage SIS permissions on the account.
            login[integration_id]             |         |string |Integration ID for the login. To set this parameter, the caller must be able to manage SIS permissions on the account. The Integration ID is a secondary identifier useful for more complex SIS integrations.
            login[authentication_provider_id] |         |string |The authentication provider this login is associated with. Logins associated with a specific provider can only be used with that provider. Legacy providers (LDAP, CAS, SAML) will search for logins associated with them, or unassociated logins. New providers will only search for logins explicitly associated with them. This can be the integer ID of the provider, or the type of the provider (in which case, it will find the first matching provider).
            login[declared_user_type]         |         |string |The declared intention of the user type. This can be set, but does not change any Canvas functionality with respect to their access. A user can still be a teacher, admin, student, etc. in any particular context without regard to this setting. This can be used for administrative purposes for integrations to be able to more easily identify why the user was created. Valid values are:                                                                 * administrative                                                                 * observer                                                                 * staff                                                                 * student                                                                 * student_other                                                                 * teacher
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/logins'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: PseudonymsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/pseudonyms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.pseudonyms.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/logins/:id

        
        Module: Logins
        Function Description: Edit a user login

        Parameter Desc:
            login[unique_id]                  | |string  |The new unique ID for the login.
            login[password]                   | |string  |The new password for the login. Can only be set by an admin user if admins are allowed to change passwords for the account.
            login[sis_user_id]                | |string  |SIS ID for the login. To set this parameter, the caller must be able to manage SIS permissions on the account.
            login[integration_id]             | |string  |Integration ID for the login. To set this parameter, the caller must be able to manage SIS permissions on the account. The Integration ID is a secondary identifier useful for more complex SIS integrations.
            login[authentication_provider_id] | |string  |The authentication provider this login is associated with. Logins associated with a specific provider can only be used with that provider. Legacy providers (LDAP, CAS, SAML) will search for logins associated with them, or unassociated logins. New providers will only search for logins explicitly associated with them. This can be the integer ID of the provider, or the type of the provider (in which case, it will find the first matching provider).
            login[workflow_state]             | |string  |Used to suspend or re-activate a login.                                                          Allowed values: active, suspended
            login[declared_user_type]         | |string  |The declared intention of the user type. This can be set, but does not change any Canvas functionality with respect to their access. A user can still be a teacher, admin, student, etc. in any particular context without regard to this setting. This can be used for administrative purposes for integrations to be able to more easily identify why the user was created. Valid values are:                                                          * administrative                                                          * observer                                                          * staff                                                          * student                                                          * student_other                                                          * teacher
            override_sis_stickiness           | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness

        Request Example: 
            curl https://<canvas>/api/v1/accounts/:account_id/logins/:login_id \
              -H "Authorization: Bearer <ACCESS-TOKEN>" \
              -X PUT

        Response Example: 
            {
              "id": 1,
              "user_id": 2,
              "account_id": 3,
              "unique_id": "bieber@example.com",
              "created_at": "2020-01-29T19:33:35Z",
              "sis_user_id": null,
              "integration_id": null,
              "authentication_provider_id": null,
              "workflow_state": "active",
              "declared_user_type": "teacher"
            }
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/logins/{id}'
        return self.request(method, api, params)
        
    def destroy(self, user_id, id, params={}):
        """
        Source Code:
            Code: PseudonymsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/pseudonyms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.pseudonyms.destroy
        
        Scope:
            url:DELETE|/api/v1/users/:user_id/logins/:id

        
        Module: Logins
        Function Description: Delete a user login


        Request Example: 
            curl https://<canvas>/api/v1/users/:user_id/logins/:login_id \
              -H "Authorization: Bearer <ACCESS-TOKEN>" \
              -X DELETE

        Response Example: 
            {
              "unique_id": "bieber@example.com",
              "sis_user_id": null,
              "account_id": 1,
              "id": 12345,
              "user_id": 2
            }
        """
        method = "DELETE"
        api = f'/api/v1/users/{user_id}/logins/{id}'
        return self.request(method, api, params)
        