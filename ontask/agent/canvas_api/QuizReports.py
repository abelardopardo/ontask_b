from .etc.conf import *
from .res import *

class QuizReports(Res):
    def index(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizReportsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_reports.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/reports

        
        Module: Quiz Reports
        Function Description: Retrieve all quiz reports

        Parameter Desc:
            includes_all_versions | |boolean |Whether to retrieve reports that consider all the submissions or only the most recent. Defaults to false, ignored for item_analysis reports.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports'
        return self.request(method, api, params)
        
    def create(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizReportsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_reports.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/reports

        
        Module: Quiz Reports
        Function Description: Create a quiz report

        Parameter Desc:
            quiz_report[report_type]           |Required |string   |The type of report to be generated.                                                                    Allowed values: student_analysis, item_analysis
            quiz_report[includes_all_versions] |         |boolean  |Whether the report should consider all submissions or only the most recent. Defaults to false, ignored for item_analysis.
            include                            |         |String[] |Whether the output should include documents for the file and/or progress objects associated with this report. (Note: JSON-API only)                                                                    Allowed values: file, progress
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports'
        return self.request(method, api, params)
        
    def show(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizReportsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_reports.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/reports/:id

        
        Module: Quiz Reports
        Function Description: Get a quiz report

        Parameter Desc:
            include | |String[] |Whether the output should include documents for the file and/or progress objects associated with this report. (Note: JSON-API only)                                 Allowed values: file, progress
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports/{id}'
        return self.request(method, api, params)
        
    def abort(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizReportsController#abort,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_reports.abort
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/quizzes/:quiz_id/reports/:id

        
        Module: Quiz Reports
        Function Description: Abort the generation of a report, or remove a previously generated one

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports/{id}'
        return self.request(method, api, params)
        