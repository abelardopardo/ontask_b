from .etc.conf import *
from .res import *

class Users(Res):
    def api_index(self, account_id, params={}):
        """
        Source Code:
            Code: UsersController#api_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.api_index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/users

        
        Module: Users
        Function Description: List users in account

        Parameter Desc:
            search_term     | |string |The partial name or full ID of the users to match and return in the results list. Must be at least 3 characters.                                       Note that the API will prefer matching on canonical user ID if the ID has a numeric form. It will only search against other fields if non-numeric in form, or if the numeric value doesn’t yield any matches. Queries by administrative users will search on SIS ID, Integration ID, login ID, name, or email address
            enrollment_type | |string |When set, only return users enrolled with the specified course-level base role. This can be a base role type of ‘student’, ‘teacher’, ‘ta’, ‘observer’, or ‘designer’.
            sort            | |string |The column to sort results by.                                       Allowed values: username, email, sis_id, integration_id, last_login
            order           | |string |The order to sort the given column by.                                       Allowed values: asc, desc
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/users'
        return self.request(method, api, params)
        
    def activity_stream(self, params={}):
        """
        Source Code:
            Code: UsersController#activity_stream,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.activity_stream
        
        Scope:
            url:GET|/api/v1/users/self/activity_stream
            url:GET|/api/v1/users/activity_stream

        
        Module: Users
        Function Description: List the activity stream

        Parameter Desc:
            only_active_courses | |boolean |If true, will only return objects for courses the user is actively participating in
        """
        method = "GET"
        api = f'/api/v1/users/self/activity_stream'
        return self.request(method, api, params)
        
    def activity_stream_summary(self, params={}):
        """
        Source Code:
            Code: UsersController#activity_stream_summary,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.activity_stream_summary
        
        Scope:
            url:GET|/api/v1/users/self/activity_stream/summary

        
        Module: Users
        Function Description: Activity stream summary

        Parameter Desc:
            only_active_courses | |boolean |If true, will only return objects for courses the user is actively participating in

        Response Example: 
            [
              {
                "type": "DiscussionTopic",
                "unread_count": 2,
                "count": 7
              },
              {
                "type": "Conversation",
                "unread_count": 0,
                "count": 3
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/users/self/activity_stream/summary'
        return self.request(method, api, params)
        
    def todo_items(self, params={}):
        """
        Source Code:
            Code: UsersController#todo_items,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.todo_items
        
        Scope:
            url:GET|/api/v1/users/self/todo

        
        Module: Users
        Function Description: List the TODO items

        Parameter Desc:
            include[] | |string |`ungraded_quizzes`                                 Optionally include ungraded quizzes (such as practice quizzes and surveys) in the list. These will be returned under a quiz key instead of an assignment key in response elements.                                 Allowed values: ungraded_quizzes

        Response Example: 
            [
              {
                'type': 'grading',        // an assignment that needs grading
                'assignment': { .. assignment object .. },
                'ignore': '.. url ..',
                'ignore_permanently': '.. url ..',
                'html_url': '.. url ..',
                'needs_grading_count': 3, // number of submissions that need grading
                'context_type': 'course', // course|group
                'course_id': 1,
                'group_id': null,
              },
              {
                'type' => 'submitting',   // an assignment that needs submitting soon
                'assignment' => { .. assignment object .. },
                'ignore' => '.. url ..',
                'ignore_permanently' => '.. url ..',
                'html_url': '.. url ..',
                'context_type': 'course',
                'course_id': 1,
              },
              {
                'type' => 'submitting',   // a quiz that needs submitting soon
                'quiz' => { .. quiz object .. },
                'ignore' => '.. url ..',
                'ignore_permanently' => '.. url ..',
                'html_url': '.. url ..',
                'context_type': 'course',
                'course_id': 1,
              },
            ]
        """
        method = "GET"
        api = f'/api/v1/users/self/todo'
        return self.request(method, api, params)
        
    def todo_item_count(self, params={}):
        """
        Source Code:
            Code: UsersController#todo_item_count,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.todo_item_count
        
        Scope:
            url:GET|/api/v1/users/self/todo_item_count

        
        Module: Users
        Function Description: List counts for todo items

        Parameter Desc:
            include[] | |string |`ungraded_quizzes`                                 Optionally include ungraded quizzes (such as practice quizzes and surveys) in the list. These will be returned under a quiz key instead of an assignment key in response elements.                                 Allowed values: ungraded_quizzes

        Response Example: 
            {
              needs_grading_count: 32,
              assignments_needing_submitting: 10
            }
        """
        method = "GET"
        api = f'/api/v1/users/self/todo_item_count'
        return self.request(method, api, params)
        
    def upcoming_events(self, params={}):
        """
        Source Code:
            Code: UsersController#upcoming_events,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.upcoming_events
        
        Scope:
            url:GET|/api/v1/users/self/upcoming_events

        
        Module: Users
        Function Description: List upcoming assignments, calendar events


        Response Example: 
            [
              {
                "id"=>597,
                "title"=>"Upcoming Course Event",
                "description"=>"Attendance is correlated with passing!",
                "start_at"=>"2013-04-27T14:33:14Z",
                "end_at"=>"2013-04-27T14:33:14Z",
                "location_name"=>"Red brick house",
                "location_address"=>"110 Top of the Hill Dr.",
                "all_day"=>false,
                "all_day_date"=>nil,
                "created_at"=>"2013-04-26T14:33:14Z",
                "updated_at"=>"2013-04-26T14:33:14Z",
                "workflow_state"=>"active",
                "context_code"=>"course_12938",
                "child_events_count"=>0,
                "child_events"=>[],
                "parent_event_id"=>nil,
                "hidden"=>false,
                "url"=>"http://www.example.com/api/v1/calendar_events/597",
                "html_url"=>"http://www.example.com/calendar?event_id=597&include_contexts=course_12938"
              },
              {
                "id"=>"assignment_9729",
                "title"=>"Upcoming Assignment",
                "description"=>nil,
                "start_at"=>"2013-04-28T14:47:32Z",
                "end_at"=>"2013-04-28T14:47:32Z",
                "all_day"=>false,
                "all_day_date"=>"2013-04-28",
                "created_at"=>"2013-04-26T14:47:32Z",
                "updated_at"=>"2013-04-26T14:47:32Z",
                "workflow_state"=>"published",
                "context_code"=>"course_12942",
                "assignment"=>{
                  "id"=>9729,
                  "name"=>"Upcoming Assignment",
                  "description"=>nil,
                  "points_possible"=>10,
                  "due_at"=>"2013-04-28T14:47:32Z",
                  "assignment_group_id"=>2439,
                  "automatic_peer_reviews"=>false,
                  "grade_group_students_individually"=>nil,
                  "grading_standard_id"=>nil,
                  "grading_type"=>"points",
                  "group_category_id"=>nil,
                  "lock_at"=>nil,
                  "peer_reviews"=>false,
                  "position"=>1,
                  "unlock_at"=>nil,
                  "course_id"=>12942,
                  "submission_types"=>["none"],
                  "needs_grading_count"=>0,
                  "html_url"=>"http://www.example.com/courses/12942/assignments/9729"
                },
                "url"=>"http://www.example.com/api/v1/calendar_events/assignment_9729",
                "html_url"=>"http://www.example.com/courses/12942/assignments/9729"
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/users/self/upcoming_events'
        return self.request(method, api, params)
        
    def missing_submissions(self, user_id, params={}):
        """
        Source Code:
            Code: UsersController#missing_submissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.missing_submissions
        
        Scope:
            url:GET|/api/v1/users/:user_id/missing_submissions

        
        Module: Users
        Function Description: List Missing Submissions

        Parameter Desc:
            user_id          | |string |the student’s ID
            observed_user_id | |string |Return missing submissions for the given observed user. Must be accompanied by course_ids[]. The user making the request must be observing the observed user in all the courses specified by course_ids[].
            include[]        | |string |`planner_overrides`                                        Optionally include the assignment’s associated planner override, if it exists, for the current user. These will be returned under a planner_override key                                        `course`                                        Optionally include the assignments’ courses                                        Allowed values: planner_overrides, course
            filter[]         | |string |`submittable`                                        Only return assignments that the current user can submit (i.e. filter out locked assignments)                                        `current_grading_period`                                        Only return missing assignments that are in the current grading period                                        Allowed values: submittable, current_grading_period
            course_ids[]     | |string |Optionally restricts the list of past-due assignments to only those associated with the specified course IDs. Required if observed_user_id is passed.
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/missing_submissions'
        return self.request(method, api, params)
        
    def ignore_stream_item(self, id, params={}):
        """
        Source Code:
            Code: UsersController#ignore_stream_item,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.ignore_stream_item
        
        Scope:
            url:DELETE|/api/v1/users/self/activity_stream/:id

        
        Module: Users
        Function Description: Hide a stream item


        Request Example: 
            curl https://<canvas>/api/v1/users/self/activity_stream/<stream_item_id> \
               -X DELETE \
               -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "hidden": true
            }
        """
        method = "DELETE"
        api = f'/api/v1/users/self/activity_stream/{id}'
        return self.request(method, api, params)
        
    def ignore_all_stream_items(self, params={}):
        """
        Source Code:
            Code: UsersController#ignore_all_stream_items,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.ignore_all_stream_items
        
        Scope:
            url:DELETE|/api/v1/users/self/activity_stream

        
        Module: Users
        Function Description: Hide all stream items


        Request Example: 
            curl https://<canvas>/api/v1/users/self/activity_stream \
               -X DELETE \
               -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "hidden": true
            }
        """
        method = "DELETE"
        api = f'/api/v1/users/self/activity_stream'
        return self.request(method, api, params)
        
    def create_file(self, user_id, params={}):
        """
        Source Code:
            Code: UsersController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.create_file
        
        Scope:
            url:POST|/api/v1/users/:user_id/files

        
        Module: Users
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/users/{user_id}/files'
        return self.request(method, api, params)
        
    def api_show(self, id, params={}):
        """
        Source Code:
            Code: UsersController#api_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.api_show
        
        Scope:
            url:GET|/api/v1/users/:id

        
        Module: Users
        Function Description: Show user details

        Parameter Desc:
            include[] | |string |Array of additional information to include on the user record. `locale`, `avatar_url`, `permissions`, `email`, and `effective_locale` will always be returned                                 Allowed values: uuid, last_login
        """
        method = "GET"
        api = f'/api/v1/users/{id}'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: UsersController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/users

        
        Module: Users
        Function Description: Create a user

        Parameter Desc:
            user[name]                               |         |string  |The full name of the user. This name will be used by teacher for grading. Required if this is a self-registration.
            user[short_name]                         |         |string  |User’s name as it will be displayed in discussions, messages, and comments.
            user[sortable_name]                      |         |string  |User’s name as used to sort alphabetically in lists.
            user[time_zone]                          |         |string  |The time zone for the user. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            user[locale]                             |         |string  |The user’s preferred language, from the list of languages Canvas supports. This is in RFC-5646 format.
            user[terms_of_use]                       |         |boolean |Whether the user accepts the terms of use. Required if this is a self-registration and this canvas instance requires users to accept the terms (on by default).                                                                         If this is true, it will mark the user as having accepted the terms of use.
            user[skip_registration]                  |         |boolean |Automatically mark the user as registered.                                                                         If this is true, it is recommended to set "pseudonym[send_confirmation]" to true as well. Otherwise, the user will not receive any messages about their account creation.                                                                         The users communication channel confirmation can be skipped by setting "communication_channel[skip_confirmation]" to true as well.
            pseudonym[unique_id]                     |Required |string  |User’s login ID. If this is a self-registration, it must be a valid email address.
            pseudonym[password]                      |         |string  |User’s password. Cannot be set during self-registration.
            pseudonym[sis_user_id]                   |         |string  |SIS ID for the user’s account. To set this parameter, the caller must be able to manage SIS permissions.
            pseudonym[integration_id]                |         |string  |Integration ID for the login. To set this parameter, the caller must be able to manage SIS permissions. The Integration ID is a secondary identifier useful for more complex SIS integrations.
            pseudonym[send_confirmation]             |         |boolean |Send user notification of account creation if true. Automatically set to true during self-registration.
            pseudonym[force_self_registration]       |         |boolean |Send user a self-registration style email if true. Setting it means the users will get a notification asking them to `complete the registration process` by clicking it, setting a password, and letting them in.  Will only be executed on if the user does not need admin approval. Defaults to false unless explicitly provided.
            pseudonym[authentication_provider_id]    |         |string  |The authentication provider this login is associated with. Logins associated with a specific provider can only be used with that provider. Legacy providers (LDAP, CAS, SAML) will search for logins associated with them, or unassociated logins. New providers will only search for logins explicitly associated with them. This can be the integer ID of the provider, or the type of the provider (in which case, it will find the first matching provider).
            communication_channel[type]              |         |string  |The communication channel type, e.g. ‘email’ or ‘sms’.
            communication_channel[address]           |         |string  |The communication channel address, e.g. the user’s email address.
            communication_channel[confirmation_url]  |         |boolean |Only valid for account admins. If true, returns the new user account confirmation URL in the response.
            communication_channel[skip_confirmation] |         |boolean |Only valid for site admins and account admins making requests; If true, the channel is automatically validated and no confirmation email or SMS is sent. Otherwise, the user must respond to a confirmation message to confirm the channel.                                                                         If this is true, it is recommended to set "pseudonym[send_confirmation]" to true as well. Otherwise, the user will not receive any messages about their account creation.
            force_validations                        |         |boolean |If true, validations are performed on the newly created user (and their associated pseudonym) even if the request is made by a privileged user like an admin. When set to false, or not included in the request parameters, any newly created users are subject to validations unless the request is made by a user with a ‘manage_user_logins’ right. In which case, certain validations such as ‘require_acceptance_of_terms’ and ‘require_presence_of_name’ are not enforced. Use this parameter to return helpful json errors while building users with an admin request.
            enable_sis_reactivation                  |         |boolean |When true, will first try to re-activate a deleted user with matching sis_user_id if possible. This is commonly done with user and communication_channel so that the default communication_channel is also restored.
            destination                              |         |URL     |If you’re setting the password for the newly created user, you can provide this param with a valid URL pointing into this Canvas installation, and the response will include a destination field that’s a URL that you can redirect a browser to and have the newly created user automatically logged in. The URL is only valid for a short time, and must match the domain this request is directed to, and be for a well-formed path that Canvas can recognize.
            initial_enrollment_type                  |         |string  |‘observer` if doing a self-registration with a pairing code. This allows setting the password during user creation.
            pairing_code[code]                       |         |string  |If provided and valid, will link the new user as an observer to the student’s whose pairing code is given.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/users'
        return self.request(method, api, params)
        
    def create_self_registered_user(self, account_id, params={}):
        """
        Source Code:
            Code: UsersController#create_self_registered_user,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.create_self_registered_user
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/self_registration

        
        Module: Users
        Function Description: [DEPRECATED] Self register a user

        Parameter Desc:
            user[name]                     |Required |string  |The full name of the user. This name will be used by teacher for grading.
            user[short_name]               |         |string  |User’s name as it will be displayed in discussions, messages, and comments.
            user[sortable_name]            |         |string  |User’s name as used to sort alphabetically in lists.
            user[time_zone]                |         |string  |The time zone for the user. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            user[locale]                   |         |string  |The user’s preferred language, from the list of languages Canvas supports. This is in RFC-5646 format.
            user[terms_of_use]             |Required |boolean |Whether the user accepts the terms of use.
            pseudonym[unique_id]           |Required |string  |User’s login ID. Must be a valid email address.
            communication_channel[type]    |         |string  |The communication channel type, e.g. ‘email’ or ‘sms’.
            communication_channel[address] |         |string  |The communication channel address, e.g. the user’s email address.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/self_registration'
        return self.request(method, api, params)
        
    def settings(self, id, params={}):
        """
        Source Code:
            Code: UsersController#settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.settings
        
        Scope:
            url:GET|/api/v1/users/:id/settings
            url:PUT|/api/v1/users/:id/settings

        
        Module: Users
        Function Description: Update user settings.

        Parameter Desc:
            manual_mark_as_read                 | |boolean |If true, require user to manually mark discussion posts as read (don’t auto-mark as read).
            release_notes_badge_disabled        | |boolean |If true, hide the badge for new release notes.
            collapse_global_nav                 | |boolean |If true, the user’s page loads with the global navigation collapsed
            collapse_course_nav                 | |boolean |If true, the user’s course pages will load with the course navigation collapsed.
            hide_dashcard_color_overlays        | |boolean |If true, images on course cards will be presented without being tinted to match the course color.
            comment_library_suggestions_enabled | |boolean |If true, suggestions within the comment library will be shown.
            elementary_dashboard_disabled       | |boolean |If true, will display the user’s preferred class Canvas dashboard view instead of the canvas for elementary view.
        """
        method = "GET"
        api = f'/api/v1/users/{id}/settings'
        return self.request(method, api, params)
        
    def get_custom_colors(self, id, params={}):
        """
        Source Code:
            Code: UsersController#get_custom_colors,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.get_custom_colors
        
        Scope:
            url:GET|/api/v1/users/:id/colors

        
        Module: Users
        Function Description: Get custom colors


        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/colors/ \
              -X GET \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "custom_colors": {
                "course_42": "#abc123",
                "course_88": "#123abc"
              }
            }
        """
        method = "GET"
        api = f'/api/v1/users/{id}/colors'
        return self.request(method, api, params)
        
    def get_custom_color(self, id, asset_string, params={}):
        """
        Source Code:
            Code: UsersController#get_custom_color,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.get_custom_color
        
        Scope:
            url:GET|/api/v1/users/:id/colors/:asset_string

        
        Module: Users
        Function Description: Get custom color


        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/colors/<asset_string> \
              -X GET \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "hexcode": "#abc123"
            }
        """
        method = "GET"
        api = f'/api/v1/users/{id}/colors/{asset_string}'
        return self.request(method, api, params)
        
    def set_custom_color(self, id, asset_string, params={}):
        """
        Source Code:
            Code: UsersController#set_custom_color,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.set_custom_color
        
        Scope:
            url:PUT|/api/v1/users/:id/colors/:asset_string

        
        Module: Users
        Function Description: Update custom color

        Parameter Desc:
            hexcode | |string |The hexcode of the color to set for the context, if you choose to pass the hexcode as a query parameter rather than in the request body you should NOT include the ‘#’ unless you escape it first.

        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/colors/<asset_string> \
              -X PUT \
              -F 'hexcode=fffeee'
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "hexcode": "#abc123"
            }
        """
        method = "PUT"
        api = f'/api/v1/users/{id}/colors/{asset_string}'
        return self.request(method, api, params)
        
    def get_dashboard_positions(self, id, params={}):
        """
        Source Code:
            Code: UsersController#get_dashboard_positions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.get_dashboard_positions
        
        Scope:
            url:GET|/api/v1/users/:id/dashboard_positions

        
        Module: Users
        Function Description: Get dashboard positions


        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/dashboard_positions/ \
              -X GET \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "dashboard_positions": {
                "course_42": 2,
                "course_88": 1
              }
            }
        """
        method = "GET"
        api = f'/api/v1/users/{id}/dashboard_positions'
        return self.request(method, api, params)
        
    def set_dashboard_positions(self, id, params={}):
        """
        Source Code:
            Code: UsersController#set_dashboard_positions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.set_dashboard_positions
        
        Scope:
            url:PUT|/api/v1/users/:id/dashboard_positions

        
        Module: Users
        Function Description: Update dashboard positions


        Request Example: 
            curl 'https://<canvas>/api/v1/users/<user_id>/dashboard_positions/ \
              -X PUT \
              -F 'dashboard_positions[course_42]=1' \
              -F 'dashboard_positions[course_53]=2' \
              -F 'dashboard_positions[course_10]=3' \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "dashboard_positions": {
                "course_10": 3,
                "course_42": 1,
                "course_53": 2
              }
            }
        """
        method = "PUT"
        api = f'/api/v1/users/{id}/dashboard_positions'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: UsersController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.update
        
        Scope:
            url:PUT|/api/v1/users/:id

        
        Module: Users
        Function Description: Edit a user

        Parameter Desc:
            user[name]              | |string  |The full name of the user. This name will be used by teacher for grading.
            user[short_name]        | |string  |User’s name as it will be displayed in discussions, messages, and comments.
            user[sortable_name]     | |string  |User’s name as used to sort alphabetically in lists.
            user[time_zone]         | |string  |The time zone for the user. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            user[email]             | |string  |The default email address of the user.
            user[locale]            | |string  |The user’s preferred language, from the list of languages Canvas supports. This is in RFC-5646 format.
            user[avatar][token]     | |string  |A unique representation of the avatar record to assign as the user’s current avatar. This token can be obtained from the user avatars endpoint. This supersedes the user [avatar] [url] argument, and if both are included the url will be ignored. Note: this is an internal representation and is subject to change without notice. It should be consumed with this api endpoint and used in the user update endpoint, and should not be constructed by the client.
            user[avatar][url]       | |string  |To set the user’s avatar to point to an external url, do not include a token and instead pass the url here. Warning: For maximum compatibility, please use 128 px square images.
            user[avatar][state]     | |string  |To set the state of user’s avatar. Only valid for account administrator.                                                Allowed values: none, submitted, approved, locked, reported, re_reported
            user[title]             | |string  |Sets a title on the user profile. (See Get user profile.) Profiles must be enabled on the root account.
            user[bio]               | |string  |Sets a bio on the user profile. (See Get user profile.) Profiles must be enabled on the root account.
            user[pronouns]          | |string  |Sets pronouns on the user profile. Passing an empty string will empty the user’s pronouns Only Available Pronouns set on the root account are allowed Adding and changing pronouns must be enabled on the root account.
            user[event]             | |string  |Suspends or unsuspends all logins for this user that the calling user has permission to                                                Allowed values: suspend, unsuspend
            override_sis_stickiness | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "PUT"
        api = f'/api/v1/users/{id}'
        return self.request(method, api, params)
        
    def terminate_sessions(self, id, params={}):
        """
        Source Code:
            Code: UsersController#terminate_sessions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.terminate_sessions
        
        Scope:
            url:DELETE|/api/v1/users/:id/sessions

        
        Module: Users
        Function Description: Terminate all user sessions

        """
        method = "DELETE"
        api = f'/api/v1/users/{id}/sessions'
        return self.request(method, api, params)
        
    def merge_into(self, id, destination_user_id, params={}):
        """
        Source Code:
            Code: UsersController#merge_into,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.merge_into
        
        Scope:
            url:PUT|/api/v1/users/:id/merge_into/:destination_user_id
            url:PUT|/api/v1/users/:id/merge_into/accounts/:destination_account_id/users/:destination_user_id

        
        Module: Users
        Function Description: Merge user into another user

        """
        method = "PUT"
        api = f'/api/v1/users/{id}/merge_into/{destination_user_id}'
        return self.request(method, api, params)
        
    def split(self, id, params={}):
        """
        Source Code:
            Code: UsersController#split,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.split
        
        Scope:
            url:POST|/api/v1/users/:id/split

        
        Module: Users
        Function Description: Split merged users into separate users

        """
        method = "POST"
        api = f'/api/v1/users/{id}/split'
        return self.request(method, api, params)
        
    def pandata_events_token(self, params={}):
        """
        Source Code:
            Code: UsersController#pandata_events_token,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.pandata_events_token
        
        Scope:
            url:POST|/api/v1/users/self/pandata_events_token

        
        Module: Users
        Function Description: Get a Pandata Events jwt token and its expiration date

        Parameter Desc:
            app_key | |string |The pandata events appKey for this mobile app

        Request Example: 
            curl https://<canvas>/api/v1/users/self/pandata_events_token \
                 -X POST \
                 -H 'Authorization: Bearer <token>'
                 -F 'app_key=MOBILE_APPS_KEY' \

        Response Example: 
            {
              "url": "https://example.com/pandata/events"
              "auth_token": "wek23klsdnsoieioeoi3of9deeo8r8eo8fdn",
              "props_token": "paowinefopwienpfiownepfiownepfownef",
              "expires_at": 1521667783000,
            }
        """
        method = "POST"
        api = f'/api/v1/users/self/pandata_events_token'
        return self.request(method, api, params)
        
    def user_graded_submissions(self, id, params={}):
        """
        Source Code:
            Code: UsersController#user_graded_submissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/users_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.users.user_graded_submissions
        
        Scope:
            url:GET|/api/v1/users/:id/graded_submissions

        
        Module: Users
        Function Description: Get a users most recently graded submissions

        """
        method = "GET"
        api = f'/api/v1/users/{id}/graded_submissions'
        return self.request(method, api, params)
        
    def settings(self, user_id, params={}):
        """
        Source Code:
            Code: ProfileController#settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/profile_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.profile.settings
        
        Scope:
            url:GET|/api/v1/users/:user_id/profile

        
        Module: Users
        Function Description: Get user profile

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/profile'
        return self.request(method, api, params)
        
    def profile_pics(self, user_id, params={}):
        """
        Source Code:
            Code: ProfileController#profile_pics,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/profile_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.profile.profile_pics
        
        Scope:
            url:GET|/api/v1/users/:user_id/avatars

        
        Module: Users
        Function Description: List avatar options


        Request Example: 
            curl 'https://<canvas>/api/v1/users/1/avatars.json' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            [
              {
                "type":"gravatar",
                "url":"https://secure.gravatar.com/avatar/2284...",
                "token":<opaque_token>,
                "display_name":"gravatar pic"
              },
              {
                "type":"attachment",
                "url":<url to fetch thumbnail of attachment>,
                "token":<opaque_token>,
                "display_name":"profile.jpg",
                "id":12,
                "content-type":"image/jpeg",
                "filename":"profile.jpg",
                "size":32649
              },
              {
                "type":"no_pic",
                "url":"https://<canvas>/images/dotted_pic.png",
                "token":<opaque_token>,
                "display_name":"no pic"
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/avatars'
        return self.request(method, api, params)
        
    def index(self, user_id, params={}):
        """
        Source Code:
            Code: PageViewsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/page_views_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.page_views.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/page_views

        
        Module: Users
        Function Description: List user page views

        Parameter Desc:
            start_time | |DateTime |The beginning of the time range from which you want page views.
            end_time   | |DateTime |The end of the time range from which you want page views.
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/page_views'
        return self.request(method, api, params)
        