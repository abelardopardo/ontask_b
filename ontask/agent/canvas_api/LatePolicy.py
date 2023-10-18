from .etc.conf import *
from .res import *

class LatePolicy(Res):
    def show(self, id, params={}):
        """
        Source Code:
            Code: LatePolicyController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/late_policy_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.late_policy.show
        
        Scope:
            url:GET|/api/v1/courses/:id/late_policy

        
        Module: Late Policy
        Function Description: Get a late policy


        Response Example: 
            {
              "late_policy": LatePolicy
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{id}/late_policy'
        return self.request(method, api, params)
        
    def create(self, id, params={}):
        """
        Source Code:
            Code: LatePolicyController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/late_policy_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.late_policy.create
        
        Scope:
            url:POST|/api/v1/courses/:id/late_policy

        
        Module: Late Policy
        Function Description: Create a late policy

        Parameter Desc:
            late_policy[missing_submission_deduction_enabled]    | |boolean |Whether to enable the missing submission deduction late policy.
            late_policy[missing_submission_deduction]            | |number  |How many percentage points to deduct from a missing submission.
            late_policy[late_submission_deduction_enabled]       | |boolean |Whether to enable the late submission deduction late policy.
            late_policy[late_submission_deduction]               | |number  |How many percentage points to deduct per the late submission interval.
            late_policy[late_submission_interval]                | |string  |The interval for late policies.
            late_policy[late_submission_minimum_percent_enabled] | |boolean |Whether to enable the late submission minimum percent for a late policy.
            late_policy[late_submission_minimum_percent]         | |number  |The minimum grade a submissions can have in percentage points.

        Response Example: 
            {
              "late_policy": LatePolicy
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{id}/late_policy'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: LatePolicyController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/late_policy_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.late_policy.update
        
        Scope:
            url:PATCH|/api/v1/courses/:id/late_policy

        
        Module: Late Policy
        Function Description: Patch a late policy

        Parameter Desc:
            late_policy[missing_submission_deduction_enabled]    | |boolean |Whether to enable the missing submission deduction late policy.
            late_policy[missing_submission_deduction]            | |number  |How many percentage points to deduct from a missing submission.
            late_policy[late_submission_deduction_enabled]       | |boolean |Whether to enable the late submission deduction late policy.
            late_policy[late_submission_deduction]               | |number  |How many percentage points to deduct per the late submission interval.
            late_policy[late_submission_interval]                | |string  |The interval for late policies.
            late_policy[late_submission_minimum_percent_enabled] | |boolean |Whether to enable the late submission minimum percent for a late policy.
            late_policy[late_submission_minimum_percent]         | |number  |The minimum grade a submissions can have in percentage points.
        """
        method = "PATCH"
        api = f'/api/v1/courses/{id}/late_policy'
        return self.request(method, api, params)
        