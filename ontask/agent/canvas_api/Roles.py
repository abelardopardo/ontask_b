from .etc.conf import *
from .res import *

class Roles(Res):
    def api_index(self, account_id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#api_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.api_index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/roles

        
        Module: Roles
        Function Description: List roles

        Parameter Desc:
            account_id     |Required |string  |The id of the account to retrieve roles for.
            state[]        |         |string  |Filter by role state. If this argument is omitted, only ‘active’ roles are returned.                                               Allowed values: active, inactive
            show_inherited |         |boolean |If this argument is true, all roles inherited from parent accounts will be included.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/roles'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/roles/:id

        
        Module: Roles
        Function Description: Get a single role

        Parameter Desc:
            account_id |Required |string  |The id of the account containing the role
            role_id    |Required |integer |The unique identifier for the role
            role       |         |string  |The name for the role
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/roles/{id}'
        return self.request(method, api, params)
        
    def add_role(self, account_id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#add_role,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.add_role
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/roles

        
        Module: Roles
        Function Description: Create a new role

        Parameter Desc:
            label                                    |Required |string  |Label for the role.
            role                                     |         |string  |Deprecated alias for label.
            base_role_type                           |         |string  |Specifies the role type that will be used as a base for the permissions granted to this role.                                                                         Defaults to ‘AccountMembership’ if absent                                                                         Allowed values: AccountMembership, StudentEnrollment, TeacherEnrollment, TaEnrollment, ObserverEnrollment, DesignerEnrollment
            permissions[<X>][explicit]               |         |boolean |no description
            permissions[<X>][enabled]                |         |boolean |If explicit is 1 and enabled is 1, permission <X> will be explicitly granted to this role. If explicit is 1 and enabled has any other value (typically 0), permission <X> will be explicitly denied to this role. If explicit is any other value (typically 0) or absent, or if enabled is absent, the value for permission <X> will be inherited from upstream. Ignored if permission <X> is locked upstream (in an ancestor account).                                                                         May occur multiple times with unique values for <X>. Recognized permission names for <X> are:                                                                         [For Account-Level Roles Only]                                                                         become_user                      -- Users - act as                                                                         import_sis                       -- SIS Data - import                                                                         manage_account_memberships       -- Admins - add / remove                                                                         manage_account_settings          -- Account-level settings - manage                                                                         manage_alerts                    -- Global announcements - add / edit / delete                                                                         manage_catalog                   -- Catalog - manage                                                                         Manage Course Templates granular permissions                                                                             add_course_template          -- Course Templates - add                                                                             delete_course_template       -- Course Templates - delete                                                                             edit_course_template         -- Course Templates - edit                                                                         manage_courses_add               -- Courses - add                                                                         manage_courses_admin             -- Courses - manage / update                                                                         manage_developer_keys            -- Developer keys - manage                                                                         manage_feature_flags             -- Feature Options - enable / disable                                                                         manage_master_courses            -- Blueprint Courses - add / edit / associate / delete                                                                         manage_role_overrides            -- Permissions - manage                                                                         manage_storage_quotas            -- Storage Quotas - manage                                                                         manage_sis                       -- SIS data - manage                                                                         manage_user_logins               -- Users - manage login details                                                                         manage_user_observers            -- Users - manage observers                                                                         moderate_user_content            -- Users - moderate content                                                                         read_course_content              -- Course Content - view                                                                         read_course_list                 -- Courses - view list                                                                         view_course_changes              -- Courses - view change logs                                                                         view_feature_flags               -- Feature Options - view                                                                         view_grade_changes               -- Grades - view change logs                                                                         view_notifications               -- Notifications - view                                                                         view_quiz_answer_audits          -- Quizzes - view submission log                                                                         view_statistics                  -- Statistics - view                                                                         undelete_courses                 -- Courses - undelete                                                                         [For both Account-Level and Course-Level roles]                                                                          Note: Applicable enrollment types for course-level roles are given in brackets:                                                                                S = student, T = teacher (instructor), A = TA, D = designer, O = observer.                                                                                Lower-case letters indicate permissions that are off by default.                                                                                A missing letter indicates the permission cannot be enabled for the role                                                                                or any derived custom roles.                                                                         allow_course_admin_actions       -- [ Tad ] Users - allow administrative actions in courses                                                                         create_collaborations            -- [STADo] Student Collaborations - create                                                                         create_conferences               -- [STADo] Web conferences - create                                                                         create_forum                     -- [STADo] Discussions - create                                                                         generate_observer_pairing_code   -- [ tado] Users - Generate observer pairing codes for students                                                                         import_outcomes                  -- [ TaDo] Learning Outcomes - import                                                                         lti_add_edit                     -- [ TAD ] LTI - add / edit / delete                                                                         manage_account_banks             -- [ td  ] Item Banks - manage account                                                                         manage_assignments               -- [ TADo] Assignments and Quizzes - add / edit / delete (deprecated)                                                                         Manage Assignments and Quizzes granular permissions                                                                             manage_assignments_add       -- [ TADo] Assignments and Quizzes - add                                                                             manage_assignments_edit      -- [ TADo] Assignments and Quizzes - edit / manage                                                                             manage_assignments_delete    -- [ TADo] Assignments and Quizzes - delete                                                                         manage_calendar                  -- [sTADo] Course Calendar - add / edit / delete                                                                         manage_content                   -- [ TADo] Course Content - add / edit / delete                                                                         manage_course_visibility         -- [ TAD ] Course - change visibility                                                                         Manage Courses granular permissions                                                                             manage_courses_conclude      -- [ TaD ] Courses - conclude                                                                             manage_courses_delete        -- [ TaD ] Courses - delete                                                                             manage_courses_publish       -- [ TaD ] Courses - publish                                                                             manage_courses_reset         -- [ TaD ] Courses - reset                                                                         Manage Files granular permissions                                                                             manage_files_add             -- [ TADo] Course Files - add                                                                             manage_files_edit            -- [ TADo] Course Files - edit                                                                             manage_files_delete          -- [ TADo] Course Files - delete                                                                         manage_grades                    -- [ TA  ] Grades - edit                                                                         Manage Groups granular permissions                                                                             manage_groups_add            -- [ TAD ] Groups - add                                                                             manage_groups_delete         -- [ TAD ] Groups - delete                                                                             manage_groups_manage         -- [ TAD ] Groups - manage                                                                         manage_interaction_alerts        -- [ Ta  ] Alerts - add / edit / delete                                                                         manage_outcomes                  -- [sTaDo] Learning Outcomes - add / edit / delete                                                                         manage_proficiency_calculations  -- [ t d ] Outcome Proficiency Calculations - add / edit / delete                                                                         manage_proficiency_scales        -- [ t d ] Outcome Proficiency/Mastery Scales - add / edit / delete                                                                         Manage Sections granular permissions                                                                             manage_sections_add          -- [ TaD ] Course Sections - add                                                                             manage_sections_edit         -- [ TaD ] Course Sections - edit                                                                             manage_sections_delete       -- [ TaD ] Course Sections - delete                                                                         manage_students                  -- [ TAD ] Users - manage students in courses                                                                         manage_user_notes                -- [ TA  ] Faculty Journal - manage entries                                                                         manage_rubrics                   -- [ TAD ] Rubrics - add / edit / delete                                                                         Manage Pages granular permissions                                                                             manage_wiki_create           -- [ TADo] Pages - create                                                                             manage_wiki_delete           -- [ TADo] Pages - delete                                                                             manage_wiki_update           -- [ TADo] Pages - update                                                                         moderate_forum                   -- [sTADo] Discussions - moderate                                                                         post_to_forum                    -- [STADo] Discussions - post                                                                         read_announcements               -- [STADO] Announcements - view                                                                         read_email_addresses             -- [sTAdo] Users - view primary email address                                                                         read_forum                       -- [STADO] Discussions - view                                                                         read_question_banks              -- [ TADo] Question banks - view and link                                                                         read_reports                     -- [ TAD ] Reports - manage                                                                         read_roster                      -- [STADo] Users - view list                                                                         read_sis                         -- [sTa  ] SIS Data - read                                                                         select_final_grade               -- [ TA  ] Grades - select final grade for moderation                                                                         send_messages                    -- [STADo] Conversations - send messages to individual course members                                                                         send_messages_all                -- [sTADo] Conversations - send messages to entire class                                                                         Users - Teacher granular permissions                                                                             add_teacher_to_course        -- [ Tad ] Add a teacher enrollment to a course                                                                             remove_teacher_from_course   -- [ Tad ] Remove a Teacher enrollment from a course                                                                         Users - TA granular permissions                                                                             add_ta_to_course             -- [ Tad ] Add a TA enrollment to a course                                                                             remove_ta_from_course        -- [ Tad ] Remove a TA enrollment from a course                                                                         Users - Designer granular permissions                                                                             add_designer_to_course       -- [ Tad ] Add a designer enrollment to a course                                                                             remove_designer_from_course  -- [ Tad ] Remove a designer enrollment from a course                                                                         Users - Observer granular permissions                                                                             add_observer_to_course       -- [ Tad ] Add an observer enrollment to a course                                                                             remove_observer_from_course  -- [ Tad ] Remove an observer enrollment from a course                                                                         Users - Student granular permissions                                                                             add_student_to_course        -- [ Tad ] Add a student enrollment to a course                                                                             remove_student_from_course   -- [ Tad ] Remove a student enrollment from a course                                                                         view_all_grades                  -- [ TAd ] Grades - view all grades                                                                         view_analytics                   -- [sTA  ] Analytics - view pages                                                                         view_audit_trail                 -- [ t   ] Grades - view audit trail                                                                         view_group_pages                 -- [sTADo] Groups - view all student groups                                                                         view_user_logins                 -- [ TA  ] Users - view login IDs                                                                         Some of these permissions are applicable only for roles on the site admin account, on a root account, or for course-level roles with a particular base role type; if a specified permission is inapplicable, it will be ignored.                                                                         Additional permissions may exist based on installed plugins.                                                                         A comprehensive list of all permissions are available:                                                                         Course Permissions PDF: bit.ly/cnvs-course-permissions                                                                         Account Permissions PDF: bit.ly/cnvs-acct-permissions
            permissions[<X>][locked]                 |         |boolean |If the value is 1, permission <X> will be locked downstream (new roles in subaccounts cannot override the setting). For any other value, permission <X> is left unlocked. Ignored if permission <X> is already locked upstream. May occur multiple times with unique values for <X>.
            permissions[<X>][applies_to_self]        |         |boolean |If the value is 1, permission <X> applies to the account this role is in. The default value is 1. Must be true if applies_to_descendants is false. This value is only returned if enabled is true.
            permissions[<X>][applies_to_descendants] |         |boolean |If the value is 1, permission <X> cascades down to sub accounts of the account this role is in. The default value is 1.  Must be true if applies_to_self is false.This value is only returned if enabled is true.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/roles'
        return self.request(method, api, params)
        
    def remove_role(self, account_id, id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#remove_role,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.remove_role
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/roles/:id

        
        Module: Roles
        Function Description: Deactivate a role

        Parameter Desc:
            role_id |Required |integer |The unique identifier for the role
            role    |         |string  |The name for the role
        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/roles/{id}'
        return self.request(method, api, params)
        
    def activate_role(self, account_id, id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#activate_role,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.activate_role
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/roles/:id/activate

        
        Module: Roles
        Function Description: Activate a role

        Parameter Desc:
            role_id |Required |integer    |The unique identifier for the role
            role    |         |Deprecated |The name for the role
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/roles/{id}/activate'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: RoleOverridesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/role_overrides_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.role_overrides.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/roles/:id

        
        Module: Roles
        Function Description: Update a role

        Parameter Desc:
            label                                    | |string  |The label for the role. Can only change the label of a custom role that belongs directly to the account.
            permissions[<X>][explicit]               | |boolean |no description
            permissions[<X>][enabled]                | |boolean |These arguments are described in the documentation for the add_role method.
            permissions[<X>][applies_to_self]        | |boolean |If the value is 1, permission <X> applies to the account this role is in. The default value is 1. Must be true if applies_to_descendants is false. This value is only returned if enabled is true.
            permissions[<X>][applies_to_descendants] | |boolean |If the value is 1, permission <X> cascades down to sub accounts of the account this role is in. The default value is 1.  Must be true if applies_to_self is false.This value is only returned if enabled is true.
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/roles/{id}'
        return self.request(method, api, params)
        