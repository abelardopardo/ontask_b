from .etc.conf import *
from .res import *

class PeerReviews(Res):
    def index(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: PeerReviewsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/peer_reviews_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.peer_reviews_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/peer_reviews
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews

        
        Module: Peer Reviews
        Function Description: Get all Peer Reviews

        Parameter Desc:
            include[] | |string |Associations to include with the peer review.                                 Allowed values: submission_comments, user
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/peer_reviews'
        return self.request(method, api, params)
        
    def create(self, course_id, assignment_id, submission_id, params={}):
        """
        Source Code:
            Code: PeerReviewsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/peer_reviews_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.peer_reviews_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews
            url:POST|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews

        
        Module: Peer Reviews
        Function Description: Create Peer Review

        Parameter Desc:
            user_id |Required |integer |user_id to assign as reviewer on this assignment
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{submission_id}/peer_reviews'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_id, submission_id, params={}):
        """
        Source Code:
            Code: PeerReviewsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/peer_reviews_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.peer_reviews_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews
            url:DELETE|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews

        
        Module: Peer Reviews
        Function Description: Delete Peer Review

        Parameter Desc:
            user_id |Required |integer |user_id to delete as reviewer on this assignment
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{submission_id}/peer_reviews'
        return self.request(method, api, params)
        