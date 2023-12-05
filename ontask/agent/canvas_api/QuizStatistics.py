from .etc.conf import *
from .res import *

class QuizStatistics(Res):
    def index(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizStatisticsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_statistics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_statistics.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/statistics

        
        Module: Quiz Statistics
        Function Description: Fetching the latest quiz statistics

        Parameter Desc:
            all_versions | |boolean |Whether the statistics report should include all submissions attempts.

        Response Example: 
            {
              "quiz_statistics": [ QuizStatistics ]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/statistics'
        return self.request(method, api, params)
        