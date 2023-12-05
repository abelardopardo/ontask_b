from .etc.conf import *
from .res import *

class OutcomeResults(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: OutcomeResultsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_results.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/outcome_results

        
        Module: Outcome Results
        Function Description: Get outcome results

        Parameter Desc:
            user_ids[]     | |integer |If specified, only the users whose ids are given will be included in the results. SIS ids can be used, prefixed by `sis_user_id:`. It is an error to specify an id for a user who is not a student in the context.
            outcome_ids[]  | |integer |If specified, only the outcomes whose ids are given will be included in the results. it is an error to specify an id for an outcome which is not linked to the context.
            include[]      | |string  |String, `alignments`|`outcomes`|`outcomes.alignments`|`outcome_groups`|`outcome_links`|`outcome_paths`|`users`                                       Specify additional collections to be side loaded with the result. `alignments` includes only the alignments referenced by the returned results. `outcomes.alignments` includes all alignments referenced by outcomes in the context.
            include_hidden | |boolean |If true, results that are hidden from the learning mastery gradebook and student rollup scores will be included

        Response Example: 
            {
              outcome_results: [OutcomeResult]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/outcome_results'
        return self.request(method, api, params)
        
    def rollups(self, course_id, params={}):
        """
        Source Code:
            Code: OutcomeResultsController#rollups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/outcome_results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.outcome_results.rollups
        
        Scope:
            url:GET|/api/v1/courses/:course_id/outcome_rollups

        
        Module: Outcome Results
        Function Description: Get outcome result rollups

        Parameter Desc:
            aggregate           | |string  |If specified, instead of returning one rollup for each user, all the user rollups will be combined into one rollup for the course that will contain the average (or median, see below) rollup score for each outcome.                                            Allowed values: course
            aggregate_stat      | |string  |If aggregate rollups requested, then this value determines what statistic is used for the aggregate. Defaults to `mean` if this value is not specified.                                            Allowed values: mean, median
            user_ids[]          | |integer |If specified, only the users whose ids are given will be included in the results or used in an aggregate result. it is an error to specify an id for a user who is not a student in the context
            outcome_ids[]       | |integer |If specified, only the outcomes whose ids are given will be included in the results. it is an error to specify an id for an outcome which is not linked to the context.
            include[]           | |string  |String, `courses`|`outcomes`|`outcomes.alignments`|`outcome_groups`|`outcome_links`|`outcome_paths`|`users`                                            Specify additional collections to be side loaded with the result.
            exclude[]           | |string  |Specify additional values to exclude. `missing_user_rollups` excludes rollups for users without results.                                            Allowed values: missing_user_rollups
            sort_by             | |string  |If specified, sorts outcome result rollups. `student` sorting will sort by a user’s sortable name. `outcome` sorting will sort by the given outcome’s rollup score. The latter requires specifying the `sort_outcome_id` parameter. By default, the sort order is ascending.                                            Allowed values: student, outcome
            sort_outcome_id     | |integer |If outcome sorting requested, then this determines which outcome to use for rollup score sorting.
            sort_order          | |string  |If sorting requested, then this allows changing the default sort order of ascending to descending.                                            Allowed values: asc, desc
            add_defaults        | |boolean |If defaults are requested, then color and mastery level defaults will be added to outcome ratings in the rollup. This will only take effect if the Account Level Mastery Scales FF is DISABLED
            contributing_scores | |boolean |If contributing scores are requested, then each individual outcome score will also include all graded artifacts that contributed to the outcome score

        Response Example: 
            {
              "rollups": [OutcomeRollup],
              "linked": {
                // (Optional) Included if include[] has outcomes
                "outcomes": [Outcome],
            
                // (Optional) Included if aggregate is not set and include[] has users
                "users": [User],
            
                // (Optional) Included if aggregate is 'course' and include[] has courses
                "courses": [Course]
            
                // (Optional) Included if include[] has outcome_groups
                "outcome_groups": [OutcomeGroup],
            
                // (Optional) Included if include[] has outcome_links
                "outcome_links": [OutcomeLink]
            
                // (Optional) Included if include[] has outcome_paths
                "outcome_paths": [OutcomePath]
            
                // (Optional) Included if include[] has outcomes.alignments
                "outcomes.alignments": [OutcomeAlignment]
              }
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/outcome_rollups'
        return self.request(method, api, params)
        