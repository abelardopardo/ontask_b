from .etc.conf import *
from .res import *

class RubricAssociations(Res):
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: RubricAssociationsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_associations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_associations.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/rubric_associations

        
        Module: RubricAssociations
        Function Description: Create a RubricAssociation

        Parameter Desc:
            rubric_association[rubric_id]        | |integer |The id of the Rubric
            rubric_association[association_id]   | |integer |The id of the object with which this rubric is associated
            rubric_association[association_type] | |string  |The type of object this rubric is associated with                                                             Allowed values: Assignment, Course, Account
            rubric_association[title]            | |string  |The name of the object this rubric is associated with
            rubric_association[use_for_grading]  | |boolean |Whether or not the associated rubric is used for grade calculation
            rubric_association[hide_score_total] | |boolean |Whether or not the score total is displayed within the rubric. This option is only available if the rubric is not used for grading.
            rubric_association[purpose]          | |string  |Whether or not the association is for grading (and thus linked to an assignment) or if it’s to indicate the rubric should appear in its context                                                             Allowed values: grading, bookmark
            rubric_association[bookmarked]       | |boolean |Whether or not the associated rubric appears in its context
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/rubric_associations'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: RubricAssociationsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_associations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_associations.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/rubric_associations/:id

        
        Module: RubricAssociations
        Function Description: Update a RubricAssociation

        Parameter Desc:
            id                                   | |integer |The id of the RubricAssociation to update
            rubric_association[rubric_id]        | |integer |The id of the Rubric
            rubric_association[association_id]   | |integer |The id of the object with which this rubric is associated
            rubric_association[association_type] | |string  |The type of object this rubric is associated with                                                             Allowed values: Assignment, Course, Account
            rubric_association[title]            | |string  |The name of the object this rubric is associated with
            rubric_association[use_for_grading]  | |boolean |Whether or not the associated rubric is used for grade calculation
            rubric_association[hide_score_total] | |boolean |Whether or not the score total is displayed within the rubric. This option is only available if the rubric is not used for grading.
            rubric_association[purpose]          | |string  |Whether or not the association is for grading (and thus linked to an assignment) or if it’s to indicate the rubric should appear in its context                                                             Allowed values: grading, bookmark
            rubric_association[bookmarked]       | |boolean |Whether or not the associated rubric appears in its context
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/rubric_associations/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: RubricAssociationsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_associations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_associations.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/rubric_associations/:id

        
        Module: RubricAssociations
        Function Description: Delete a RubricAssociation

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/rubric_associations/{id}'
        return self.request(method, api, params)
        