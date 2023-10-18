from .etc.conf import *
from .res import *

class CalendarEvents(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.index
        
        Scope:
            url:GET|/api/v1/calendar_events

        
        Module: Calendar Events
        Function Description: List calendar events

        Parameter Desc:
            type            | |string  |Defaults to `event`                                        Allowed values: event, assignment
            start_date      | |Date    |Only return events since the start_date (inclusive). Defaults to today. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            end_date        | |Date    |Only return events before the end_date (inclusive). Defaults to start_date. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ. If end_date is the same as start_date, then only events on that day are returned.
            undated         | |boolean |Defaults to false (dated events only). If true, only return undated events and ignore start_date and end_date.
            all_events      | |boolean |Defaults to false (uses start_date, end_date, and undated criteria). If true, all events are returned, ignoring start_date, end_date, and undated criteria.
            context_codes[] | |string  |List of context codes of courses/groups/users whose events you want to see. If not specified, defaults to the current user (i.e personal calendar, no course/group events). Limited to 10 context codes, additional ones are ignored. The format of this field is the context type, followed by an underscore, followed by the context id. For example: course_42
            excludes[]      | |Array   |Array of attributes to exclude. Possible values are `description`, `child_events` and `assignment`
            includes[]      | |Array   |Array of optional attributes to include. Possible values are `web_conferenes` and `series_natural_language`
            important_dates | |boolean |Defaults to false. If true, only events with important dates set to true will be returned.
            blackout_date   | |boolean |Defaults to false. If true, only events with blackout date set to true will be returned.
        """
        method = "GET"
        api = f'/api/v1/calendar_events'
        return self.request(method, api, params)
        
    def user_index(self, user_id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#user_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.user_index
        
        Scope:
            url:GET|/api/v1/users/:user_id/calendar_events

        
        Module: Calendar Events
        Function Description: List calendar events for a user

        Parameter Desc:
            type                       | |string  |Defaults to `event`                                                   Allowed values: event, assignment
            start_date                 | |Date    |Only return events since the start_date (inclusive). Defaults to today. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            end_date                   | |Date    |Only return events before the end_date (inclusive). Defaults to start_date. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ. If end_date is the same as start_date, then only events on that day are returned.
            undated                    | |boolean |Defaults to false (dated events only). If true, only return undated events and ignore start_date and end_date.
            all_events                 | |boolean |Defaults to false (uses start_date, end_date, and undated criteria). If true, all events are returned, ignoring start_date, end_date, and undated criteria.
            context_codes[]            | |string  |List of context codes of courses/groups/users whose events you want to see. If not specified, defaults to the current user (i.e personal calendar, no course/group events). Limited to 10 context codes, additional ones are ignored. The format of this field is the context type, followed by an underscore, followed by the context id. For example: course_42
            excludes[]                 | |Array   |Array of attributes to exclude. Possible values are `description`, `child_events` and `assignment`
            submission_types[]         | |Array   |When type is `assignment`, specifies the allowable submission types for returned assignments. Ignored if type is not `assignment` or if exclude_submission_types is provided.
            exclude_submission_types[] | |Array   |When type is `assignment`, specifies the submission types to be excluded from the returned assignments. Ignored if type is not `assignment`.
            includes[]                 | |Array   |Array of optional attributes to include. Possible values are `web_conferenes` and `series_natural_language`
            important_dates            | |boolean |Defaults to false If true, only events with important dates set to true will be returned.
            blackout_date              | |boolean |Defaults to false If true, only events with blackout date set to true will be returned.
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/calendar_events'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.create
        
        Scope:
            url:POST|/api/v1/calendar_events

        
        Module: Calendar Events
        Function Description: Create a calendar event

        Parameter Desc:
            calendar_event[context_code]                      |Required |string   |Context code of the course/group/user whose calendar this event should be added to.
            calendar_event[title]                             |         |string   |Short title for the calendar event.
            calendar_event[description]                       |         |string   |Longer HTML description of the event.
            calendar_event[start_at]                          |         |DateTime |Start date/time of the event.
            calendar_event[end_at]                            |         |DateTime |End date/time of the event.
            calendar_event[location_name]                     |         |string   |Location name of the event.
            calendar_event[location_address]                  |         |string   |Location address
            calendar_event[time_zone_edited]                  |         |string   |Time zone of the user editing the event. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            calendar_event[all_day]                           |         |boolean  |When true event is considered to span the whole day and times are ignored.
            calendar_event[child_event_data][X][start_at]     |         |DateTime |Section-level start time(s) if this is a course event. X can be any identifier, provided that it is consistent across the start_at, end_at and context_code
            calendar_event[child_event_data][X][end_at]       |         |DateTime |Section-level end time(s) if this is a course event.
            calendar_event[child_event_data][X][context_code] |         |string   |Context code(s) corresponding to the section-level start and end time(s).
            calendar_event[duplicate][count]                  |         |number   |Number of times to copy/duplicate the event.  Count cannot exceed 200.
            calendar_event[duplicate][interval]               |         |number   |Defaults to 1 if duplicate ‘count` is set.  The interval between the duplicated events.
            calendar_event[duplicate][frequency]              |         |string   |Defaults to `weekly`.  The frequency at which to duplicate the event                                                                                   Allowed values: daily, weekly, monthly
            calendar_event[duplicate][append_iterator]        |         |boolean  |Defaults to false.  If set to ‘true`, an increasing counter number will be appended to the event title when the event is duplicated.  (e.g. Event 1, Event 2, Event 3, etc)
            calendar_event[rrule]                             |         |string   |If the calendar_series flag is enabled, this parameter replaces the calendar_event’s duplicate parameter to create a series of recurring events. Its value is the iCalendar RRULE defining how the event repeats, though unending series not supported.
            calendar_event[blackout_date]                     |         |boolean  |If the blackout_date is true, this event represents a holiday or some other special day that does not count in course pacing.
        """
        method = "POST"
        api = f'/api/v1/calendar_events'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.show
        
        Scope:
            url:GET|/api/v1/calendar_events/:id

        
        Module: Calendar Events
        Function Description: Get a single calendar event or assignment

        """
        method = "GET"
        api = f'/api/v1/calendar_events/{id}'
        return self.request(method, api, params)
        
    def reserve(self, id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#reserve,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.reserve
        
        Scope:
            url:POST|/api/v1/calendar_events/:id/reservations
            url:POST|/api/v1/calendar_events/:id/reservations/:participant_id

        
        Module: Calendar Events
        Function Description: Reserve a time slot

        Parameter Desc:
            participant_id  | |string  |User or group id for whom you are making the reservation (depends on the participant type). Defaults to the current user (or user’s candidate group).
            comments        | |string  |Comments to associate with this reservation
            cancel_existing | |boolean |Defaults to false. If true, cancel any previous reservation(s) for this participant and appointment group.
        """
        method = "POST"
        api = f'/api/v1/calendar_events/{id}/reservations'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.update
        
        Scope:
            url:PUT|/api/v1/calendar_events/:id

        
        Module: Calendar Events
        Function Description: Update a calendar event

        Parameter Desc:
            calendar_event[context_code]                      | |string   |Context code of the course/group/user to move this event to. Scheduler appointments and events with section-specific times cannot be moved between calendars.
            calendar_event[title]                             | |string   |Short title for the calendar event.
            calendar_event[description]                       | |string   |Longer HTML description of the event.
            calendar_event[start_at]                          | |DateTime |Start date/time of the event.
            calendar_event[end_at]                            | |DateTime |End date/time of the event.
            calendar_event[location_name]                     | |string   |Location name of the event.
            calendar_event[location_address]                  | |string   |Location address
            calendar_event[time_zone_edited]                  | |string   |Time zone of the user editing the event. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            calendar_event[all_day]                           | |boolean  |When true event is considered to span the whole day and times are ignored.
            calendar_event[child_event_data][X][start_at]     | |DateTime |Section-level start time(s) if this is a course event. X can be any identifier, provided that it is consistent across the start_at, end_at and context_code
            calendar_event[child_event_data][X][end_at]       | |DateTime |Section-level end time(s) if this is a course event.
            calendar_event[child_event_data][X][context_code] | |string   |Context code(s) corresponding to the section-level start and end time(s).
            calendar_event[rrule]                             | |string   |Valid if the calendar_series feature is enabled and the event whose ID is in the URL is part of a series. This defines the shape of the recurring event series after it’s updated. Its value is the iCalendar RRULE, though unending series not supported.
            which                                             | |string   |Valid if the calendar_series feature is enabled and the event whose ID is in the URL is part of a series. Update just the event whose ID is in in the URL, all events in the series, or the given event and all those following.                                                                           Allowed values: one, all, following
            calendar_event[blackout_date]                     | |boolean  |If the blackout_date is true, this event represents a holiday or some other special day that does not count in course pacing.
        """
        method = "PUT"
        api = f'/api/v1/calendar_events/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.destroy
        
        Scope:
            url:DELETE|/api/v1/calendar_events/:id

        
        Module: Calendar Events
        Function Description: Delete a calendar event

        Parameter Desc:
            cancel_reason | |string |Reason for deleting/canceling the event.
            which         | |string |Valid if the calendar_series feature is enabled and the event whose ID is in the URL is part of a series. Delete just the event whose ID is in in the URL, all events in the series, or the given event and all those following.                                     Allowed values: one, all, following
        """
        method = "DELETE"
        api = f'/api/v1/calendar_events/{id}'
        return self.request(method, api, params)
        
    def save_enabled_account_calendars(self, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#save_enabled_account_calendars,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.save_enabled_account_calendars
        
        Scope:
            url:POST|/api/v1/calendar_events/save_enabled_account_calendars

        
        Module: Calendar Events
        Function Description: Save enabled account calendars

        Parameter Desc:
            mark_feature_as_seen        | |boolean |Flag to mark account calendars feature as seen
            enabled_account_calendars[] | |Array   |An array of account Ids to remember in the calendars list of the user
        """
        method = "POST"
        api = f'/api/v1/calendar_events/save_enabled_account_calendars'
        return self.request(method, api, params)
        
    def set_course_timetable(self, course_id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#set_course_timetable,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.set_course_timetable
        
        Scope:
            url:POST|/api/v1/courses/:course_id/calendar_events/timetable

        
        Module: Calendar Events
        Function Description: Set a course timetable

        Parameter Desc:
            timetables[course_section_id][]                | |Array  |An array of timetable objects for the course section specified by course_section_id. If course_section_id is set to `all`, events will be created for the entire course.
            timetables[course_section_id][][weekdays]      | |string |A comma-separated list of abbreviated weekdays (Mon-Monday, Tue-Tuesday, Wed-Wednesday, Thu-Thursday, Fri-Friday, Sat-Saturday, Sun-Sunday)
            timetables[course_section_id][][start_time]    | |string |Time to start each event at (e.g. `9:00 am`)
            timetables[course_section_id][][end_time]      | |string |Time to end each event at (e.g. `9:00 am`)
            timetables[course_section_id][][location_name] | |string |A location name to set for each event
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/calendar_events/timetable'
        return self.request(method, api, params)
        
    def get_course_timetable(self, course_id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#get_course_timetable,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.get_course_timetable
        
        Scope:
            url:GET|/api/v1/courses/:course_id/calendar_events/timetable

        
        Module: Calendar Events
        Function Description: Get course timetable

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/calendar_events/timetable'
        return self.request(method, api, params)
        
    def set_course_timetable_events(self, course_id, params={}):
        """
        Source Code:
            Code: CalendarEventsApiController#set_course_timetable_events,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/calendar_events_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.calendar_events_api.set_course_timetable_events
        
        Scope:
            url:POST|/api/v1/courses/:course_id/calendar_events/timetable_events

        
        Module: Calendar Events
        Function Description: Create or update events directly for a course timetable

        Parameter Desc:
            course_section_id       | |string   |Events will be created for the course section specified by course_section_id. If not present, events will be created for the entire course.
            events[]                | |Array    |An array of event objects to use.
            events[][start_at]      | |DateTime |Start time for the event
            events[][end_at]        | |DateTime |End time for the event
            events[][location_name] | |string   |Location name for the event
            events[][code]          | |string   |A unique identifier that can be used to update the event at a later time If one is not specified, an identifier will be generated based on the start and end times
            events[][title]         | |string   |Title for the meeting. If not present, will default to the associated course’s name
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/calendar_events/timetable_events'
        return self.request(method, api, params)
        