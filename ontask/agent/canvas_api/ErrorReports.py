from .etc.conf import *
from .res import *

class ErrorReports(Res):
    def create(self, params={}):
        """
        Source Code:
            Code: ErrorsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/errors_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.errors.create
        
        Scope:
            url:POST|/api/v1/error_reports

        
        Module: Error Reports
        Function Description: Create Error Report

        Parameter Desc:
            error[subject]  |Required |string         |The summary of the problem
            error[url]      |         |string         |URL from which the report was issued
            error[email]    |         |string         |Email address for the reporting user
            error[comments] |         |string         |The long version of the story from the user one what they experienced
            error[http_env] |         |SerializedHash |A collection of metadata about the users’ environment.  If not provided, canvas will collect it based on information found in the request. (Doesn’t have to be HTTPENV info, could be anything JSON object that can be serialized as a hash, a mobile app might include relevant metadata for itself)
        """
        method = "POST"
        api = f'/api/v1/error_reports'
        return self.request(method, api, params)
        