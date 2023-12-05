from .etc.conf import *
from .res import *

class QuizSubmissions(Res):
    def index(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions

        
        Module: Quiz Submissions
        Function Description: Get all quiz submissions.

        Parameter Desc:
            include[] | |string |Associations to include with the quiz submission.                                 Allowed values: submission, quiz, user

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions'
        return self.request(method, api, params)
        
    def submission(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#submission,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.submission
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/submission

        
        Module: Quiz Submissions
        Function Description: Get the quiz submission.

        Parameter Desc:
            include[] | |string |Associations to include with the quiz submission.                                 Allowed values: submission, quiz, user

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submission'
        return self.request(method, api, params)
        
    def show(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id

        
        Module: Quiz Submissions
        Function Description: Get a single quiz submission.

        Parameter Desc:
            include[] | |string |Associations to include with the quiz submission.                                 Allowed values: submission, quiz, user

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions

        
        Module: Quiz Submissions
        Function Description: Create the quiz submission (start a quiz-taking session)

        Parameter Desc:
            access_code | |string  |Access code for the Quiz, if any.
            preview     | |boolean |Whether this should be a preview QuizSubmission and not count towards the user’s course record. Teachers only.

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions'
        return self.request(method, api, params)
        
    def update(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id

        
        Module: Quiz Submissions
        Function Description: Update student question scores and comments.

        Parameter Desc:
            quiz_submissions[][attempt]      |Required |integer |The attempt number of the quiz submission that should be updated. This attempt MUST be already completed.
            quiz_submissions[][fudge_points] |         |number  |Amount of positive or negative points to fudge the total score by.
            quiz_submissions[][questions]    |         |Hash    |A set of scores and comments for each question answered by the student. The keys are the question IDs, and the values are hashes of ‘score` and `comment` entries. See Appendix: Manual Scoring for more on this parameter.

        Request Example: 
            {
              "quiz_submissions": [{
                "attempt": 1,
                "fudge_points": -2.4,
                "questions": {
                  "1": {
                    "score": 2.5,
                    "comment": "This can't be right, but I'll let it pass this one time."
                  },
                  "2": {
                    "score": 0,
                    "comment": "Good thinking. Almost!"
                  }
                }
              }]
            }

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}'
        return self.request(method, api, params)
        
    def complete(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#complete,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.complete
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id/complete

        
        Module: Quiz Submissions
        Function Description: Complete the quiz submission (turn it in).

        Parameter Desc:
            attempt          |Required |integer |The attempt number of the quiz submission that should be completed. Note that this must be the latest attempt index, as earlier attempts can not be modified.
            validation_token |Required |string  |The unique validation token you received when this Quiz Submission was created.
            access_code      |         |string  |Access code for the Quiz, if any.

        Response Example: 
            {
              "quiz_submissions": [QuizSubmission]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}/complete'
        return self.request(method, api, params)
        
    def time(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionsApiController#time,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submissions_api.time
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id/time

        
        Module: Quiz Submissions
        Function Description: Get current quiz submission times.


        Response Example: 
            {
              "end_at": [DateTime],
              "time_left": [Integer]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}/time'
        return self.request(method, api, params)
        