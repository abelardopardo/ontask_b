from .etc.conf import *
from .res import *

class FeatureFlags(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/features
            url:GET|/api/v1/accounts/:account_id/features
            url:GET|/api/v1/users/:user_id/features

        
        Module: Feature Flags
        Function Description: List features

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/features'
        return self.request(method, api, params)
        
    def enabled_features(self, course_id, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#enabled_features,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.enabled_features
        
        Scope:
            url:GET|/api/v1/courses/:course_id/features/enabled
            url:GET|/api/v1/accounts/:account_id/features/enabled
            url:GET|/api/v1/users/:user_id/features/enabled

        
        Module: Feature Flags
        Function Description: List enabled features


        Request Example: 
            curl 'http://<canvas>/api/v1/courses/1/features/enabled' \
              -H "Authorization: Bearer <token>"

        Response Example: 
            ["fancy_wickets", "automatic_essay_grading", "telepathic_navigation"]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/features/enabled'
        return self.request(method, api, params)
        
    def environment(self, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#environment,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.environment
        
        Scope:
            url:GET|/api/v1/features/environment

        
        Module: Feature Flags
        Function Description: List environment features


        Request Example: 
            curl 'http://<canvas>/api/v1/features/environment' \
              -H "Authorization: Bearer <token>"

        Response Example: 
            { "telepathic_navigation": true, "fancy_wickets": true, "automatic_essay_grading": false }
        """
        method = "GET"
        api = f'/api/v1/features/environment'
        return self.request(method, api, params)
        
    def show(self, course_id, feature, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/features/flags/:feature
            url:GET|/api/v1/accounts/:account_id/features/flags/:feature
            url:GET|/api/v1/users/:user_id/features/flags/:feature

        
        Module: Feature Flags
        Function Description: Get feature flag

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/features/flags/{feature}'
        return self.request(method, api, params)
        
    def update(self, course_id, feature, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/features/flags/:feature
            url:PUT|/api/v1/accounts/:account_id/features/flags/:feature
            url:PUT|/api/v1/users/:user_id/features/flags/:feature

        
        Module: Feature Flags
        Function Description: Set feature flag

        Parameter Desc:
            state | |string |`off`                             The feature is not available for the course, user, or account and sub-accounts.                             `allowed`                             (valid only on accounts) The feature is off in the account, but may be enabled in sub-accounts and courses by setting a feature flag on the sub-account or course.                             `on`                             The feature is turned on unconditionally for the user, course, or account and sub-accounts.                             Allowed values: off, allowed, on
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/features/flags/{feature}'
        return self.request(method, api, params)
        
    def delete(self, course_id, feature, params={}):
        """
        Source Code:
            Code: FeatureFlagsController#delete,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/feature_flags_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.feature_flags.delete
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/features/flags/:feature
            url:DELETE|/api/v1/accounts/:account_id/features/flags/:feature
            url:DELETE|/api/v1/users/:user_id/features/flags/:feature

        
        Module: Feature Flags
        Function Description: Remove feature flag

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/features/flags/{feature}'
        return self.request(method, api, params)
        