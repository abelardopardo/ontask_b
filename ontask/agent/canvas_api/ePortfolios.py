from .etc.conf import *
from .res import *

class ePortfolios(Res):
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/eportfolios

        
        Module: ePortfolios
        Function Description: Get all ePortfolios for a User

        Parameter Desc:
            include[] | |string |deleted                                 Include deleted ePortfolios. Only available to admins who can                                 moderate_user_content.                                 Allowed values: deleted
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/eportfolios'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.show
        
        Scope:
            url:GET|/api/v1/eportfolios/:id

        
        Module: ePortfolios
        Function Description: Get an ePortfolio

        """
        method = "GET"
        api = f'/api/v1/eportfolios/{id}'
        return self.request(method, api, params)
        
    def delete(self, id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#delete,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.delete
        
        Scope:
            url:DELETE|/api/v1/eportfolios/:id

        
        Module: ePortfolios
        Function Description: Delete an ePortfolio

        """
        method = "DELETE"
        api = f'/api/v1/eportfolios/{id}'
        return self.request(method, api, params)
        
    def pages(self, eportfolio_id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#pages,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.pages
        
        Scope:
            url:GET|/api/v1/eportfolios/:eportfolio_id/pages

        
        Module: ePortfolios
        Function Description: Get ePortfolio Pages

        """
        method = "GET"
        api = f'/api/v1/eportfolios/{eportfolio_id}/pages'
        return self.request(method, api, params)
        
    def moderate(self, eportfolio_id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#moderate,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.moderate
        
        Scope:
            url:PUT|/api/v1/eportfolios/:eportfolio_id/moderate

        
        Module: ePortfolios
        Function Description: Moderate an ePortfolio

        Parameter Desc:
            spam_status | |string |The spam status for the ePortfolio                                   Allowed values: marked_as_spam, marked_as_safe
        """
        method = "PUT"
        api = f'/api/v1/eportfolios/{eportfolio_id}/moderate'
        return self.request(method, api, params)
        
    def moderate_all(self, user_id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#moderate_all,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.moderate_all
        
        Scope:
            url:PUT|/api/v1/users/:user_id/eportfolios

        
        Module: ePortfolios
        Function Description: Moderate all ePortfolios for a User

        Parameter Desc:
            spam_status | |string |The spam status for all the ePortfolios                                   Allowed values: marked_as_spam, marked_as_safe
        """
        method = "PUT"
        api = f'/api/v1/users/{user_id}/eportfolios'
        return self.request(method, api, params)
        
    def restore(self, eportfolio_id, params={}):
        """
        Source Code:
            Code: EportfoliosApiController#restore,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/eportfolios_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.eportfolios_api.restore
        
        Scope:
            url:PUT|/api/v1/eportfolios/:eportfolio_id/restore

        
        Module: ePortfolios
        Function Description: Restore a deleted ePortfolio

        """
        method = "PUT"
        api = f'/api/v1/eportfolios/{eportfolio_id}/restore'
        return self.request(method, api, params)
        