from .etc.conf import *
from .res import *

class Outcomes(Res):
    def show(self, id, params={}):
        """
        Source Code:
            Code: OutcomesApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcomes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcomes_api.show
        
        Scope:
            url:GET|/api/v1/outcomes/:id

        
        Module: Outcomes
        Function Description: Show an outcome

        Parameter Desc:
            add_defaults | |boolean |If defaults are requested, then color and mastery level defaults will be added to outcome ratings in the result. This will only take effect if the Account Level Mastery Scales FF is DISABLED
        """
        method = "GET"
        api = f'/api/v1/outcomes/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: OutcomesApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcomes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcomes_api.update
        
        Scope:
            url:PUT|/api/v1/outcomes/:id

        
        Module: Outcomes
        Function Description: Update an outcome

        Parameter Desc:
            title                  | |string  |The new outcome title.
            display_name           | |string  |A friendly name shown in reports for outcomes with cryptic titles, such as common core standards names.
            description            | |string  |The new outcome description.
            vendor_guid            | |string  |A custom GUID for the learning standard.
            mastery_points         | |integer |The new mastery threshold for the embedded rubric criterion.
            ratings[][description] | |string  |The description of a new rating level for the embedded rubric criterion.
            ratings[][points]      | |integer |The points corresponding to a new rating level for the embedded rubric criterion.
            calculation_method     | |string  |The new calculation method.                                               Allowed values: decaying_average, n_mastery, latest, highest, average
            calculation_int        | |integer |The new calculation int.  Only applies if the calculation_method is `decaying_average` or `n_mastery`
            add_defaults           | |boolean |If defaults are requested, then color and mastery level defaults will be added to outcome ratings in the result. This will only take effect if the Account Level Mastery Scales FF is DISABLED
        """
        method = "PUT"
        api = f'/api/v1/outcomes/{id}'
        return self.request(method, api, params)
        
    def outcome_alignments(self, course_id, params={}):
        """
        Source Code:
            Code: OutcomesApiController#outcome_alignments,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcomes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcomes_api.outcome_alignments
        
        Scope:
            url:GET|/api/v1/courses/:course_id/outcome_alignments

        
        Module: Outcomes
        Function Description: Get aligned assignments for an outcome in a course for a particular student

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/outcome_alignments'
        return self.request(method, api, params)
        