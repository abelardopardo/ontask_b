from .etc.conf import *
from .res import *

class OriginalityReports(Res):
    def create(self, assignment_id, submission_id, params={}):
        """
        Source Code:
            Code: Lti::OriginalityReportsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/originality_reports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/originality_reports_api.create
        
        Scope:
            url:POST|/api/lti/assignments/:assignment_id/submissions/:submission_id/originality_report

        
        Module: Originality Reports
        Function Description: Create an Originality Report

        Parameter Desc:
            originality_report[file_id]                          |         |integer |The id of the file being given an originality score. Required if creating a report associated with a file.
            originality_report[originality_score]                |Required |number  |A number between 0 and 100 representing the measure of the specified file’s originality.
            originality_report[originality_report_url]           |         |string  |The URL where the originality report for the specified file may be found.
            originality_report[originality_report_file_id]       |         |integer |The ID of the file within Canvas that contains the originality report for the submitted file provided in the request URL.
            originality_report[tool_setting][resource_type_code] |         |string  |The resource type code of the resource handler Canvas should use for the LTI launch for viewing originality reports. If set Canvas will launch to the message with type ‘basic-lti-launch-request’ in the specified resource handler rather than using the originality_report_url.
            originality_report[tool_setting][resource_url]       |         |string  |The URL Canvas should launch to when showing an LTI originality report. Note that this value is inferred from the specified resource handler’s message `path` value (See ‘resource_type_code`) unless it is specified. If this parameter is used a `resource_type_code` must also be specified.
            originality_report[workflow_state]                   |         |string  |May be set to `pending`, `error`, or `scored`. If an originality score is provided a workflow state of `scored` will be inferred.
            originality_report[error_message]                    |         |string  |A message describing the error. If set, the `workflow_state` will be set to `error.`
            originality_report[attempt]                          |         |integer |If no ‘file_id` is given, and no file is required for the assignment (that is, the assignment allows an online text entry), this parameter may be given to clarify which attempt number the report is for (in the case of resubmissions). If this field is omitted and no `file_id` is given, the report will be created (or updated, if it exists) for the first submission attempt with no associated file.
        """
        method = "POST"
        api = f'/api/lti/assignments/{assignment_id}/submissions/{submission_id}/originality_report'
        return self.request(method, api, params)
        
    def update(self, assignment_id, submission_id, id, params={}):
        """
        Source Code:
            Code: Lti::OriginalityReportsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/originality_reports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/originality_reports_api.update
        
        Scope:
            url:PUT|/api/lti/assignments/:assignment_id/submissions/:submission_id/originality_report/:id
            url:PUT|/api/lti/assignments/:assignment_id/files/:file_id/originality_report

        
        Module: Originality Reports
        Function Description: Edit an Originality Report

        Parameter Desc:
            originality_report[originality_score]                | |number  |A number between 0 and 100 representing the measure of the specified file’s originality.
            originality_report[originality_report_url]           | |string  |The URL where the originality report for the specified file may be found.
            originality_report[originality_report_file_id]       | |integer |The ID of the file within Canvas that contains the originality report for the submitted file provided in the request URL.
            originality_report[tool_setting][resource_type_code] | |string  |The resource type code of the resource handler Canvas should use for the LTI launch for viewing originality reports. If set Canvas will launch to the message with type ‘basic-lti-launch-request’ in the specified resource handler rather than using the originality_report_url.
            originality_report[tool_setting][resource_url]       | |string  |The URL Canvas should launch to when showing an LTI originality report. Note that this value is inferred from the specified resource handler’s message `path` value (See ‘resource_type_code`) unless it is specified. If this parameter is used a `resource_type_code` must also be specified.
            originality_report[workflow_state]                   | |string  |May be set to `pending`, `error`, or `scored`. If an originality score is provided a workflow state of `scored` will be inferred.
            originality_report[error_message]                    | |string  |A message describing the error. If set, the `workflow_state` will be set to `error.`
        """
        method = "PUT"
        api = f'/api/lti/assignments/{assignment_id}/submissions/{submission_id}/originality_report/{id}'
        return self.request(method, api, params)
        
    def show(self, assignment_id, submission_id, id, params={}):
        """
        Source Code:
            Code: Lti::OriginalityReportsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/originality_reports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/originality_reports_api.show
        
        Scope:
            url:GET|/api/lti/assignments/:assignment_id/submissions/:submission_id/originality_report/:id
            url:GET|/api/lti/assignments/:assignment_id/files/:file_id/originality_report

        
        Module: Originality Reports
        Function Description: Show an Originality Report

        """
        method = "GET"
        api = f'/api/lti/assignments/{assignment_id}/submissions/{submission_id}/originality_report/{id}'
        return self.request(method, api, params)
        