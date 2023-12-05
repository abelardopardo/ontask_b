from .etc.conf import *
from .res import *

class QuizSubmissionFiles(Res):
    def create(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionFilesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_files.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/submissions/self/files

        
        Module: Quiz Submission Files
        Function Description: Upload a file

        Parameter Desc:
            name         | |string |The name of the quiz submission file
            on_duplicate | |string |How to handle duplicate names

        Response Example: 
            {
              "attachments": [
                {
                  "upload_url": "https://some-bucket.s3.amazonaws.com/",
                  "upload_params": {
                    "key": "/users/1234/files/answer_pic.jpg",
                    "acl": "private",
                    "Filename": "answer_pic.jpg",
                    "AWSAccessKeyId": "some_id",
                    "Policy": "some_opaque_string",
                    "Signature": "another_opaque_string",
                    "Content-Type": "image/jpeg"
                  }
                }
              ]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/self/files'
        return self.request(method, api, params)
        