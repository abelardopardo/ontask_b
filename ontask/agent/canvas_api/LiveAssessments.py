from .etc.conf import *
from .res import *

class LiveAssessments(Res):
    def create(self, course_id, assessment_id, params={}):
        """
        Source Code:
            Code: LiveAssessments::ResultsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/live_assessments/results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.live_assessments/results.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/live_assessments/:assessment_id/results

        
        Module: LiveAssessments
        Function Description: Create live assessment results


        Request Example: 
            {
              "results": [{
                "passed": false,
                "assessed_at": "2014-05-26T14:57:23-07:00",
                "links": {
                  "user": "15"
                }
              },{
                "passed": true,
                "assessed_at": "2014-05-26T13:05:40-07:00",
                "links": {
                  "user": "16"
                }
              }]
            }

        Response Example: 
            {
              "results": [Result]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/live_assessments/{assessment_id}/results'
        return self.request(method, api, params)
        
    def index(self, course_id, assessment_id, params={}):
        """
        Source Code:
            Code: LiveAssessments::ResultsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/live_assessments/results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.live_assessments/results.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/live_assessments/:assessment_id/results

        
        Module: LiveAssessments
        Function Description: List live assessment results

        Parameter Desc:
            user_id | |integer |If set, restrict results to those for this user

        Response Example: 
            {
              "results": [Result]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/live_assessments/{assessment_id}/results'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: LiveAssessments::AssessmentsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/live_assessments/assessments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.live_assessments/assessments.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/live_assessments

        
        Module: LiveAssessments
        Function Description: Create or find a live assessment


        Request Example: 
            {
              "assessments": [{
                "key": "2014-05-27-Outcome-52",
                "title": "Tuesday's LiveAssessment",
                "links": {
                  "outcome": "1"
                }
              }]
            }

        Response Example: 
            {
              "links": {
                "assessments.results": "http://example.com/courses/1/live_assessments/5/results"
              },
              "assessments": [Assessment]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/live_assessments'
        return self.request(method, api, params)
        
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: LiveAssessments::AssessmentsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/live_assessments/assessments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.live_assessments/assessments.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/live_assessments

        
        Module: LiveAssessments
        Function Description: List live assessments


        Response Example: 
            {
              "links": {
                "assessments.results": "http://example.com/courses/1/live_assessments/{assessments.id}/results"
              },
              "assessments": [Assessment]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/live_assessments'
        return self.request(method, api, params)
        