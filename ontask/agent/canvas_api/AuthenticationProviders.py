from .etc.conf import *
from .res import *

class AuthenticationProviders(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/authentication_providers

        
        Module: Authentication Providers
        Function Description: List authentication providers

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/authentication_providers'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/authentication_providers

        
        Module: Authentication Providers
        Function Description: Add authentication provider

        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/authentication_providers'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/authentication_providers/:id

        
        Module: Authentication Providers
        Function Description: Update authentication provider

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/authentication_providers/{id}'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/authentication_providers/:id

        
        Module: Authentication Providers
        Function Description: Get authentication provider

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/authentication_providers/{id}'
        return self.request(method, api, params)
        
    def destroy(self, account_id, id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/authentication_providers/:id

        
        Module: Authentication Providers
        Function Description: Delete authentication provider

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/authentication_providers/{id}'
        return self.request(method, api, params)
        
    def show_sso_settings(self, account_id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#show_sso_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.show_sso_settings
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sso_settings

        
        Module: Authentication Providers
        Function Description: show account auth settings

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sso_settings'
        return self.request(method, api, params)
        
    def update_sso_settings(self, account_id, params={}):
        """
        Source Code:
            Code: AuthenticationProvidersController#update_sso_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/authentication_providers_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.authentication_providers.update_sso_settings
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/sso_settings

        
        Module: Authentication Providers
        Function Description: update account auth settings

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/sso_settings'
        return self.request(method, api, params)
        