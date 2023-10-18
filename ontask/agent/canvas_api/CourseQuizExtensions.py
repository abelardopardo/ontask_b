from .etc.conf import *
from .res import *

class CourseQuizExtensions(Res):
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: Quizzes::CourseQuizExtensionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/course_quiz_extensions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/course_quiz_extensions.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quiz_extensions

        
        Module: Course Quiz Extensions
        Function Description: Set extensions for student quiz submissions

        Parameter Desc:
            user_id            |Required |integer |The ID of the user we want to add quiz extensions for.
            extra_attempts     |         |integer |Number of times the student is allowed to re-take the quiz over the multiple-attempt limit. This is limited to 1000 attempts or less.
            extra_time         |         |integer |The number of extra minutes to allow for all attempts. This will add to the existing time limit on the submission. This is limited to 10080 minutes (1 week)
            manually_unlocked  |         |boolean |Allow the student to take the quiz even if it’s locked for everyone else.
            extend_from_now    |         |integer |The number of minutes to extend the quiz from the current time. This is mutually exclusive to extend_from_end_at. This is limited to 1440 minutes (24 hours)
            extend_from_end_at |         |integer |The number of minutes to extend the quiz beyond the quiz’s current ending time. This is mutually exclusive to extend_from_now. This is limited to 1440 minutes (24 hours)

        Request Example: 
            {
              "quiz_extensions": [{
                "user_id": 3,
                "extra_attempts": 2,
                "extra_time": 20,
                "manually_unlocked": true
              },{
                "user_id": 2,
                "extra_attempts": 2,
                "extra_time": 20,
                "manually_unlocked": false
              }]
            }{
              "quiz_extensions": [{
                "user_id": 3,
                "extend_from_now": 20
              }]
            }

        Response Example: 
            {
              "quiz_extensions": [QuizExtension]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quiz_extensions'
        return self.request(method, api, params)
        