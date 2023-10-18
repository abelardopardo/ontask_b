from .etc.conf import *
from .res import *

class Progress(Res):
    def show(self, id, params={}):
        """
        Source Code:
            Code: ProgressController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/progress_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.progress.show
        
        Scope:
            url:GET|/api/v1/progress/:id

        
        Module: Progress
        Function Description: Query progress

        """
        method = "GET"
        api = f'/api/v1/progress/{id}'
        return self.request(method, api, params)
        
    def cancel(self, id, params={}):
        """
        Source Code:
            Code: ProgressController#cancel,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/progress_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.progress.cancel
        
        Scope:
            url:POST|/api/v1/progress/:id/cancel

        
        Module: Progress
        Function Description: Cancel progress

        """
        method = "POST"
        api = f'/api/v1/progress/{id}/cancel'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: Lti::Ims::ProgressController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/progress_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/progress.show
        
        Scope:
            url:GET|/api/lti/courses/:course_id/progress/:id

        
        Module: Progress
        Function Description: Query progress

        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/progress/{id}'
        return self.request(method, api, params)
        