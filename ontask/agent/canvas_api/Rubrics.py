from .etc.conf import *
from .res import *

class Rubrics(Res):
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: RubricsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubrics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubrics.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/rubrics

        
        Module: Rubrics
        Function Description: Create a single rubric

        Parameter Desc:
            id                                   | |integer |The id of the rubric
            rubric_association_id                | |integer |The id of the object with which this rubric is associated
            rubric[title]                        | |string  |The title of the rubric
            rubric[free_form_criterion_comments] | |boolean |Whether or not you can write custom comments in the ratings field for a rubric
            rubric_association[association_id]   | |integer |The id of the object with which this rubric is associated
            rubric_association[association_type] | |string  |The type of object this rubric is associated with                                                             Allowed values: Assignment, Course, Account
            rubric_association[use_for_grading]  | |boolean |Whether or not the associated rubric is used for grade calculation
            rubric_association[hide_score_total] | |boolean |Whether or not the score total is displayed within the rubric. This option is only available if the rubric is not used for grading.
            rubric_association[purpose]          | |string  |Whether or not the association is for grading (and thus linked to an assignment) or if it’s to indicate the rubric should appear in its context
            rubric[criteria]                     | |Hash    |An indexed Hash of RubricCriteria objects where the keys are integer ids and the values are the RubricCriteria objects
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/rubrics'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: RubricsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubrics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubrics.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/rubrics/:id

        
        Module: Rubrics
        Function Description: Update a single rubric

        Parameter Desc:
            id                                    | |integer |The id of the rubric
            rubric_association_id                 | |integer |The id of the object with which this rubric is associated
            rubric[title]                         | |string  |The title of the rubric
            rubric[free_form_criterion_comments]  | |boolean |Whether or not you can write custom comments in the ratings field for a rubric
            rubric[skip_updating_points_possible] | |boolean |Whether or not to update the points possible
            rubric_association[association_id]    | |integer |The id of the object with which this rubric is associated
            rubric_association[association_type]  | |string  |The type of object this rubric is associated with                                                              Allowed values: Assignment, Course, Account
            rubric_association[use_for_grading]   | |boolean |Whether or not the associated rubric is used for grade calculation
            rubric_association[hide_score_total]  | |boolean |Whether or not the score total is displayed within the rubric. This option is only available if the rubric is not used for grading.
            rubric_association[purpose]           | |string  |Whether or not the association is for grading (and thus linked to an assignment) or if it’s to indicate the rubric should appear in its context                                                              Allowed values: grading, bookmark
            rubric[criteria]                      | |Hash    |An indexed Hash of RubricCriteria objects where the keys are integer ids and the values are the RubricCriteria objects
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/rubrics/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: RubricsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubrics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubrics.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/rubrics/:id

        
        Module: Rubrics
        Function Description: Delete a single rubric

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/rubrics/{id}'
        return self.request(method, api, params)
        
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: RubricsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubrics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubrics_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/rubrics
            url:GET|/api/v1/courses/:course_id/rubrics

        
        Module: Rubrics
        Function Description: List rubrics

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/rubrics'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: RubricsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubrics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubrics_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/rubrics/:id
            url:GET|/api/v1/courses/:course_id/rubrics/:id

        
        Module: Rubrics
        Function Description: Get a single rubric

        Parameter Desc:
            include[] | |string |Related records to include in the response.                                 Allowed values: assessments, graded_assessments, peer_assessments, associations, assignment_associations, course_associations, account_associations
            style     | |string |Applicable only if assessments are being returned. If included, returns either all criteria data associated with the assessment, or just the comments. If not included, both data and comments are omitted.                                 Allowed values: full, comments_only
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/rubrics/{id}'
        return self.request(method, api, params)
        