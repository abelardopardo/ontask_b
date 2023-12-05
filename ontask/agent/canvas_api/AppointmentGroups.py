from .etc.conf import *
from .res import *

class AppointmentGroups(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.index
        
        Scope:
            url:GET|/api/v1/appointment_groups

        
        Module: Appointment Groups
        Function Description: List appointment groups

        Parameter Desc:
            scope                     | |string  |Defaults to `reservable`                                                  Allowed values: reservable, manageable
            context_codes[]           | |string  |Array of context codes used to limit returned results.
            include_past_appointments | |boolean |Defaults to false. If true, includes past appointment groups
            include[]                 | |string  |Array of additional information to include.                                                  `appointments`                                                  calendar event time slots for this appointment group                                                  `child_events`                                                  reservations of those time slots                                                  `participant_count`                                                  number of reservations                                                  `reserved_times`                                                  the event id, start time and end time of reservations the current user has made)                                                  `all_context_codes`                                                  all context codes associated with this appointment group                                                  Allowed values: appointments, child_events, participant_count, reserved_times, all_context_codes
        """
        method = "GET"
        api = f'/api/v1/appointment_groups'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.create
        
        Scope:
            url:POST|/api/v1/appointment_groups

        
        Module: Appointment Groups
        Function Description: Create an appointment group

        Parameter Desc:
            appointment_group[context_codes][]                  |Required |string  |Array of context codes (courses, e.g. course_1) this group should be linked to (1 or more). Users in the course(s) with appropriate permissions will be able to sign up for this appointment group.
            appointment_group[sub_context_codes][]              |         |string  |Array of sub context codes (course sections or a single group category) this group should be linked to. Used to limit the appointment group to particular sections. If a group category is specified, students will sign up in groups and the participant_type will be `Group` instead of `User`.
            appointment_group[title]                            |Required |string  |Short title for the appointment group.
            appointment_group[description]                      |         |string  |Longer text description of the appointment group.
            appointment_group[location_name]                    |         |string  |Location name of the appointment group.
            appointment_group[location_address]                 |         |string  |Location address.
            appointment_group[publish]                          |         |boolean |Indicates whether this appointment group should be published (i.e. made available for signup). Once published, an appointment group cannot be unpublished. Defaults to false.
            appointment_group[participants_per_appointment]     |         |integer |Maximum number of participants that may register for each time slot. Defaults to null (no limit).
            appointment_group[min_appointments_per_participant] |         |integer |Minimum number of time slots a user must register for. If not set, users do not need to sign up for any time slots.
            appointment_group[max_appointments_per_participant] |         |integer |Maximum number of time slots a user may register for.
            appointment_group[new_appointments][X][]            |         |string  |Nested array of start time/end time pairs indicating time slots for this appointment group. Refer to the example request.
            appointment_group[participant_visibility]           |         |string  |`private`                                                                                    participants cannot see who has signed up for a particular time slot                                                                                    `protected`                                                                                    participants can see who has signed up.  Defaults to `private`.                                                                                    Allowed values: private, protected
        """
        method = "POST"
        api = f'/api/v1/appointment_groups'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.show
        
        Scope:
            url:GET|/api/v1/appointment_groups/:id

        
        Module: Appointment Groups
        Function Description: Get a single appointment group

        Parameter Desc:
            include[] | |string |Array of additional information to include. See include[] argument of `List appointment groups` action.                                 `child_events`                                 reservations of time slots time slots                                 `appointments`                                 will always be returned                                 `all_context_codes`                                 all context codes associated with this appointment group                                 Allowed values: child_events, appointments, all_context_codes
        """
        method = "GET"
        api = f'/api/v1/appointment_groups/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.update
        
        Scope:
            url:PUT|/api/v1/appointment_groups/:id

        
        Module: Appointment Groups
        Function Description: Update an appointment group

        Parameter Desc:
            appointment_group[context_codes][]                  |Required |string  |Array of context codes (courses, e.g. course_1) this group should be linked to (1 or more). Users in the course(s) with appropriate permissions will be able to sign up for this appointment group.
            appointment_group[sub_context_codes][]              |         |string  |Array of sub context codes (course sections or a single group category) this group should be linked to. Used to limit the appointment group to particular sections. If a group category is specified, students will sign up in groups and the participant_type will be `Group` instead of `User`.
            appointment_group[title]                            |         |string  |Short title for the appointment group.
            appointment_group[description]                      |         |string  |Longer text description of the appointment group.
            appointment_group[location_name]                    |         |string  |Location name of the appointment group.
            appointment_group[location_address]                 |         |string  |Location address.
            appointment_group[publish]                          |         |boolean |Indicates whether this appointment group should be published (i.e. made available for signup). Once published, an appointment group cannot be unpublished. Defaults to false.
            appointment_group[participants_per_appointment]     |         |integer |Maximum number of participants that may register for each time slot. Defaults to null (no limit).
            appointment_group[min_appointments_per_participant] |         |integer |Minimum number of time slots a user must register for. If not set, users do not need to sign up for any time slots.
            appointment_group[max_appointments_per_participant] |         |integer |Maximum number of time slots a user may register for.
            appointment_group[new_appointments][X][]            |         |string  |Nested array of start time/end time pairs indicating time slots for this appointment group. Refer to the example request.
            appointment_group[participant_visibility]           |         |string  |`private`                                                                                    participants cannot see who has signed up for a particular time slot                                                                                    `protected`                                                                                    participants can see who has signed up. Defaults to `private`.                                                                                    Allowed values: private, protected
        """
        method = "PUT"
        api = f'/api/v1/appointment_groups/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.destroy
        
        Scope:
            url:DELETE|/api/v1/appointment_groups/:id

        
        Module: Appointment Groups
        Function Description: Delete an appointment group

        Parameter Desc:
            cancel_reason | |string |Reason for deleting/canceling the appointment group.
        """
        method = "DELETE"
        api = f'/api/v1/appointment_groups/{id}'
        return self.request(method, api, params)
        
    def users(self, id, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.users
        
        Scope:
            url:GET|/api/v1/appointment_groups/:id/users

        
        Module: Appointment Groups
        Function Description: List user participants

        Parameter Desc:
            registration_status | |string |Limits results to the a given participation status, defaults to `all`                                           Allowed values: all, registered, registered
        """
        method = "GET"
        api = f'/api/v1/appointment_groups/{id}/users'
        return self.request(method, api, params)
        
    def groups(self, id, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#groups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.groups
        
        Scope:
            url:GET|/api/v1/appointment_groups/:id/groups

        
        Module: Appointment Groups
        Function Description: List student group participants

        Parameter Desc:
            registration_status | |string |Limits results to the a given participation status, defaults to `all`                                           Allowed values: all, registered, registered
        """
        method = "GET"
        api = f'/api/v1/appointment_groups/{id}/groups'
        return self.request(method, api, params)
        
    def next_appointment(self, params={}):
        """
        Source Code:
            Code: AppointmentGroupsController#next_appointment,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/appointment_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.appointment_groups.next_appointment
        
        Scope:
            url:GET|/api/v1/appointment_groups/next_appointment

        
        Module: Appointment Groups
        Function Description: Get next appointment

        Parameter Desc:
            appointment_group_ids[] | |string |List of ids of appointment groups to search.
        """
        method = "GET"
        api = f'/api/v1/appointment_groups/next_appointment'
        return self.request(method, api, params)
        