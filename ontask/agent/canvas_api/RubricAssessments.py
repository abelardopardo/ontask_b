from .etc.conf import *
from .res import *

class RubricAssessments(Res):
    def create(self, course_id, rubric_association_id, params={}):
        """
        Source Code:
            Code: RubricAssessmentsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_assessments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_assessments.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/rubric_associations/:rubric_association_id/rubric_assessments

        
        Module: RubricAssessments
        Function Description: Create a single rubric assessment

        Parameter Desc:
            course_id             | |integer |The id of the course
            rubric_association_id | |integer |The id of the object with which this rubric assessment is associated
            provisional           | |string  |(optional) Indicates whether this assessment is provisional, defaults to false.
            final                 | |string  |(optional) Indicates a provisional grade will be marked as final. It only takes effect if the provisional param is passed as true. Defaults to false.
            graded_anonymously    | |boolean |(optional) Defaults to false
            rubric_assessment     | |Hash    |A Hash of data to complement the rubric assessment: The user id that refers to the person being assessed                                              rubric_assessment[user_id]                                              Assessment type. There are only three valid types:  ‘grading’, ‘peer_review’, or ‘provisional_grade’                                              rubric_assessment[assessment_type]                                              The points awarded for this row.                                              rubric_assessment[criterion_id][points]                                              Comments to add for this row.                                              rubric_assessment[criterion_id][comments]                                              For each criterion_id, change the id by the criterion number, ex: criterion_123 If the criterion_id is not specified it defaults to false, and nothing is updated.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/rubric_associations/{rubric_association_id}/rubric_assessments'
        return self.request(method, api, params)
        
    def update(self, course_id, rubric_association_id, id, params={}):
        """
        Source Code:
            Code: RubricAssessmentsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_assessments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_assessments.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/rubric_associations/:rubric_association_id/rubric_assessments/:id

        
        Module: RubricAssessments
        Function Description: Update a single rubric assessment

        Parameter Desc:
            id                    | |integer |The id of the rubric assessment
            course_id             | |integer |The id of the course
            rubric_association_id | |integer |The id of the object with which this rubric assessment is associated
            provisional           | |string  |(optional) Indicates whether this assessment is provisional, defaults to false.
            final                 | |string  |(optional) Indicates a provisional grade will be marked as final. It only takes effect if the provisional param is passed as true. Defaults to false.
            graded_anonymously    | |boolean |(optional) Defaults to false
            rubric_assessment     | |Hash    |A Hash of data to complement the rubric assessment: The user id that refers to the person being assessed                                              rubric_assessment[user_id]                                              Assessment type. There are only three valid types:  ‘grading’, ‘peer_review’, or ‘provisional_grade’                                              rubric_assessment[assessment_type]                                              The points awarded for this row.                                              rubric_assessment[criterion_id][points]                                              Comments to add for this row.                                              rubric_assessment[criterion_id][comments]                                              For each criterion_id, change the id by the criterion number, ex: criterion_123 If the criterion_id is not specified it defaults to false, and nothing is updated.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/rubric_associations/{rubric_association_id}/rubric_assessments/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, rubric_association_id, id, params={}):
        """
        Source Code:
            Code: RubricAssessmentsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/rubric_assessments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.rubric_assessments.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/rubric_associations/:rubric_association_id/rubric_assessments/:id

        
        Module: RubricAssessments
        Function Description: Delete a single rubric assessment

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/rubric_associations/{rubric_association_id}/rubric_assessments/{id}'
        return self.request(method, api, params)
        