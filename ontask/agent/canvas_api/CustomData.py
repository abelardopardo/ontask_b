from .etc.conf import *
from .res import *

class CustomData(Res):
    def set_data(self, user_id, params={}):
        """
        Source Code:
            Code: CustomDataController#set_data,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_data_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_data.set_data
        
        Scope:
            url:PUT|/api/v1/users/:user_id/custom_data(/*scope)

        
        Module: Custom Data
        Function Description: Store custom data

        Parameter Desc:
            ns   |Required |string |The namespace under which to store the data.  This should be something other Canvas API apps aren’t likely to use, such as a reverse DNS for your organization.
            data |Required |JSON   |The data you want to store for the user, at the specified scope.  If the data is composed of (possibly nested) JSON objects, scopes will be generated for the (nested) keys (see examples).

        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/custom_data/food_app' \
              -X PUT \
              -F 'ns=com.my-organization.canvas-app' \
              -F 'data[weight]=81kg' \
              -F 'data[favorites][meat]=pork belly' \
              -F 'data[favorites][dessert]=pistachio ice cream' \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "data": {
                "weight": "81kg",
                "favorites": {
                  "meat": "pork belly",
                  "dessert": "pistachio ice cream"
                }
              }
            }
        """
        method = "PUT"
        api = f'/api/v1/users/{user_id}/custom_data(/*scope)'
        return self.request(method, api, params)
        
    def get_data(self, user_id, params={}):
        """
        Source Code:
            Code: CustomDataController#get_data,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_data_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_data.get_data
        
        Scope:
            url:GET|/api/v1/users/:user_id/custom_data(/*scope)

        
        Module: Custom Data
        Function Description: Load custom data

        Parameter Desc:
            ns |Required |string |The namespace from which to retrieve the data.  This should be something other Canvas API apps aren’t likely to use, such as a reverse DNS for your organization.

        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/custom_data/food_app/favorites/dessert' \
              -X GET \
              -F 'ns=com.my-organization.canvas-app' \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "data": "pistachio ice cream"
            }
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/custom_data(/*scope)'
        return self.request(method, api, params)
        
    def delete_data(self, user_id, params={}):
        """
        Source Code:
            Code: CustomDataController#delete_data,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_data_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_data.delete_data
        
        Scope:
            url:DELETE|/api/v1/users/:user_id/custom_data(/*scope)

        
        Module: Custom Data
        Function Description: Delete custom data

        Parameter Desc:
            ns |Required |string |The namespace from which to delete the data.  This should be something other Canvas API apps aren’t likely to use, such as a reverse DNS for your organization.

        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/custom_data/fruit/kiwi' \
              -X DELETE \
              -F 'ns=com.my-organization.canvas-app' \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            !!!javascript
            {
              "data": "a bit sour"
            }
        """
        method = "DELETE"
        api = f'/api/v1/users/{user_id}/custom_data(/*scope)'
        return self.request(method, api, params)
        