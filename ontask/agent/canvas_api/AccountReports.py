from .etc.conf import *
from .res import *

class AccountReports(Res):
    def available_reports(self, account_id, params={}):
        """
        Source Code:
            Code: AccountReportsController#available_reports,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_reports.available_reports
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/reports

        
        Module: Account Reports
        Function Description: List Available Reports


        Request Example: 
            curl -H 'Authorization: Bearer <token>' \
                 https://<canvas>/api/v1/accounts/<account_id>/reports/

        Response Example: 
            [
              {
                "report":"student_assignment_outcome_map_csv",
                "title":"Student Competency",
                "parameters":null
              },
              {
                "report":"grade_export_csv",
                "title":"Grade Export",
                "parameters":{
                  "term":{
                    "description":"The canvas id of the term to get grades from",
                    "required":true
                  }
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/reports'
        return self.request(method, api, params)
        
    def create(self, account_id, report, params={}):
        """
        Source Code:
            Code: AccountReportsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_reports.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/reports/:report

        
        Module: Account Reports
        Function Description: Start a Report

        Parameter Desc:
            parameters               | |string  |The parameters will vary for each report. To fetch a list of available parameters for each report, see List Available Reports. A few example parameters have been provided below. Note that the example parameters provided below may not be valid for every report.
            parameters[skip_message] | |boolean |If true, no message will be sent to the user upon completion of the report.
            parameters[course_id]    | |integer |The id of the course to report on. Note: this parameter has been listed to serve as an example and may not be valid for every report.
            parameters[users]        | |boolean |If true, user data will be included. If false, user data will be omitted. Note: this parameter has been listed to serve as an example and may not be valid for every report.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/reports/{report}'
        return self.request(method, api, params)
        
    def index(self, account_id, report, params={}):
        """
        Source Code:
            Code: AccountReportsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_reports.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/reports/:report

        
        Module: Account Reports
        Function Description: Index of Reports

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/reports/{report}'
        return self.request(method, api, params)
        
    def show(self, account_id, report, id, params={}):
        """
        Source Code:
            Code: AccountReportsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_reports.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/reports/:report/:id

        
        Module: Account Reports
        Function Description: Status of a Report

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/reports/{report}/{id}'
        return self.request(method, api, params)
        
    def destroy(self, account_id, report, id, params={}):
        """
        Source Code:
            Code: AccountReportsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_reports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_reports.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/reports/:report/:id

        
        Module: Account Reports
        Function Description: Delete a Report

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/reports/{report}/{id}'
        return self.request(method, api, params)
        