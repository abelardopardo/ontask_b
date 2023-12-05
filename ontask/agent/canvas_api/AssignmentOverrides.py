from .etc.conf import *
from .res import *

class AssignmentOverrides(Res):
    def index(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/overrides

        
        Module: Assignment Overrides
        Function Description: List assignment overrides

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/overrides'
        return self.request(method, api, params)
        
    def show(self, course_id, assignment_id, id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/overrides/:id

        
        Module: Assignment Overrides
        Function Description: Get a single assignment override

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/overrides/{id}'
        return self.request(method, api, params)
        
    def group_alias(self, group_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#group_alias,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.group_alias
        
        Scope:
            url:GET|/api/v1/groups/:group_id/assignments/:assignment_id/override

        
        Module: Assignment Overrides
        Function Description: Redirect to the assignment override for a group

        """
        method = "GET"
        api = f'/api/v1/groups/{group_id}/assignments/{assignment_id}/override'
        return self.request(method, api, params)
        
    def section_alias(self, course_section_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#section_alias,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.section_alias
        
        Scope:
            url:GET|/api/v1/sections/:course_section_id/assignments/:assignment_id/override

        
        Module: Assignment Overrides
        Function Description: Redirect to the assignment override for a section

        """
        method = "GET"
        api = f'/api/v1/sections/{course_section_id}/assignments/{assignment_id}/override'
        return self.request(method, api, params)
        
    def create(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/overrides

        
        Module: Assignment Overrides
        Function Description: Create an assignment override

        Parameter Desc:
            assignment_override[student_ids][]     | |integer  |The IDs of the override’s target students. If present, the IDs must each identify a user with an active student enrollment in the course that is not already targetted by a different adhoc override.
            assignment_override[title]             | |string   |The title of the adhoc assignment override. Required if student_ids is present, ignored otherwise (the title is set to the name of the targetted group or section instead).
            assignment_override[group_id]          | |integer  |The ID of the override’s target group. If present, the following conditions must be met for the override to be successful:                                                                the assignment MUST be a group assignment (a group_category_id is assigned to it)                                                                the ID must identify an active group in the group set the assignment is in                                                                the ID must not be targetted by a different override                                                                See Appendix: Group assignments for more info.
            assignment_override[course_section_id] | |integer  |The ID of the override’s target section. If present, must identify an active section of the assignment’s course not already targetted by a different override.
            assignment_override[due_at]            | |DateTime |The day/time the overridden assignment is due. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect due date. May be present but null to indicate the override removes any previous due date.
            assignment_override[unlock_at]         | |DateTime |The day/time the overridden assignment becomes unlocked. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect the unlock date. May be present but null to indicate the override removes any previous unlock date.
            assignment_override[lock_at]           | |DateTime |The day/time the overridden assignment becomes locked. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect the lock date. May be present but null to indicate the override removes any previous lock date.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/overrides'
        return self.request(method, api, params)
        
    def update(self, course_id, assignment_id, id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/overrides/:id

        
        Module: Assignment Overrides
        Function Description: Update an assignment override

        Parameter Desc:
            assignment_override[student_ids][] | |integer  |The IDs of the override’s target students. If present, the IDs must each identify a user with an active student enrollment in the course that is not already targetted by a different adhoc override. Ignored unless the override being updated is adhoc.
            assignment_override[title]         | |string   |The title of an adhoc assignment override. Ignored unless the override being updated is adhoc.
            assignment_override[due_at]        | |DateTime |The day/time the overridden assignment is due. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect due date. May be present but null to indicate the override removes any previous due date.
            assignment_override[unlock_at]     | |DateTime |The day/time the overridden assignment becomes unlocked. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect the unlock date. May be present but null to indicate the override removes any previous unlock date.
            assignment_override[lock_at]       | |DateTime |The day/time the overridden assignment becomes locked. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z. If absent, this override will not affect the lock date. May be present but null to indicate the override removes any previous lock date.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/overrides/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_id, id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignments/:assignment_id/overrides/:id

        
        Module: Assignment Overrides
        Function Description: Delete an assignment override

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/overrides/{id}'
        return self.request(method, api, params)
        
    def batch_retrieve(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#batch_retrieve,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.batch_retrieve
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/overrides

        
        Module: Assignment Overrides
        Function Description: Batch retrieve overrides in a course

        Parameter Desc:
            assignment_overrides[][id]            |Required |string |Ids of overrides to retrieve
            assignment_overrides[][assignment_id] |Required |string |Ids of assignments for each override
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/overrides'
        return self.request(method, api, params)
        
    def batch_create(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#batch_create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.batch_create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/overrides

        
        Module: Assignment Overrides
        Function Description: Batch create overrides in a course

        Parameter Desc:
            assignment_overrides[] |Required |AssignmentOverride |Attributes for the new assignment overrides. See Create an assignment override for available attributes
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/overrides'
        return self.request(method, api, params)
        
    def batch_update(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentOverridesController#batch_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignment_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignment_overrides.batch_update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/overrides

        
        Module: Assignment Overrides
        Function Description: Batch update overrides in a course

        Parameter Desc:
            assignment_overrides[] |Required |AssignmentOverride |Attributes for the updated overrides.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/overrides'
        return self.request(method, api, params)
        