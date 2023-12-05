from .etc.conf import *
from .res import *

class GradingPeriods(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: GradingPeriodsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_periods_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_periods.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/grading_periods
            url:GET|/api/v1/courses/:course_id/grading_periods

        
        Module: Grading Periods
        Function Description: List grading periods


        Response Example: 
            {
              "grading_periods": [GradingPeriod]
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/grading_periods'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: GradingPeriodsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_periods_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_periods.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/grading_periods/:id

        
        Module: Grading Periods
        Function Description: Get a single grading period


        Response Example: 
            {
              "grading_periods": [GradingPeriod]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/grading_periods/{id}'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: GradingPeriodsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_periods_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_periods.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/grading_periods/:id

        
        Module: Grading Periods
        Function Description: Update a single grading period

        Parameter Desc:
            grading_periods[][start_date] |Required |Date   |The date the grading period starts.
            grading_periods[][end_date]   |Required |Date   |no description
            grading_periods[][weight]     |         |number |A weight value that contributes to the overall weight of a grading period set which is used to calculate how much assignments in this period contribute to the total grade

        Response Example: 
            {
              "grading_periods": [GradingPeriod]
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/grading_periods/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: GradingPeriodsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_periods_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_periods.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/grading_periods/:id
            url:DELETE|/api/v1/accounts/:account_id/grading_periods/:id

        
        Module: Grading Periods
        Function Description: Delete a grading period

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/grading_periods/{id}'
        return self.request(method, api, params)
        
    def batch_update(self, course_id, params={}):
        """
        Source Code:
            Code: GradingPeriodsController#batch_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_periods_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_periods.batch_update
        
        Scope:
            url:PATCH|/api/v1/courses/:course_id/grading_periods/batch_update
            url:PATCH|/api/v1/grading_period_sets/:set_id/grading_periods/batch_update

        
        Module: Grading Periods
        Function Description: Batch update grading periods

        Parameter Desc:
            set_id                        |Required |string |The id of the grading period set.
            grading_periods[][id]         |         |string |The id of the grading period. If the id parameter does not exist, a new grading period will be created.
            grading_periods[][title]      |Required |string |The title of the grading period. The title is required for creating a new grading period, but not for updating an existing grading period.
            grading_periods[][start_date] |Required |Date   |The date the grading period starts. The start_date is required for creating a new grading period, but not for updating an existing grading period.
            grading_periods[][end_date]   |Required |Date   |The date the grading period ends. The end_date is required for creating a new grading period, but not for updating an existing grading period.
            grading_periods[][close_date] |Required |Date   |The date after which grades can no longer be changed for a grading period. The close_date is required for creating a new grading period, but not for updating an existing grading period.
            grading_periods[][weight]     |         |number |A weight value that contributes to the overall weight of a grading period set which is used to calculate how much assignments in this period contribute to the total grade

        Response Example: 
            {
              "grading_periods": [GradingPeriod]
            }
        """
        method = "PATCH"
        api = f'/api/v1/courses/{course_id}/grading_periods/batch_update'
        return self.request(method, api, params)
        