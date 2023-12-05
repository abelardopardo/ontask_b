from .etc.conf import *
from .res import *

class Accounts(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: AccountsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.index
        
        Scope:
            url:GET|/api/v1/accounts

        
        Module: Accounts
        Function Description: List accounts

        Parameter Desc:
            include[] | |string |Array of additional information to include.                                 `lti_guid`                                 the ‘tool_consumer_instance_guid’ that will be sent for this account on LTI launches                                 `registration_settings`                                 returns info about the privacy policy and terms of use                                 `services`                                 returns services and whether they are enabled (requires account management permissions)                                 Allowed values: lti_guid, registration_settings, services
        """
        method = "GET"
        api = f'/api/v1/accounts'
        return self.request(method, api, params)
        
    def manageable_accounts(self, params={}):
        """
        Source Code:
            Code: AccountsController#manageable_accounts,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.manageable_accounts
        
        Scope:
            url:GET|/api/v1/manageable_accounts

        
        Module: Accounts
        Function Description: Get accounts that admins can manage

        """
        method = "GET"
        api = f'/api/v1/manageable_accounts'
        return self.request(method, api, params)
        
    def course_accounts(self, params={}):
        """
        Source Code:
            Code: AccountsController#course_accounts,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.course_accounts
        
        Scope:
            url:GET|/api/v1/course_accounts

        
        Module: Accounts
        Function Description: List accounts for course admins

        """
        method = "GET"
        api = f'/api/v1/course_accounts'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: AccountsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.show
        
        Scope:
            url:GET|/api/v1/accounts/:id

        
        Module: Accounts
        Function Description: Get a single account

        """
        method = "GET"
        api = f'/api/v1/accounts/{id}'
        return self.request(method, api, params)
        
    def show_settings(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#show_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.show_settings
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/settings

        
        Module: Accounts
        Function Description: Settings


        Request Example: 
            curl https://<canvas>/api/v1/accounts/<account_id>/settings \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {"microsoft_sync_enabled": true, "microsoft_sync_login_attribute_suffix": false}
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/settings'
        return self.request(method, api, params)
        
    def permissions(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#permissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.permissions
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/permissions

        
        Module: Accounts
        Function Description: Permissions

        Parameter Desc:
            permissions[] | |string |List of permissions to check against the authenticated user. Permission names are documented in the Create a role endpoint.

        Request Example: 
            curl https://<canvas>/api/v1/accounts/self/permissions \
              -H 'Authorization: Bearer <token>' \
              -d 'permissions[]=manage_account_memberships' \
              -d 'permissions[]=become_user'

        Response Example: 
            {'manage_account_memberships': 'false', 'become_user': 'true'}
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/permissions'
        return self.request(method, api, params)
        
    def sub_accounts(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#sub_accounts,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.sub_accounts
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sub_accounts

        
        Module: Accounts
        Function Description: Get the sub-accounts of an account

        Parameter Desc:
            recursive | |boolean |If true, the entire account tree underneath this account will be returned (though still paginated). If false, only direct sub-accounts of this account will be returned. Defaults to false.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sub_accounts'
        return self.request(method, api, params)
        
    def terms_of_service(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#terms_of_service,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.terms_of_service
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/terms_of_service

        
        Module: Accounts
        Function Description: Get the Terms of Service

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/terms_of_service'
        return self.request(method, api, params)
        
    def help_links(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#help_links,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.help_links
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/help_links

        
        Module: Accounts
        Function Description: Get help links

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/help_links'
        return self.request(method, api, params)
        
    def manually_created_courses_account(self, params={}):
        """
        Source Code:
            Code: AccountsController#manually_created_courses_account,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.manually_created_courses_account
        
        Scope:
            url:GET|/api/v1/manually_created_courses_account

        
        Module: Accounts
        Function Description: Get the manually-created courses sub-account for the domain root account

        """
        method = "GET"
        api = f'/api/v1/manually_created_courses_account'
        return self.request(method, api, params)
        
    def courses_api(self, account_id, params={}):
        """
        Source Code:
            Code: AccountsController#courses_api,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.courses_api
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/courses

        
        Module: Accounts
        Function Description: List active courses in an account

        Parameter Desc:
            with_enrollments            | |boolean |If true, include only courses with at least one enrollment.  If false, include only courses with no enrollments.  If not present, do not filter on course enrollment status.
            enrollment_type[]           | |string  |If set, only return courses that have at least one user enrolled in in the course with one of the specified enrollment types.                                                    Allowed values: teacher, student, ta, observer, designer
            published                   | |boolean |If true, include only published courses.  If false, exclude published courses.  If not present, do not filter on published status.
            completed                   | |boolean |If true, include only completed courses (these may be in state ‘completed’, or their enrollment term may have ended).  If false, exclude completed courses.  If not present, do not filter on completed status.
            blueprint                   | |boolean |If true, include only blueprint courses. If false, exclude them. If not present, do not filter on this basis.
            blueprint_associated        | |boolean |If true, include only courses that inherit content from a blueprint course. If false, exclude them. If not present, do not filter on this basis.
            public                      | |boolean |If true, include only public courses. If false, exclude them. If not present, do not filter on this basis.
            by_teachers[]               | |integer |List of User IDs of teachers; if supplied, include only courses taught by one of the referenced users.
            by_subaccounts[]            | |integer |List of Account IDs; if supplied, include only courses associated with one of the referenced subaccounts.
            hide_enrollmentless_courses | |boolean |If present, only return courses that have at least one enrollment. Equivalent to ‘with_enrollments=true’; retained for compatibility.
            state[]                     | |string  |If set, only return courses that are in the given state(s). By default, all states but `deleted` are returned.                                                    Allowed values: created, claimed, available, completed, deleted, all
            enrollment_term_id          | |integer |If set, only includes courses from the specified term.
            search_term                 | |string  |The partial course name, code, or full ID to match and return in the results list. Must be at least 3 characters.
            include[]                   | |string  |All explanations can be seen in the Course API index documentation                                                    `sections`, `needs_grading_count` and `total_scores` are not valid options at the account level                                                    Allowed values: syllabus_body, term, course_progress, storage_quota_used_mb, total_students, teachers, account_name, concluded
            sort                        | |string  |The column to sort results by.                                                    Allowed values: course_name, sis_course_id, teacher, account_name
            order                       | |string  |The order to sort the given column by.                                                    Allowed values: asc, desc
            search_by                   | |string  |The filter to search by. `course` searches for course names, course codes, and SIS IDs. `teacher` searches for teacher names                                                    Allowed values: course, teacher
            starts_before               | |Date    |If set, only return courses that start before the value (inclusive) or their enrollment term starts before the value (inclusive) or both the course’s start_at and the enrollment term’s start_at are set to null. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            ends_after                  | |Date    |If set, only return courses that end after the value (inclusive) or their enrollment term ends after the value (inclusive) or both the course’s end_at and the enrollment term’s end_at are set to null. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            homeroom                    | |boolean |If set, only return homeroom courses.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/courses'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: AccountsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.update
        
        Scope:
            url:PUT|/api/v1/accounts/:id

        
        Module: Accounts
        Function Description: Update an account

        Parameter Desc:
            account[name]                                              | |string  |Updates the account name
            account[sis_account_id]                                    | |string  |Updates the account sis_account_id Must have manage_sis permission and must not be a root_account.
            account[default_time_zone]                                 | |string  |The default time zone of the account. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            account[default_storage_quota_mb]                          | |integer |The default course storage quota to be used, if not otherwise specified.
            account[default_user_storage_quota_mb]                     | |integer |The default user storage quota to be used, if not otherwise specified.
            account[default_group_storage_quota_mb]                    | |integer |The default group storage quota to be used, if not otherwise specified.
            account[course_template_id]                                | |integer |The ID of a course to be used as a template for all newly created courses. Empty means to inherit the setting from parent account, 0 means to not use a template even if a parent account has one set. The course must be marked as a template.
            account[settings][restrict_student_past_view][value]       | |boolean |Restrict students from viewing courses after end date
            account[settings][restrict_student_past_view][locked]      | |boolean |Lock this setting for sub-accounts and courses
            account[settings][restrict_student_future_view][value]     | |boolean |Restrict students from viewing courses before start date
            account[settings][microsoft_sync_enabled]                  | |boolean |Determines whether this account has Microsoft Teams Sync enabled or not.                                                                                   Note that if you are altering Microsoft Teams sync settings you must enable the Microsoft Group enrollment syncing feature flag. In addition, if you are enabling Microsoft Teams sync, you must also specify a tenant, login attribute, and a remote attribute. Specifying a suffix to use is optional.
            account[settings][microsoft_sync_tenant]                   | |string  |The tenant this account should use when using Microsoft Teams Sync. This should be an Azure Active Directory domain name.
            account[settings][microsoft_sync_login_attribute]          | |string  |The attribute this account should use to lookup users when using Microsoft Teams Sync. Must be one of `sub`, `email`, `oid`, `preferred_username`, or `integration_id`.
            account[settings][microsoft_sync_login_attribute_suffix]   | |string  |A suffix that will be appended to the result of the login attribute when associating Canvas users with Microsoft users. Must be under 255 characters and contain no whitespace. This field is optional.
            account[settings][microsoft_sync_remote_attribute]         | |string  |The Active Directory attribute to use when associating Canvas users with Microsoft users. Must be one of `mail`, `mailNickname`, or `userPrincipalName`.
            account[settings][restrict_student_future_view][locked]    | |boolean |Lock this setting for sub-accounts and courses
            account[settings][lock_all_announcements][value]           | |boolean |Disable comments on announcements
            account[settings][lock_all_announcements][locked]          | |boolean |Lock this setting for sub-accounts and courses
            account[settings][usage_rights_required][value]            | |boolean |Copyright and license information must be provided for files before they are published.
            account[settings][usage_rights_required][locked]           | |boolean |Lock this setting for sub-accounts and courses
            account[settings][restrict_student_future_listing][value]  | |boolean |Restrict students from viewing future enrollments in course list
            account[settings][restrict_student_future_listing][locked] | |boolean |Lock this setting for sub-accounts and courses
            account[settings][conditional_release][value]              | |boolean |Enable or disable individual learning paths for students based on assessment
            account[settings][conditional_release][locked]             | |boolean |Lock this setting for sub-accounts and courses
            override_sis_stickiness                                    | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
            account[settings][lock_outcome_proficiency][value]         | |boolean |DEPRECATED                                                                                   Restrict instructors from changing mastery scale
            account[lock_outcome_proficiency][locked]                  | |boolean |DEPRECATED                                                                                   Lock this setting for sub-accounts and courses
            account[settings][lock_proficiency_calculation][value]     | |boolean |DEPRECATED                                                                                   Restrict instructors from changing proficiency calculation method
            account[lock_proficiency_calculation][locked]              | |boolean |DEPRECATED                                                                                   Lock this setting for sub-accounts and courses
            account[services]                                          | |Hash    |Give this a set of keys and boolean values to enable or disable services matching the keys
        """
        method = "PUT"
        api = f'/api/v1/accounts/{id}'
        return self.request(method, api, params)
        
    def remove_user(self, account_id, user_id, params={}):
        """
        Source Code:
            Code: AccountsController#remove_user,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/accounts_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.accounts.remove_user
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/users/:user_id

        
        Module: Accounts
        Function Description: Delete a user from the root account

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/users/{user_id}'
        return self.request(method, api, params)
        