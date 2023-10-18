from .etc.conf import *
from .res import *

class AssignmentGroups(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentGroupsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_groups.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignment_groups

        
        Module: Assignment Groups
        Function Description: List assignment groups

        Parameter Desc:
            include[]                             | |string  |Associations to include with the group. `discussion_topic`, `all_dates`, `can_edit`, `assignment_visibility` & `submission` are only valid if `assignments` is also included. `score_statistics` requires that the `assignments` and `submission` options are included. The `assignment_visibility` option additionally requires that the Differentiated Assignments course feature be turned on. If `observed_users` is passed along with `assignments` and `submission`, submissions for observed users will also be included as an array.                                                              Allowed values: assignments, discussion_topic, all_dates, assignment_visibility, overrides, submission, observed_users, can_edit, score_statistics
            assignment_ids[]                      | |string  |If `assignments` are included, optionally return only assignments having their ID in this array. This argument may also be passed as a comma separated string.
            exclude_assignment_submission_types[] | |string  |If `assignments` are included, those with the specified submission types will be excluded from the assignment groups.                                                              Allowed values: online_quiz, discussion_topic, wiki_page, external_tool
            override_assignment_dates             | |boolean |Apply assignment overrides for each assignment, defaults to true.
            grading_period_id                     | |integer |The id of the grading period in which assignment groups are being requested (Requires grading periods to exist.)
            scope_assignments_to_student          | |boolean |If true, all assignments returned will apply to the current user in the specified grading period. If assignments apply to other students in the specified grading period, but not the current user, they will not be returned. (Requires the grading_period_id argument and grading periods to exist. In addition, the current user must be a student.)
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignment_groups'
        return self.request(method, api, params)
        
    def show(self, course_id, assignment_group_id, params={}):
        """
        Source Code:
            Code: AssignmentGroupsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_groups_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignment_groups/:assignment_group_id

        
        Module: Assignment Groups
        Function Description: Get an Assignment Group

        Parameter Desc:
            include[]                 | |string  |Associations to include with the group. `discussion_topic` and `assignment_visibility` and `submission` are only valid if `assignments` is also included. `score_statistics` is only valid if `submission` and `assignments` are also included. The `assignment_visibility` option additionally requires that the Differentiated Assignments course feature be turned on.                                                  Allowed values: assignments, discussion_topic, assignment_visibility, submission, score_statistics
            override_assignment_dates | |boolean |Apply assignment overrides for each assignment, defaults to true.
            grading_period_id         | |integer |The id of the grading period in which assignment groups are being requested (Requires grading periods to exist on the account)
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignment_groups/{assignment_group_id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentGroupsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_groups_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignment_groups

        
        Module: Assignment Groups
        Function Description: Create an Assignment Group

        Parameter Desc:
            name             | |string  |The assignment group’s name
            position         | |integer |The position of this assignment group in relation to the other assignment groups
            group_weight     | |number  |The percent of the total grade that this assignment group represents
            sis_source_id    | |string  |The sis source id of the Assignment Group
            integration_data | |Object  |The integration data of the Assignment Group
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignment_groups'
        return self.request(method, api, params)
        
    def update(self, course_id, assignment_group_id, params={}):
        """
        Source Code:
            Code: AssignmentGroupsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_groups_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignment_groups/:assignment_group_id

        
        Module: Assignment Groups
        Function Description: Edit an Assignment Group

        Parameter Desc:
            name             | |string  |The assignment group’s name
            position         | |integer |The position of this assignment group in relation to the other assignment groups
            group_weight     | |number  |The percent of the total grade that this assignment group represents
            sis_source_id    | |string  |The sis source id of the Assignment Group
            integration_data | |Object  |The integration data of the Assignment Group
            rules            | |string  |The grading rules that are applied within this assignment group See the Assignment Group object definition for format
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignment_groups/{assignment_group_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_group_id, params={}):
        """
        Source Code:
            Code: AssignmentGroupsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_groups_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_groups_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignment_groups/:assignment_group_id

        
        Module: Assignment Groups
        Function Description: Destroy an Assignment Group

        Parameter Desc:
            move_assignments_to | |integer |The ID of an active Assignment Group to which the assignments that are currently assigned to the destroyed Assignment Group will be assigned. NOTE: If this argument is not provided, any assignments in this Assignment Group will be deleted.
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignment_groups/{assignment_group_id}'
        return self.request(method, api, params)
        