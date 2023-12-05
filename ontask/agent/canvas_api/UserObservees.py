from .etc.conf import *
from .res import *

class UserObservees(Res):
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/observees

        
        Module: User Observees
        Function Description: List observees

        Parameter Desc:
            include[] | |string |`avatar_url`: Optionally include avatar_url.                                 Allowed values: avatar_url
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/observees'
        return self.request(method, api, params)
        
    def observers(self, user_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#observers,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.observers
        
        Scope:
            url:GET|/api/v1/users/:user_id/observers

        
        Module: User Observees
        Function Description: List observers

        Parameter Desc:
            include[] | |string |`avatar_url`: Optionally include avatar_url.                                 Allowed values: avatar_url
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/observers'
        return self.request(method, api, params)
        
    def create(self, user_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.create
        
        Scope:
            url:POST|/api/v1/users/:user_id/observees

        
        Module: User Observees
        Function Description: Add an observee with credentials

        Parameter Desc:
            observee[unique_id] | |string  |The login id for the user to observe.  Required if access_token is omitted.
            observee[password]  | |string  |The password for the user to observe. Required if access_token is omitted.
            access_token        | |string  |The access token for the user to observe.  Required if observee[unique_id] or observee[password] are omitted.
            pairing_code        | |string  |A generated pairing code for the user to observe. Required if the Observer pairing code feature flag is enabled
            root_account_id     | |integer |The ID for the root account to associate with the observation link. Defaults to the current domain account. If ‘all’ is specified, a link will be created for each root account associated to both the observer and observee.
        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/observees'
        return self.request(method, api, params)
        
    def show(self, user_id, observee_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.show
        
        Scope:
            url:GET|/api/v1/users/:user_id/observees/:observee_id

        
        Module: User Observees
        Function Description: Show an observee

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/observees/{observee_id}'
        return self.request(method, api, params)
        
    def show_observer(self, user_id, observer_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#show_observer,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.show_observer
        
        Scope:
            url:GET|/api/v1/users/:user_id/observers/:observer_id

        
        Module: User Observees
        Function Description: Show an observer

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/observers/{observer_id}'
        return self.request(method, api, params)
        
    def update(self, user_id, observee_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.update
        
        Scope:
            url:PUT|/api/v1/users/:user_id/observees/:observee_id

        
        Module: User Observees
        Function Description: Add an observee

        Parameter Desc:
            root_account_id | |integer |The ID for the root account to associate with the observation link. If not specified, a link will be created for each root account associated to both the observer and observee.
        """
        method = "PUT"
        api = f'/api/v1/users/{user_id}/observees/{observee_id}'
        return self.request(method, api, params)
        
    def destroy(self, user_id, observee_id, params={}):
        """
        Source Code:
            Code: UserObserveesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/user_observees_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.user_observees.destroy
        
        Scope:
            url:DELETE|/api/v1/users/:user_id/observees/:observee_id

        
        Module: User Observees
        Function Description: Remove an observee

        Parameter Desc:
            root_account_id | |integer |If specified, only removes the link for the given root account
        """
        method = "DELETE"
        api = f'/api/v1/users/{user_id}/observees/{observee_id}'
        return self.request(method, api, params)
        
    def create(self, user_id, params={}):
        """
        Source Code:
            Code: ObserverPairingCodesApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/observer_pairing_codes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.observer_pairing_codes_api.create
        
        Scope:
            url:POST|/api/v1/users/:user_id/observer_pairing_codes

        
        Module: User Observees
        Function Description: Create observer pairing code

        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/observer_pairing_codes'
        return self.request(method, api, params)
        