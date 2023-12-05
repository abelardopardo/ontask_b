from .etc.conf import *
from .res import *

class QuizSubmissionUserList(Res):
    def message(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionUsersController#message,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_users.message
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:id/submission_users/message

        
        Module: Quiz Submission User List
        Function Description: Send a message to unsubmitted or submitted users for the quiz

        Parameter Desc:
            conversations | |QuizUserConversation |Body and recipients to send the message to.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}/submission_users/message'
        return self.request(method, api, params)
        