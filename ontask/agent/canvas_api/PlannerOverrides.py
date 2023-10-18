from .etc.conf import *
from .res import *

class PlannerOverrides(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: PlannerOverridesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner_overrides.index
        
        Scope:
            url:GET|/api/v1/planner/overrides

        
        Module: Planner Overrides
        Function Description: List planner overrides

        """
        method = "GET"
        api = f'/api/v1/planner/overrides'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: PlannerOverridesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner_overrides.show
        
        Scope:
            url:GET|/api/v1/planner/overrides/:id

        
        Module: Planner Overrides
        Function Description: Show a planner override

        """
        method = "GET"
        api = f'/api/v1/planner/overrides/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: PlannerOverridesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner_overrides.update
        
        Scope:
            url:PUT|/api/v1/planner/overrides/:id

        
        Module: Planner Overrides
        Function Description: Update a planner override

        Parameter Desc:
            marked_complete | |string |determines whether the planner item is marked as completed
            dismissed       | |string |determines whether the planner item shows in the opportunities list
        """
        method = "PUT"
        api = f'/api/v1/planner/overrides/{id}'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: PlannerOverridesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner_overrides.create
        
        Scope:
            url:POST|/api/v1/planner/overrides

        
        Module: Planner Overrides
        Function Description: Create a planner override

        Parameter Desc:
            plannable_type  |Required |string  |Type of the item that you are overriding in the planner                                                Allowed values: announcement, assignment, discussion_topic, quiz, wiki_page, planner_note
            plannable_id    |Required |integer |ID of the item that you are overriding in the planner
            marked_complete |         |boolean |If this is true, the item will show in the planner as completed
            dismissed       |         |boolean |If this is true, the item will not show in the opportunities list
        """
        method = "POST"
        api = f'/api/v1/planner/overrides'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: PlannerOverridesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner_overrides.destroy
        
        Scope:
            url:DELETE|/api/v1/planner/overrides/:id

        
        Module: Planner Overrides
        Function Description: Delete a planner override

        """
        method = "DELETE"
        api = f'/api/v1/planner/overrides/{id}'
        return self.request(method, api, params)
        