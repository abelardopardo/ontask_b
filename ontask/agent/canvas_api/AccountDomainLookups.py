from .etc.conf import *
from .res import *

class AccountDomainLookups(Res):
    def search(self, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_domain_lookups.search
        
        Scope:
            url:GET|/api/v1/accounts/search

        
        Module: Account Domain Lookups
        Function Description: Search account domains

        Parameter Desc:
            name      | |string |campus name
            domain    | |string |no description
            latitude  | |number |no description
            longitude | |number |no description

        Request Example: 
            curl https://<canvas>/api/v1/accounts/search \
              -G -H 'Authorization: Bearer <ACCESS_TOKEN>' \
              -d 'name=utah'

        Response Example: 
            [
              {
                "name": "University of Utah",
                "domain": "utah.edu",
                "distance": null, // distance is always nil, but preserved in the api response for backwards compatibility
                "authentication_provider": "canvas", // which authentication_provider param to pass to the oauth flow; may be NULL
              },
              ...
            ]
        """
        method = "GET"
        api = f'/api/v1/accounts/search'
        return self.request(method, api, params)
        