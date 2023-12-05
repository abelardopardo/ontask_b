from .etc.conf import *
from .res import *

class GroupCategories(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/group_categories
            url:GET|/api/v1/courses/:course_id/group_categories

        
        Module: Group Categories
        Function Description: List group categories for a context

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/group_categories'
        return self.request(method, api, params)
        
    def show(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.show
        
        Scope:
            url:GET|/api/v1/group_categories/:group_category_id

        
        Module: Group Categories
        Function Description: Get a single group category

        """
        method = "GET"
        api = f'/api/v1/group_categories/{group_category_id}'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/group_categories
            url:POST|/api/v1/courses/:course_id/group_categories

        
        Module: Group Categories
        Function Description: Create a Group Category

        Parameter Desc:
            name                  |Required |string  |Name of the group category
            self_signup           |         |string  |Allow students to sign up for a group themselves (Course Only). valid values are:                                                      `enabled`                                                      allows students to self sign up for any group in course                                                      `restricted`                                                      allows students to self sign up only for groups in the same section null disallows self sign up                                                      Allowed values: enabled, restricted
            auto_leader           |         |string  |Assigns group leaders automatically when generating and allocating students to groups Valid values are:                                                      `first`                                                      the first student to be allocated to a group is the leader                                                      `random`                                                      a random student from all members is chosen as the leader                                                      Allowed values: first, random
            group_limit           |         |integer |Limit the maximum number of users in each group (Course Only). Requires self signup.
            sis_group_category_id |         |string  |The unique SIS identifier.
            create_group_count    |         |integer |Create this number of groups (Course Only).
            split_group_count     |         |string  |(Deprecated) Create this number of groups, and evenly distribute students among them. not allowed with `enable_self_signup`. because the group assignment happens synchronously, it’s recommended that you instead use the assign_unassigned_members endpoint. (Course Only)
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/group_categories'
        return self.request(method, api, params)
        
    def import_func(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#import,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.import
        
        Scope:
            url:POST|/api/v1/group_categories/:group_category_id/import

        
        Module: Group Categories
        Function Description: Import category groups

        Parameter Desc:
            attachment | |string |There are two ways to post group category import data - either via a multipart/form-data form-field-style attachment, or via a non-multipart raw post request.                                  ‘attachment’ is required for multipart/form-data style posts. Assumed to be outcome data from a file upload form field named ‘attachment’.                                  Examples:                                  curl -F attachment=@<filename> -H "Authorization: Bearer <token>" \                                      'https://<canvas>/api/v1/group_categories/<category_id>/import'                                  If you decide to do a raw post, you can skip the ‘attachment’ argument, but you will then be required to provide a suitable Content-Type header. You are encouraged to also provide the ‘extension’ argument.                                  Examples:                                  curl -H 'Content-Type: text/csv' --data-binary @<filename>.csv \                                      -H "Authorization: Bearer <token>" \                                      'https://<canvas>/api/v1/group_categories/<category_id>/import'

        Response Example: 
            # Progress (default)
            {
                "completion": 0,
                "context_id": 20,
                "context_type": "GroupCategory",
                "created_at": "2013-07-05T10:57:48-06:00",
                "id": 2,
                "message": null,
                "tag": "course_group_import",
                "updated_at": "2013-07-05T10:57:48-06:00",
                "user_id": null,
                "workflow_state": "running",
                "url": "http://localhost:3000/api/v1/progress/2"
            }
        """
        method = "POST"
        api = f'/api/v1/group_categories/{group_category_id}/import'
        return self.request(method, api, params)
        
    def update(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.update
        
        Scope:
            url:PUT|/api/v1/group_categories/:group_category_id

        
        Module: Group Categories
        Function Description: Update a Group Category

        Parameter Desc:
            name                  | |string  |Name of the group category
            self_signup           | |string  |Allow students to sign up for a group themselves (Course Only). Valid values are:                                              `enabled`                                              allows students to self sign up for any group in course                                              `restricted`                                              allows students to self sign up only for groups in the same section null disallows self sign up                                              Allowed values: enabled, restricted
            auto_leader           | |string  |Assigns group leaders automatically when generating and allocating students to groups Valid values are:                                              `first`                                              the first student to be allocated to a group is the leader                                              `random`                                              a random student from all members is chosen as the leader                                              Allowed values: first, random
            group_limit           | |integer |Limit the maximum number of users in each group (Course Only). Requires self signup.
            sis_group_category_id | |string  |The unique SIS identifier.
            create_group_count    | |integer |Create this number of groups (Course Only).
            split_group_count     | |string  |(Deprecated) Create this number of groups, and evenly distribute students among them. not allowed with `enable_self_signup`. because the group assignment happens synchronously, it’s recommended that you instead use the assign_unassigned_members endpoint. (Course Only)
        """
        method = "PUT"
        api = f'/api/v1/group_categories/{group_category_id}'
        return self.request(method, api, params)
        
    def destroy(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.destroy
        
        Scope:
            url:DELETE|/api/v1/group_categories/:group_category_id

        
        Module: Group Categories
        Function Description: Delete a Group Category

        """
        method = "DELETE"
        api = f'/api/v1/group_categories/{group_category_id}'
        return self.request(method, api, params)
        
    def groups(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#groups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.groups
        
        Scope:
            url:GET|/api/v1/group_categories/:group_category_id/groups

        
        Module: Group Categories
        Function Description: List groups in group category

        """
        method = "GET"
        api = f'/api/v1/group_categories/{group_category_id}/groups'
        return self.request(method, api, params)
        
    def export(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#export,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.export
        
        Scope:
            url:GET|/api/v1/group_categories/:group_category_id/export

        
        Module: Group Categories
        Function Description: export groups in and users in category

        """
        method = "GET"
        api = f'/api/v1/group_categories/{group_category_id}/export'
        return self.request(method, api, params)
        
    def users(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.users
        
        Scope:
            url:GET|/api/v1/group_categories/:group_category_id/users

        
        Module: Group Categories
        Function Description: List users in group category

        Parameter Desc:
            search_term | |string  |The partial name or full ID of the users to match and return in the results list. Must be at least 3 characters.
            unassigned  | |boolean |Set this value to true if you wish only to search unassigned users in the group category.
        """
        method = "GET"
        api = f'/api/v1/group_categories/{group_category_id}/users'
        return self.request(method, api, params)
        
    def assign_unassigned_members(self, group_category_id, params={}):
        """
        Source Code:
            Code: GroupCategoriesController#assign_unassigned_members,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/group_categories_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.group_categories.assign_unassigned_members
        
        Scope:
            url:POST|/api/v1/group_categories/:group_category_id/assign_unassigned_members

        
        Module: Group Categories
        Function Description: Assign unassigned members

        Parameter Desc:
            sync | |boolean |The assigning is done asynchronously by default. If you would like to override this and have the assigning done synchronously, set this value to true.

        Request Example: 
            curl https://<canvas>/api/v1/group_categories/1/assign_unassigned_members \
                 -H 'Authorization: Bearer <token>'

        Response Example: 
            # Progress (default)
            {
                "completion": 0,
                "context_id": 20,
                "context_type": "GroupCategory",
                "created_at": "2013-07-05T10:57:48-06:00",
                "id": 2,
                "message": null,
                "tag": "assign_unassigned_members",
                "updated_at": "2013-07-05T10:57:48-06:00",
                "user_id": null,
                "workflow_state": "running",
                "url": "http://localhost:3000/api/v1/progress/2"
            }# New Group Memberships (when sync = true)
            [
              {
                "id": 65,
                "new_members": [
                  {
                    "user_id": 2,
                    "name": "Sam",
                    "display_name": "Sam",
                    "sections": [
                      {
                        "section_id": 1,
                        "section_code": "Section 1"
                      }
                    ]
                  },
                  {
                    "user_id": 3,
                    "name": "Sue",
                    "display_name": "Sue",
                    "sections": [
                      {
                        "section_id": 2,
                        "section_code": "Section 2"
                      }
                    ]
                  }
                ]
              },
              {
                "id": 66,
                "new_members": [
                  {
                    "user_id": 5,
                    "name": "Joe",
                    "display_name": "Joe",
                    "sections": [
                      {
                        "section_id": 2,
                        "section_code": "Section 2"
                      }
                    ]
                  },
                  {
                    "user_id": 11,
                    "name": "Cecil",
                    "display_name": "Cecil",
                    "sections": [
                      {
                        "section_id": 3,
                        "section_code": "Section 3"
                      }
                    ]
                  }
                ]
              }
            ]
        """
        method = "POST"
        api = f'/api/v1/group_categories/{group_category_id}/assign_unassigned_members'
        return self.request(method, api, params)
        