from .etc.conf import *
from .res import *

class Tabs(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: TabsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/tabs_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.tabs.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/tabs
            url:GET|/api/v1/courses/:course_id/tabs
            url:GET|/api/v1/groups/:group_id/tabs
            url:GET|/api/v1/users/:user_id/tabs

        
        Module: Tabs
        Function Description: List available tabs for a course or group

        Parameter Desc:
            include[] | |string |`course_subject_tabs`: Optional flag to return the tabs associated with a canvas_for_elementary subject course’s home page instead of the typical sidebar navigation. Only takes effect if this request is for a course context in a canvas_for_elementary-enabled account or sub-account.                                 Allowed values: course_subject_tabs

        Request Example: 
            curl -H 'Authorization: Bearer <token>' \
                 https://<canvas>/api/v1/groups/<group_id>/tabs"

        Response Example: 
            [
              {
                "html_url": "/courses/1",
                "id": "home",
                "label": "Home",
                "position": 1,
                "visibility": "public",
                "type": "internal"
              },
              {
                "html_url": "/courses/1/external_tools/4",
                "id": "context_external_tool_4",
                "label": "WordPress",
                "hidden": true,
                "visibility": "public",
                "position": 2,
                "type": "external"
              },
              {
                "html_url": "/courses/1/grades",
                "id": "grades",
                "label": "Grades",
                "position": 3,
                "hidden": true
                "visibility": "admins"
                "type": "internal"
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/tabs'
        return self.request(method, api, params)
        
    def update(self, course_id, tab_id, params={}):
        """
        Source Code:
            Code: TabsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/tabs_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.tabs.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/tabs/:tab_id

        
        Module: Tabs
        Function Description: Update a tab for a course

        Parameter Desc:
            position | |integer |The new position of the tab, 1-based
            hidden   | |boolean |no description
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/tabs/{tab_id}'
        return self.request(method, api, params)
        