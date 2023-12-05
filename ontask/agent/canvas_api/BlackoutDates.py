from .etc.conf import *
from .res import *

class BlackoutDates(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blackout_dates
            url:GET|/api/v1/accounts/:account_id/blackout_dates

        
        Module: Blackout Dates
        Function Description: List blackout dates

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blackout_dates'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blackout_dates/:id
            url:GET|/api/v1/accounts/:account_id/blackout_dates/:id

        
        Module: Blackout Dates
        Function Description: Get a single blackout date

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blackout_dates/{id}'
        return self.request(method, api, params)
        
    def new(self, course_id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#new,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.new
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blackout_dates/new
            url:GET|/api/v1/accounts/:account_id/blackout_dates/new

        
        Module: Blackout Dates
        Function Description: New Blackout Date

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blackout_dates/new'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/blackout_dates
            url:POST|/api/v1/accounts/:account_id/blackout_dates

        
        Module: Blackout Dates
        Function Description: Create Blackout Date

        Parameter Desc:
            start_date  | |Date   |The start date of the blackout date.
            end_date    | |Date   |The end date of the blackout date.
            event_title | |string |The title of the blackout date.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/blackout_dates'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/blackout_dates/:id
            url:PUT|/api/v1/accounts/:account_id/blackout_dates/:id

        
        Module: Blackout Dates
        Function Description: Update Blackout Date

        Parameter Desc:
            start_date  | |Date   |The start date of the blackout date.
            end_date    | |Date   |The end date of the blackout date.
            event_title | |string |The title of the blackout date.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/blackout_dates/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/blackout_dates/:id
            url:DELETE|/api/v1/accounts/:account_id/blackout_dates/:id

        
        Module: Blackout Dates
        Function Description: Delete Blackout Date

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/blackout_dates/{id}'
        return self.request(method, api, params)
        
    def bulk_update(self, course_id, params={}):
        """
        Source Code:
            Code: BlackoutDatesController#bulk_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/blackout_dates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.blackout_dates.bulk_update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/blackout_dates

        
        Module: Blackout Dates
        Function Description: Update a list of Blackout Dates

        Parameter Desc:
            blackout_dates: | |string |blackout_date, …                                       An object containing the array of BlackoutDates we want to exist after this operation. For array entries, if it has an id it will be updated, if not created, and if an existing BlackoutDate id is missing from the array, it will be deleted.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/blackout_dates'
        return self.request(method, api, params)
        