from .etc.conf import *
from .res import *

class OutcomeGroups(Res):
    def redirect(self, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#redirect,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.redirect
        
        Scope:
            url:GET|/api/v1/global/root_outcome_group
            url:GET|/api/v1/accounts/:account_id/root_outcome_group
            url:GET|/api/v1/courses/:course_id/root_outcome_group

        
        Module: Outcome Groups
        Function Description: Redirect to root outcome group for context

        """
        method = "GET"
        api = f'/api/v1/global/root_outcome_group'
        return self.request(method, api, params)
        
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/outcome_groups
            url:GET|/api/v1/courses/:course_id/outcome_groups

        
        Module: Outcome Groups
        Function Description: Get all outcome groups for context

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/outcome_groups'
        return self.request(method, api, params)
        
    def link_index(self, account_id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#link_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.link_index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/outcome_group_links
            url:GET|/api/v1/courses/:course_id/outcome_group_links

        
        Module: Outcome Groups
        Function Description: Get all outcome links for context

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/outcome_group_links'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.show
        
        Scope:
            url:GET|/api/v1/global/outcome_groups/:id
            url:GET|/api/v1/accounts/:account_id/outcome_groups/:id
            url:GET|/api/v1/courses/:course_id/outcome_groups/:id

        
        Module: Outcome Groups
        Function Description: Show an outcome group

        """
        method = "GET"
        api = f'/api/v1/global/outcome_groups/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.update
        
        Scope:
            url:PUT|/api/v1/global/outcome_groups/:id
            url:PUT|/api/v1/accounts/:account_id/outcome_groups/:id
            url:PUT|/api/v1/courses/:course_id/outcome_groups/:id

        
        Module: Outcome Groups
        Function Description: Update an outcome group

        Parameter Desc:
            title                   | |string  |The new outcome group title.
            description             | |string  |The new outcome group description.
            vendor_guid             | |string  |A custom GUID for the learning standard.
            parent_outcome_group_id | |integer |The id of the new parent outcome group.
        """
        method = "PUT"
        api = f'/api/v1/global/outcome_groups/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.destroy
        
        Scope:
            url:DELETE|/api/v1/global/outcome_groups/:id
            url:DELETE|/api/v1/accounts/:account_id/outcome_groups/:id
            url:DELETE|/api/v1/courses/:course_id/outcome_groups/:id

        
        Module: Outcome Groups
        Function Description: Delete an outcome group

        """
        method = "DELETE"
        api = f'/api/v1/global/outcome_groups/{id}'
        return self.request(method, api, params)
        
    def outcomes(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#outcomes,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.outcomes
        
        Scope:
            url:GET|/api/v1/global/outcome_groups/:id/outcomes
            url:GET|/api/v1/accounts/:account_id/outcome_groups/:id/outcomes
            url:GET|/api/v1/courses/:course_id/outcome_groups/:id/outcomes

        
        Module: Outcome Groups
        Function Description: List linked outcomes

        Parameter Desc:
            outcome_style | |string |The detail level of the outcomes. Defaults to `abbrev`. Specify `full` for more information.
        """
        method = "GET"
        api = f'/api/v1/global/outcome_groups/{id}/outcomes'
        return self.request(method, api, params)
        
    def link(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#link,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.link
        
        Scope:
            url:POST|/api/v1/global/outcome_groups/:id/outcomes
            url:PUT|/api/v1/global/outcome_groups/:id/outcomes/:outcome_id
            url:POST|/api/v1/accounts/:account_id/outcome_groups/:id/outcomes
            url:PUT|/api/v1/accounts/:account_id/outcome_groups/:id/outcomes/:outcome_id
            url:POST|/api/v1/courses/:course_id/outcome_groups/:id/outcomes
            url:PUT|/api/v1/courses/:course_id/outcome_groups/:id/outcomes/:outcome_id

        
        Module: Outcome Groups
        Function Description: Create/link an outcome

        Parameter Desc:
            outcome_id             | |integer |The ID of the existing outcome to link.
            move_from              | |integer |The ID of the old outcome group. Only used if outcome_id is present.
            title                  | |string  |The title of the new outcome. Required if outcome_id is absent.
            display_name           | |string  |A friendly name shown in reports for outcomes with cryptic titles, such as common core standards names.
            description            | |string  |The description of the new outcome.
            vendor_guid            | |string  |A custom GUID for the learning standard.
            mastery_points         | |integer |The mastery threshold for the embedded rubric criterion.
            ratings[][description] | |string  |The description of a rating level for the embedded rubric criterion.
            ratings[][points]      | |integer |The points corresponding to a rating level for the embedded rubric criterion.
            calculation_method     | |string  |The new calculation method.  Defaults to `decaying_average`                                               Allowed values: decaying_average, n_mastery, latest, highest, average
            calculation_int        | |integer |The new calculation int.  Only applies if the calculation_method is `decaying_average` or `n_mastery`. Defaults to 65
        """
        method = "POST"
        api = f'/api/v1/global/outcome_groups/{id}/outcomes'
        return self.request(method, api, params)
        
    def unlink(self, id, outcome_id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#unlink,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.unlink
        
        Scope:
            url:DELETE|/api/v1/global/outcome_groups/:id/outcomes/:outcome_id
            url:DELETE|/api/v1/accounts/:account_id/outcome_groups/:id/outcomes/:outcome_id
            url:DELETE|/api/v1/courses/:course_id/outcome_groups/:id/outcomes/:outcome_id

        
        Module: Outcome Groups
        Function Description: Unlink an outcome

        """
        method = "DELETE"
        api = f'/api/v1/global/outcome_groups/{id}/outcomes/{outcome_id}'
        return self.request(method, api, params)
        
    def subgroups(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#subgroups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.subgroups
        
        Scope:
            url:GET|/api/v1/global/outcome_groups/:id/subgroups
            url:GET|/api/v1/accounts/:account_id/outcome_groups/:id/subgroups
            url:GET|/api/v1/courses/:course_id/outcome_groups/:id/subgroups

        
        Module: Outcome Groups
        Function Description: List subgroups

        """
        method = "GET"
        api = f'/api/v1/global/outcome_groups/{id}/subgroups'
        return self.request(method, api, params)
        
    def create(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.create
        
        Scope:
            url:POST|/api/v1/global/outcome_groups/:id/subgroups
            url:POST|/api/v1/accounts/:account_id/outcome_groups/:id/subgroups
            url:POST|/api/v1/courses/:course_id/outcome_groups/:id/subgroups

        
        Module: Outcome Groups
        Function Description: Create a subgroup

        Parameter Desc:
            title       |Required |string |The title of the new outcome group.
            description |         |string |The description of the new outcome group.
            vendor_guid |         |string |A custom GUID for the learning standard
        """
        method = "POST"
        api = f'/api/v1/global/outcome_groups/{id}/subgroups'
        return self.request(method, api, params)
        
    def import_func(self, id, params={}):
        """
        Source Code:
            Code: OutcomeGroupsApiController#import,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_groups_api.import
        
        Scope:
            url:POST|/api/v1/global/outcome_groups/:id/import
            url:POST|/api/v1/accounts/:account_id/outcome_groups/:id/import
            url:POST|/api/v1/courses/:course_id/outcome_groups/:id/import

        
        Module: Outcome Groups
        Function Description: Import an outcome group

        Parameter Desc:
            source_outcome_group_id |Required |integer |The ID of the source outcome group.
            async                   |         |boolean |If true, perform action asynchronously.  In that case, this endpoint will return a Progress object instead of an OutcomeGroup. Use the progress endpoint to query the status of the operation.  The imported outcome group id and url will be returned in the results of the Progress object as `outcome_group_id` and `outcome_group_url`
        """
        method = "POST"
        api = f'/api/v1/global/outcome_groups/{id}/import'
        return self.request(method, api, params)
        