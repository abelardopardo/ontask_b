from .etc.conf import *
from .res import *

class SubmissionComments(Res):
    def update(self, course_id, assignment_id, user_id, id, params={}):
        """
        Source Code:
            Code: SubmissionCommentsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submission_comments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submission_comments_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/comments/:id

        
        Module: Submission Comments
        Function Description: Edit a submission comment

        Parameter Desc:
            comment | |string |If this argument is present, edit the text of a comment.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_id, user_id, id, params={}):
        """
        Source Code:
            Code: SubmissionCommentsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submission_comments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submission_comments_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/comments/:id

        
        Module: Submission Comments
        Function Description: Delete a submission comment

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/{id}'
        return self.request(method, api, params)
        
    def create_file(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionCommentsApiController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submission_comments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submission_comments_api.create_file
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/comments/files

        
        Module: Submission Comments
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/files'
        return self.request(method, api, params)
        