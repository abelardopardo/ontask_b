from .etc.conf import *
from .res import *

class AccountCalendars(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.index
        
        Scope:
            url:GET|/api/v1/account_calendars

        
        Module: Account Calendars
        Function Description: List available account calendars

        Parameter Desc:
            search_term | |string |When included, searches available account calendars for the term. Returns matching results. Term must be at least 2 characters.
        """
        method = "GET"
        api = f'/api/v1/account_calendars'
        return self.request(method, api, params)
        
    def show(self, account_id, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.show
        
        Scope:
            url:GET|/api/v1/account_calendars/:account_id

        
        Module: Account Calendars
        Function Description: Get a single account calendar

        """
        method = "GET"
        api = f'/api/v1/account_calendars/{account_id}'
        return self.request(method, api, params)
        
    def update(self, account_id, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.update
        
        Scope:
            url:PUT|/api/v1/account_calendars/:account_id

        
        Module: Account Calendars
        Function Description: Update a calendar

        Parameter Desc:
            visible        | |boolean |Allow administrators with ‘manage_account_calendar_events` permission to create events on this calendar, and allow users to view this calendar and its events.
            auto_subscribe | |boolean |When true, users will automatically see events from this account in their calendar, even if they haven’t manually added that calendar.
        """
        method = "PUT"
        api = f'/api/v1/account_calendars/{account_id}'
        return self.request(method, api, params)
        
    def bulk_update(self, account_id, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#bulk_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.bulk_update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/account_calendars

        
        Module: Account Calendars
        Function Description: Update several calendars

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/account_calendars'
        return self.request(method, api, params)
        
    def all_calendars(self, account_id, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#all_calendars,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.all_calendars
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/account_calendars

        
        Module: Account Calendars
        Function Description: List all account calendars

        Parameter Desc:
            search_term | |string |When included, searches all descendent accounts of provided account for the term. Returns matching results. Term must be at least 2 characters. Can be combined with a filter value.
            filter      | |string |When included, only returns calendars that are either visible or hidden. Can be combined with a search term.                                   Allowed values: visible, hidden
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/account_calendars'
        return self.request(method, api, params)
        
    def visible_calendars_count(self, account_id, params={}):
        """
        Source Code:
            Code: AccountCalendarsApiController#visible_calendars_count,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_calendars_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_calendars_api.visible_calendars_count
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/visible_calendars_count

        
        Module: Account Calendars
        Function Description: Count of all visible account calendars

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/visible_calendars_count'
        return self.request(method, api, params)
        