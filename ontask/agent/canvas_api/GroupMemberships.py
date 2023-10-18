from .etc.conf import *
from .res import *

class GroupMemberships(Res):
    def invite(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#invite,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.invite
        
        Scope:
            url:POST|/api/v1/groups/:group_id/invite

        
        Module: Group Memberships
        Function Description: Invite others to a group

        Parameter Desc:
            invitees[] |Required |string |An array of email addresses to be sent invitations.
        """
        method = "POST"
        api = f'/api/v1/groups/{group_id}/invite'
        return self.request(method, api, params)
        
    def index(self, group_id, params={}):
        """
        Source Code:
            Code: GroupMembershipsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_memberships_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_memberships.index
        
        Scope:
            url:GET|/api/v1/groups/:group_id/memberships

        
        Module: Group Memberships
        Function Description: List group memberships

        Parameter Desc:
            filter_states[] | |string |Only list memberships with the given workflow_states. By default it will return all memberships.                                       Allowed values: accepted, invited, requested
        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/memberships'
        return self.request(method, api, params)
        
    def show(self, group_id, membership_id, params={}):
        """
        Source Code:
            Code: GroupMembershipsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_memberships_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_memberships.show
        
        Scope:
            url:GET|/api/v1/groups/:group_id/memberships/:membership_id
            url:GET|/api/v1/groups/:group_id/users/:user_id

        
        Module: Group Memberships
        Function Description: Get a single group membership

        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/memberships/{membership_id}'
        return self.request(method, api, params)
        
    def create(self, group_id, params={}):
        """
        Source Code:
            Code: GroupMembershipsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_memberships_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_memberships.create
        
        Scope:
            url:POST|/api/v1/groups/:group_id/memberships

        
        Module: Group Memberships
        Function Description: Create a membership

        Parameter Desc:
            user_id | |string |no description
        """
        method = "POST"
        api = f'/api/v1/groups/{group_id}/memberships'
        return self.request(method, api, params)
        
    def update(self, group_id, membership_id, params={}):
        """
        Source Code:
            Code: GroupMembershipsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_memberships_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_memberships.update
        
        Scope:
            url:PUT|/api/v1/groups/:group_id/memberships/:membership_id
            url:PUT|/api/v1/groups/:group_id/users/:user_id

        
        Module: Group Memberships
        Function Description: Update a membership

        Parameter Desc:
            workflow_state | |string |Currently, the only allowed value is `accepted`                                      Allowed values: accepted
            moderator      | |string |no description
        """
        method = "PUT"
        api = f'/api/v1/groups/{group_id}/memberships/{membership_id}'
        return self.request(method, api, params)
        
    def destroy(self, group_id, membership_id, params={}):
        """
        Source Code:
            Code: GroupMembershipsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_memberships_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_memberships.destroy
        
        Scope:
            url:DELETE|/api/v1/groups/:group_id/memberships/:membership_id
            url:DELETE|/api/v1/groups/:group_id/users/:user_id

        
        Module: Group Memberships
        Function Description: Leave a group

        """
        method = "DELETE"
        api = f'/api/v1/groups/{group_id}/memberships/{membership_id}'
        return self.request(method, api, params)
        