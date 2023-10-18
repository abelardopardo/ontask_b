from .etc.conf import *
from .res import *

class Result(Res):
    def index(self, course_id, line_item_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::ResultsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/results.index
        
        Scope:
            url:GET|/api/lti/courses/:course_id/line_items/:line_item_id/results

        
        Module: Result
        Function Description: Show a collection of Results

        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/line_items/{line_item_id}/results'
        return self.request(method, api, params)
        
    def show(self, course_id, line_item_id, id, params={}):
        """
        Source Code:
            Code: Lti::Ims::ResultsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/results_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/results.show
        
        Scope:
            url:GET|/api/lti/courses/:course_id/line_items/:line_item_id/results/:id

        
        Module: Result
        Function Description: Show a Result

        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/line_items/{line_item_id}/results/{id}'
        return self.request(method, api, params)
        