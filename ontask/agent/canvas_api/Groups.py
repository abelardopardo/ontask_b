from .etc.conf import *
from .res import *

class Groups(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: GroupsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.index
        
        Scope:
            url:GET|/api/v1/users/self/groups

        
        Module: Groups
        Function Description: List your groups

        Parameter Desc:
            context_type | |string |Only include groups that are in this type of context.                                    Allowed values: Account, Course
            include[]    | |string |`tabs`: Include the list of tabs configured for each group.  See the List available tabs API for more information.                                    Allowed values: tabs
        """
        method = "GET"
        api = f'/api/v1/users/self/groups'
        return self.request(method, api, params)
        
    def context_index(self, account_id, params={}):
        """
        Source Code:
            Code: GroupsController#context_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.context_index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/groups
            url:GET|/api/v1/courses/:course_id/groups

        
        Module: Groups
        Function Description: List the groups available in a context.

        Parameter Desc:
            only_own_groups | |boolean |Will only include groups that the user belongs to if this is set
            include[]       | |string  |`tabs`: Include the list of tabs configured for each group.  See the List available tabs API for more information.                                        Allowed values: tabs
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/groups'
        return self.request(method, api, params)
        
    def show(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.show
        
        Scope:
            url:GET|/api/v1/groups/:group_id

        
        Module: Groups
        Function Description: Get a single group

        Parameter Desc:
            include[] | |string |`permissions`: Include permissions the current user has for the group.                                 `tabs`: Include the list of tabs configured for each group.  See the List available tabs API for more information.                                 Allowed values: permissions, tabs
        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: GroupsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.create
        
        Scope:
            url:POST|/api/v1/groups
            url:POST|/api/v1/group_categories/:group_category_id/groups

        
        Module: Groups
        Function Description: Create a group

        Parameter Desc:
            name             | |string  |The name of the group
            description      | |string  |A description of the group
            is_public        | |boolean |whether the group is public (applies only to community groups)
            join_level       | |string  |no description                                         Allowed values: parent_context_auto_join, parent_context_request, invitation_only
            storage_quota_mb | |integer |The allowed file storage for the group, in megabytes. This parameter is ignored if the caller does not have the manage_storage_quotas permission.
            sis_group_id     | |string  |The sis ID of the group. Must have manage_sis permission to set.
        """
        method = "POST"
        api = f'/api/v1/groups'
        return self.request(method, api, params)
        
    def update(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.update
        
        Scope:
            url:PUT|/api/v1/groups/:group_id

        
        Module: Groups
        Function Description: Edit a group

        Parameter Desc:
            name                    | |string  |The name of the group
            description             | |string  |A description of the group
            is_public               | |boolean |Whether the group is public (applies only to community groups). Currently you cannot set a group back to private once it has been made public.
            join_level              | |string  |no description                                                Allowed values: parent_context_auto_join, parent_context_request, invitation_only
            avatar_id               | |integer |The id of the attachment previously uploaded to the group that you would like to use as the avatar image for this group.
            storage_quota_mb        | |integer |The allowed file storage for the group, in megabytes. This parameter is ignored if the caller does not have the manage_storage_quotas permission.
            members[]               | |string  |An array of user ids for users you would like in the group. Users not in the group will be sent invitations. Existing group members who aren’t in the list will be removed from the group.
            sis_group_id            | |string  |The sis ID of the group. Must have manage_sis permission to set.
            override_sis_stickiness | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "PUT"
        api = f'/api/v1/groups/{group_id}'
        return self.request(method, api, params)
        
    def destroy(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.destroy
        
        Scope:
            url:DELETE|/api/v1/groups/:group_id

        
        Module: Groups
        Function Description: Delete a group

        """
        method = "DELETE"
        api = f'/api/v1/groups/{group_id}'
        return self.request(method, api, params)
        
    def users(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.users
        
        Scope:
            url:GET|/api/v1/groups/:group_id/users

        
        Module: Groups
        Function Description: List group's users

        Parameter Desc:
            search_term      | |string  |The partial name or full ID of the users to match and return in the results list. Must be at least 3 characters.
            include[]        | |string  |`avatar_url`: Include users’ avatar_urls.                                         Allowed values: avatar_url
            exclude_inactive | |boolean |Whether to filter out inactive users from the results. Defaults to false unless explicitly provided.
        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/users'
        return self.request(method, api, params)
        
    def create_file(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.create_file
        
        Scope:
            url:POST|/api/v1/groups/:group_id/files

        
        Module: Groups
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/groups/{group_id}/files'
        return self.request(method, api, params)
        
    def preview_html(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#preview_html,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.preview_html
        
        Scope:
            url:POST|/api/v1/groups/:group_id/preview_html

        
        Module: Groups
        Function Description: Preview processed html

        Parameter Desc:
            html | |string |The html content to process

        Request Example: 
            curl https://<canvas>/api/v1/groups/<group_id>/preview_html \
                 -F 'html=<p><badhtml></badhtml>processed html</p>' \
                 -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "html": "<p>processed html</p>"
            }
        """
        method = "POST"
        api = f'/api/v1/groups/{group_id}/preview_html'
        return self.request(method, api, params)
        
    def activity_stream(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#activity_stream,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.activity_stream
        
        Scope:
            url:GET|/api/v1/groups/:group_id/activity_stream

        
        Module: Groups
        Function Description: Group activity stream

        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/activity_stream'
        return self.request(method, api, params)
        
    def activity_stream_summary(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#activity_stream_summary,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.activity_stream_summary
        
        Scope:
            url:GET|/api/v1/groups/:group_id/activity_stream/summary

        
        Module: Groups
        Function Description: Group activity stream summary

        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/activity_stream/summary'
        return self.request(method, api, params)
        
    def permissions(self, group_id, params={}):
        """
        Source Code:
            Code: GroupsController#permissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.groups.permissions
        
        Scope:
            url:GET|/api/v1/groups/:group_id/permissions

        
        Module: Groups
        Function Description: Permissions

        Parameter Desc:
            permissions[] | |string |List of permissions to check against the authenticated user. Permission names are documented in the Create a role endpoint.

        Request Example: 
            curl https://<canvas>/api/v1/groups/<group_id>/permissions \
              -H 'Authorization: Bearer <token>' \
              -d 'permissions[]=read_roster'
              -d 'permissions[]=send_messages_all'

        Response Example: 
            {'read_roster': 'true', 'send_messages_all': 'false'}
        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/permissions'
        return self.request(method, api, params)
        