from .etc.conf import *
from .res import *

class GradingPeriodSets(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: GradingPeriodSetsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_period_sets_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_period_sets.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/grading_period_sets

        
        Module: Grading Period Sets
        Function Description: List grading period sets


        Response Example: 
            {
              "grading_period_set": [GradingPeriodGroup]
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/grading_period_sets'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: GradingPeriodSetsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_period_sets_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_period_sets.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/grading_period_sets

        
        Module: Grading Period Sets
        Function Description: Create a grading period set

        Parameter Desc:
            enrollment_term_ids[]                                        |         |Array   |A list of associated term ids for the grading period set
            grading_period_set[][title]                                  |Required |string  |The title of the grading period set
            grading_period_set[][weighted]                               |         |boolean |A boolean to determine whether the grading periods in the set are weighted
            grading_period_set[][display_totals_for_all_grading_periods] |         |boolean |A boolean to determine whether the totals for all grading periods in the set are displayed

        Response Example: 
            {
              "grading_period_set": [GradingPeriodGroup]
            }
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/grading_period_sets'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: GradingPeriodSetsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_period_sets_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_period_sets.update
        
        Scope:
            url:PATCH|/api/v1/accounts/:account_id/grading_period_sets/:id

        
        Module: Grading Period Sets
        Function Description: Update a grading period set

        Parameter Desc:
            enrollment_term_ids[]                                        |         |Array   |A list of associated term ids for the grading period set
            grading_period_set[][title]                                  |Required |string  |The title of the grading period set
            grading_period_set[][weighted]                               |         |boolean |A boolean to determine whether the grading periods in the set are weighted
            grading_period_set[][display_totals_for_all_grading_periods] |         |boolean |A boolean to determine whether the totals for all grading periods in the set are displayed
        """
        method = "PATCH"
        api = f'/api/v1/accounts/{account_id}/grading_period_sets/{id}'
        return self.request(method, api, params)
        
    def destroy(self, account_id, id, params={}):
        """
        Source Code:
            Code: GradingPeriodSetsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/grading_period_sets_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.grading_period_sets.destroy
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/grading_period_sets/:id

        
        Module: Grading Period Sets
        Function Description: Delete a grading period set

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/grading_period_sets/{id}'
        return self.request(method, api, params)
        