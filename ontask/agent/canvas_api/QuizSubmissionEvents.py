from .etc.conf import *
from .res import *

class QuizSubmissionEvents(Res):
    def create(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionEventsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_events_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id/events

        
        Module: Quiz Submission Events
        Function Description: Submit captured events

        Parameter Desc:
            quiz_submission_events[] |Required |Array |The submission events to be recorded
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}/events'
        return self.request(method, api, params)
        
    def index(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionEventsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_events_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id/events

        
        Module: Quiz Submission Events
        Function Description: Retrieve captured events

        Parameter Desc:
            attempt | |integer |The specific submission attempt to look up the events for. If unspecified, the latest attempt will be used.

        Response Example: 
            {
              "quiz_submission_events": [
                {
                  "id": "3409",
                  "event_type": "page_blurred",
                  "event_data": null,
                  "created_at": "2014-11-16T13:37:21Z"
                },
                {
                  "id": "3410",
                  "event_type": "page_focused",
                  "event_data": null,
                  "created_at": "2014-11-16T13:37:27Z"
                }
              ]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}/events'
        return self.request(method, api, params)
        