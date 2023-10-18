from .etc.conf import *
from .res import *

class EnrollmentTerms(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: TermsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/terms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.terms.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/terms

        
        Module: Enrollment Terms
        Function Description: Create enrollment term

        Parameter Desc:
            enrollment_term[name]                                 | |string   |The name of the term.
            enrollment_term[start_at]                             | |DateTime |The day/time the term starts. Accepts times in ISO 8601 format, e.g. 2015-01-10T18:48:00Z.
            enrollment_term[end_at]                               | |DateTime |The day/time the term ends. Accepts times in ISO 8601 format, e.g. 2015-01-10T18:48:00Z.
            enrollment_term[sis_term_id]                          | |string   |The unique SIS identifier for the term.
            enrollment_term[overrides][enrollment_type][start_at] | |DateTime |The day/time the term starts, overridden for the given enrollment type. enrollment_type can be one of StudentEnrollment, TeacherEnrollment, TaEnrollment, or DesignerEnrollment
            enrollment_term[overrides][enrollment_type][end_at]   | |DateTime |The day/time the term ends, overridden for the given enrollment type. enrollment_type can be one of StudentEnrollment, TeacherEnrollment, TaEnrollment, or DesignerEnrollment
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/terms'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: TermsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/terms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.terms.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/terms/:id

        
        Module: Enrollment Terms
        Function Description: Update enrollment term

        Parameter Desc:
            enrollment_term[name]                                 | |string   |The name of the term.
            enrollment_term[start_at]                             | |DateTime |The day/time the term starts. Accepts times in ISO 8601 format, e.g. 2015-01-10T18:48:00Z.
            enrollment_term[end_at]                               | |DateTime |The day/time the term ends. Accepts times in ISO 8601 format, e.g. 2015-01-10T18:48:00Z.
            enrollment_term[sis_term_id]                          | |string   |The unique SIS identifier for the term.
            enrollment_term[overrides][enrollment_type][start_at] | |DateTime |The day/time the term starts, overridden for the given enrollment type. enrollment_type can be one of StudentEnrollment, TeacherEnrollment, TaEnrollment, or DesignerEnrollment
            enrollment_term[overrides][enrollment_type][end_at]   | |DateTime |The day/time the term ends, overridden for the given enrollment type. enrollment_type can be one of StudentEnrollment, TeacherEnrollment, TaEnrollment, or DesignerEnrollment
            override_sis_stickiness                               | |boolean  |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/terms/{id}'
        return self.request(method, api, params)
        
    def destroy(self, account_id, id, params={}):
        """
        Source Code:
            Code: TermsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/terms_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.terms.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/terms/:id

        
        Module: Enrollment Terms
        Function Description: Delete enrollment term

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/terms/{id}'
        return self.request(method, api, params)
        
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: TermsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/terms_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.terms_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/terms

        
        Module: Enrollment Terms
        Function Description: List enrollment terms

        Parameter Desc:
            workflow_state[] | |string |If set, only returns terms that are in the given state. Defaults to ‘active’.                                        Allowed values: active, deleted, all
            include[]        | |string |Array of additional information to include.                                        `overrides`                                        term start/end dates overridden for different enrollment types                                        `course_count`                                        the number of courses in each term                                        Allowed values: overrides

        Request Example: 
            curl -H 'Authorization: Bearer <token>' \
            https://<canvas>/api/v1/accounts/1/terms?include[]=overrides

        Response Example: 
            {
              "enrollment_terms": [
                {
                  "id": 1,
                  "name": "Fall 20X6"
                  "start_at": "2026-08-31T20:00:00Z",
                  "end_at": "2026-12-20T20:00:00Z",
                  "created_at": "2025-01-02T03:43:11Z",
                  "workflow_state": "active",
                  "grading_period_group_id": 1,
                  "sis_term_id": null,
                  "overrides": {
                    "StudentEnrollment": {
                      "start_at": "2026-09-03T20:00:00Z",
                      "end_at": "2026-12-19T20:00:00Z"
                    },
                    "TeacherEnrollment": {
                      "start_at": null,
                      "end_at": "2026-12-30T20:00:00Z"
                    }
                  }
                }
              ]
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/terms'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: TermsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/terms_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.terms_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/terms/:id

        
        Module: Enrollment Terms
        Function Description: Retrieve enrollment term

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/terms/{id}'
        return self.request(method, api, params)
        