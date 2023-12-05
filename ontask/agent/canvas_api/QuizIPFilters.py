from .etc.conf import *
from .res import *

class QuizIPFilters(Res):
    def index(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizIpFiltersController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_ip_filters_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_ip_filters.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/ip_filters

        
        Module: Quiz IP Filters
        Function Description: Get available quiz IP filters.


        Response Example: 
            {
              "quiz_ip_filters": [QuizIPFilter]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/ip_filters'
        return self.request(method, api, params)
        