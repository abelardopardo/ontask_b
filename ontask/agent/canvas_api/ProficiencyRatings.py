from .etc.conf import *
from .res import *

class ProficiencyRatings(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: OutcomeProficiencyApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_proficiency_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_proficiency_api.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/outcome_proficiency
            url:POST|/api/v1/courses/:course_id/outcome_proficiency

        
        Module: Proficiency Ratings
        Function Description: Create/update proficiency ratings

        Parameter Desc:
            ratings[][description] | |string  |The description of the rating level.
            ratings[][points]      | |integer |The non-negative number of points of the rating level. Points across ratings should be strictly decreasing in value.
            ratings[][mastery]     | |integer |Indicates the rating level where mastery is first achieved. Only one rating in a proficiency should be marked for mastery.
            ratings[][color]       | |integer |The color associated with the rating level. Should be a hex color code like ‘00FFFF’.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/outcome_proficiency'
        return self.request(method, api, params)
        
    def show(self, account_id, params={}):
        """
        Source Code:
            Code: OutcomeProficiencyApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_proficiency_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_proficiency_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/outcome_proficiency
            url:GET|/api/v1/courses/:course_id/outcome_proficiency

        
        Module: Proficiency Ratings
        Function Description: Get proficiency ratings

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/outcome_proficiency'
        return self.request(method, api, params)
        