from .etc.conf import *
from .res import *

class Courses(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: CoursesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.index
        
        Scope:
            url:GET|/api/v1/courses

        
        Module: Courses
        Function Description: List your courses

        Parameter Desc:
            enrollment_type           | |string  |When set, only return courses where the user is enrolled as this type. For example, set to `teacher` to return only courses where the user is enrolled as a Teacher.  This argument is ignored if enrollment_role is given.                                                  Allowed values: teacher, student, ta, observer, designer
            enrollment_role           | |string  |Deprecated When set, only return courses where the user is enrolled with the specified course-level role.  This can be a role created with the Add Role API or a base role type of ‘StudentEnrollment’, ‘TeacherEnrollment’, ‘TaEnrollment’, ‘ObserverEnrollment’, or ‘DesignerEnrollment’.
            enrollment_role_id        | |integer |When set, only return courses where the user is enrolled with the specified course-level role.  This can be a role created with the Add Role API or a built_in role type of ‘StudentEnrollment’, ‘TeacherEnrollment’, ‘TaEnrollment’, ‘ObserverEnrollment’, or ‘DesignerEnrollment’.
            enrollment_state          | |string  |When set, only return courses where the user has an enrollment with the given state. This will respect section/course/term date overrides.                                                  Allowed values: active, invited_or_pending, completed
            exclude_blueprint_courses | |boolean |When set, only return courses that are not configured as blueprint courses.
            include[]                 | |string  |`needs_grading_count`: Optional information to include with each Course. When needs_grading_count is given, and the current user has grading rights, the total number of submissions needing grading for all assignments is returned.                                                  `syllabus_body`: Optional information to include with each Course. When syllabus_body is given the user-generated html for the course syllabus is returned.                                                  `public_description`: Optional information to include with each Course. When public_description is given the user-generated text for the course public description is returned.                                                  `total_scores`: Optional information to include with each Course. When total_scores is given, any student enrollments will also include the fields ‘computed_current_score’, ‘computed_final_score’, ‘computed_current_grade’, and ‘computed_final_grade’, as well as (if the user has permission) ‘unposted_current_score’, ‘unposted_final_score’, ‘unposted_current_grade’, and ‘unposted_final_grade’ (see Enrollment documentation for more information on these fields). This argument is ignored if the course is configured to hide final grades.                                                  `current_grading_period_scores`: Optional information to include with each Course. When current_grading_period_scores is given and total_scores is given, any student enrollments will also include the fields ‘has_grading_periods’, ‘totals_for_all_grading_periods_option’, ‘current_grading_period_title’, ‘current_grading_period_id’, current_period_computed_current_score’, ‘current_period_computed_final_score’, ‘current_period_computed_current_grade’, and ‘current_period_computed_final_grade’, as well as (if the user has permission) ‘current_period_unposted_current_score’, ‘current_period_unposted_final_score’, ‘current_period_unposted_current_grade’, and ‘current_period_unposted_final_grade’ (see Enrollment documentation for more information on these fields). In addition, when this argument is passed, the course will have a ‘has_grading_periods’ attribute on it. This argument is ignored if the total_scores argument is not included. If the course is configured to hide final grades, the following fields are not returned: ‘totals_for_all_grading_periods_option’, ‘current_period_computed_current_score’, ‘current_period_computed_final_score’, ‘current_period_computed_current_grade’, ‘current_period_computed_final_grade’, ‘current_period_unposted_current_score’, ‘current_period_unposted_final_score’, ‘current_period_unposted_current_grade’, and ‘current_period_unposted_final_grade’                                                  `grading_periods`: Optional information to include with each Course. When grading_periods is given, a list of the grading periods associated with each course is returned.                                                  `term`: Optional information to include with each Course. When term is given, the information for the enrollment term for each course is returned.                                                  `account`: Optional information to include with each Course. When account is given, the account json for each course is returned.                                                  `course_progress`: Optional information to include with each Course. When course_progress is given, each course will include a ‘course_progress’ object with the fields: ‘requirement_count’, an integer specifying the total number of requirements in the course, ‘requirement_completed_count’, an integer specifying the total number of requirements in this course that have been completed, and ‘next_requirement_url’, a string url to the next requirement item, and ‘completed_at’, the date the course was completed (null if incomplete). ‘next_requirement_url’ will be null if all requirements have been completed or the current module does not require sequential progress. `course_progress` will return an error message if the course is not module based or the user is not enrolled as a student in the course.                                                  `sections`: Section enrollment information to include with each Course. Returns an array of hashes containing the section ID (id), section name (name), start and end dates (start_at, end_at), as well as the enrollment type (enrollment_role, e.g. ‘StudentEnrollment’).                                                  `storage_quota_used_mb`: The amount of storage space used by the files in this course                                                  `total_students`: Optional information to include with each Course. Returns an integer for the total amount of active and invited students.                                                  `passback_status`: Include the grade passback_status                                                  `favorites`: Optional information to include with each Course. Indicates if the user has marked the course as a favorite course.                                                  `teachers`: Teacher information to include with each Course. Returns an array of hashes containing the UserDisplay information for each teacher in the course.                                                  `observed_users`: Optional information to include with each Course. Will include data for observed users if the current user has an observer enrollment.                                                  `tabs`: Optional information to include with each Course. Will include the list of tabs configured for each course.  See the List available tabs API for more information.                                                  `course_image`: Optional information to include with each Course. Returns course image url if a course image has been set.                                                  `banner_image`: Optional information to include with each Course. Returns course banner image url if the course is a Canvas for Elementary subject and a banner image has been set.                                                  `concluded`: Optional information to include with each Course. Indicates whether the course has been concluded, taking course and term dates into account.                                                  Allowed values: needs_grading_count, syllabus_body, public_description, total_scores, current_grading_period_scores, grading_periods, term, account, course_progress, sections, storage_quota_used_mb, total_students, passback_status, favorites, teachers, observed_users, course_image, banner_image, concluded
            state[]                   | |string  |If set, only return courses that are in the given state(s). By default, `available` is returned for students and observers, and anything except `deleted`, for all other enrollment types                                                  Allowed values: unpublished, available, completed, deleted
        """
        method = "GET"
        api = f'/api/v1/courses'
        return self.request(method, api, params)
        
    def user_index(self, user_id, params={}):
        """
        Source Code:
            Code: CoursesController#user_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.user_index
        
        Scope:
            url:GET|/api/v1/users/:user_id/courses

        
        Module: Courses
        Function Description: List courses for a user

        Parameter Desc:
            include[]        | |string  |`needs_grading_count`: Optional information to include with each Course. When needs_grading_count is given, and the current user has grading rights, the total number of submissions needing grading for all assignments is returned.                                         `syllabus_body`: Optional information to include with each Course. When syllabus_body is given the user-generated html for the course syllabus is returned.                                         `public_description`: Optional information to include with each Course. When public_description is given the user-generated text for the course public description is returned.                                         `total_scores`: Optional information to include with each Course. When total_scores is given, any student enrollments will also include the fields ‘computed_current_score’, ‘computed_final_score’, ‘computed_current_grade’, and ‘computed_final_grade’ (see Enrollment documentation for more information on these fields). This argument is ignored if the course is configured to hide final grades.                                         `current_grading_period_scores`: Optional information to include with each Course. When current_grading_period_scores is given and total_scores is given, any student enrollments will also include the fields ‘has_grading_periods’, ‘totals_for_all_grading_periods_option’, ‘current_grading_period_title’, ‘current_grading_period_id’, current_period_computed_current_score’, ‘current_period_computed_final_score’, ‘current_period_computed_current_grade’, and ‘current_period_computed_final_grade’, as well as (if the user has permission) ‘current_period_unposted_current_score’, ‘current_period_unposted_final_score’, ‘current_period_unposted_current_grade’, and ‘current_period_unposted_final_grade’ (see Enrollment documentation for more information on these fields). In addition, when this argument is passed, the course will have a ‘has_grading_periods’ attribute on it. This argument is ignored if the course is configured to hide final grades or if the total_scores argument is not included.                                         `grading_periods`: Optional information to include with each Course. When grading_periods is given, a list of the grading periods associated with each course is returned.                                         `term`: Optional information to include with each Course. When term is given, the information for the enrollment term for each course is returned.                                         `account`: Optional information to include with each Course. When account is given, the account json for each course is returned.                                         `course_progress`: Optional information to include with each Course. When course_progress is given, each course will include a ‘course_progress’ object with the fields: ‘requirement_count’, an integer specifying the total number of requirements in the course, ‘requirement_completed_count’, an integer specifying the total number of requirements in this course that have been completed, and ‘next_requirement_url’, a string url to the next requirement item, and ‘completed_at’, the date the course was completed (null if incomplete). ‘next_requirement_url’ will be null if all requirements have been completed or the current module does not require sequential progress. `course_progress` will return an error message if the course is not module based or the user is not enrolled as a student in the course.                                         `sections`: Section enrollment information to include with each Course. Returns an array of hashes containing the section ID (id), section name (name), start and end dates (start_at, end_at), as well as the enrollment type (enrollment_role, e.g. ‘StudentEnrollment’).                                         `storage_quota_used_mb`: The amount of storage space used by the files in this course                                         `total_students`: Optional information to include with each Course. Returns an integer for the total amount of active and invited students.                                         `passback_status`: Include the grade passback_status                                         `favorites`: Optional information to include with each Course. Indicates if the user has marked the course as a favorite course.                                         `teachers`: Teacher information to include with each Course. Returns an array of hashes containing the UserDisplay information for each teacher in the course.                                         `observed_users`: Optional information to include with each Course. Will include data for observed users if the current user has an observer enrollment.                                         `tabs`: Optional information to include with each Course. Will include the list of tabs configured for each course.  See the List available tabs API for more information.                                         `course_image`: Optional information to include with each Course. Returns course image url if a course image has been set.                                         `banner_image`: Optional information to include with each Course. Returns course banner image url if the course is a Canvas for Elementary subject and a banner image has been set.                                         `concluded`: Optional information to include with each Course. Indicates whether the course has been concluded, taking course and term dates into account.                                         Allowed values: needs_grading_count, syllabus_body, public_description, total_scores, current_grading_period_scores, grading_periods, term, account, course_progress, sections, storage_quota_used_mb, total_students, passback_status, favorites, teachers, observed_users, course_image, banner_image, concluded
            state[]          | |string  |If set, only return courses that are in the given state(s). By default, `available` is returned for students and observers, and anything except `deleted`, for all other enrollment types                                         Allowed values: unpublished, available, completed, deleted
            enrollment_state | |string  |When set, only return courses where the user has an enrollment with the given state. This will respect section/course/term date overrides.                                         Allowed values: active, invited_or_pending, completed
            homeroom         | |boolean |If set, only return homeroom courses.
        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/courses'
        return self.request(method, api, params)
        
    def user_progress(self, course_id, user_id, params={}):
        """
        Source Code:
            Code: CoursesController#user_progress,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.user_progress
        
        Scope:
            url:GET|/api/v1/courses/:course_id/users/:user_id/progress

        
        Module: Courses
        Function Description: Get user progress

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/users/{user_id}/progress'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: CoursesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/courses

        
        Module: Courses
        Function Description: Create a new course

        Parameter Desc:
            course[name]                                 | |string   |The name of the course. If omitted, the course will be named `Unnamed Course.`
            course[course_code]                          | |string   |The course code for the course.
            course[start_at]                             | |DateTime |Course start date in ISO8601 format, e.g. 2011-01-01T01:00Z This value is ignored unless ‘restrict_enrollments_to_course_dates’ is set to true.
            course[end_at]                               | |DateTime |Course end date in ISO8601 format. e.g. 2011-01-01T01:00Z This value is ignored unless ‘restrict_enrollments_to_course_dates’ is set to true.
            course[license]                              | |string   |The name of the licensing. Should be one of the following abbreviations (a descriptive name is included in parenthesis for reference):                                                                      ‘private’ (Private Copyrighted)                                                                      ‘cc_by_nc_nd’ (CC Attribution Non-Commercial No Derivatives)                                                                      ‘cc_by_nc_sa’ (CC Attribution Non-Commercial Share Alike)                                                                      ‘cc_by_nc’ (CC Attribution Non-Commercial)                                                                      ‘cc_by_nd’ (CC Attribution No Derivatives)                                                                      ‘cc_by_sa’ (CC Attribution Share Alike)                                                                      ‘cc_by’ (CC Attribution)                                                                      ‘public_domain’ (Public Domain).
            course[is_public]                            | |boolean  |Set to true if course is public to both authenticated and unauthenticated users.
            course[is_public_to_auth_users]              | |boolean  |Set to true if course is public only to authenticated users.
            course[public_syllabus]                      | |boolean  |Set to true to make the course syllabus public.
            course[public_syllabus_to_auth]              | |boolean  |Set to true to make the course syllabus public for authenticated users.
            course[public_description]                   | |string   |A publicly visible description of the course.
            course[allow_student_wiki_edits]             | |boolean  |If true, students will be able to modify the course wiki.
            course[allow_wiki_comments]                  | |boolean  |If true, course members will be able to comment on wiki pages.
            course[allow_student_forum_attachments]      | |boolean  |If true, students can attach files to forum posts.
            course[open_enrollment]                      | |boolean  |Set to true if the course is open enrollment.
            course[self_enrollment]                      | |boolean  |Set to true if the course is self enrollment.
            course[restrict_enrollments_to_course_dates] | |boolean  |Set to true to restrict user enrollments to the start and end dates of the course. This value must be set to true in order to specify a course start date and/or end date.
            course[term_id]                              | |string   |The unique ID of the term to create to course in.
            course[sis_course_id]                        | |string   |The unique SIS identifier.
            course[integration_id]                       | |string   |The unique Integration identifier.
            course[hide_final_grades]                    | |boolean  |If this option is set to true, the totals in student grades summary will be hidden.
            course[apply_assignment_group_weights]       | |boolean  |Set to true to weight final grade based on assignment groups percentages.
            course[time_zone]                            | |string   |The time zone for the course. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            offer                                        | |boolean  |If this option is set to true, the course will be available to students immediately.
            enroll_me                                    | |boolean  |Set to true to enroll the current user as the teacher.
            course[default_view]                         | |string   |The type of page that users will see when they first visit the course                                                                      ‘feed’ Recent Activity Dashboard                                                                      ‘modules’ Course Modules/Sections Page                                                                      ‘assignments’ Course Assignments List                                                                      ‘syllabus’ Course Syllabus Page                                                                      other types may be added in the future                                                                      Allowed values: feed, wiki, modules, syllabus, assignments
            course[syllabus_body]                        | |string   |The syllabus body for the course
            course[grading_standard_id]                  | |integer  |The grading standard id to set for the course.  If no value is provided for this argument the current grading_standard will be un-set from this course.
            course[grade_passback_setting]               | |string   |Optional. The grade_passback_setting for the course. Only ‘nightly_sync’, ‘disabled’, and ` are allowed
            course[course_format]                        | |string   |Optional. Specifies the format of the course. (Should be ‘on_campus’, ‘online’, or ‘blended’)
            enable_sis_reactivation                      | |boolean  |When true, will first try to re-activate a deleted course with matching sis_course_id if possible.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/courses'
        return self.request(method, api, params)
        
    def create_file(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.create_file
        
        Scope:
            url:POST|/api/v1/courses/:course_id/files

        
        Module: Courses
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/files'
        return self.request(method, api, params)
        
    def students(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#students,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.students
        
        Scope:
            url:GET|/api/v1/courses/:course_id/students

        
        Module: Courses
        Function Description: List students

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/students'
        return self.request(method, api, params)
        
    def users(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.users
        
        Scope:
            url:GET|/api/v1/courses/:course_id/users
            url:GET|/api/v1/courses/:course_id/search_users

        
        Module: Courses
        Function Description: List users in course

        Parameter Desc:
            search_term        | |string  |The partial name or full ID of the users to match and return in the results list.
            sort               | |string  |When set, sort the results of the search based on the given field.                                           Allowed values: username, last_login, email, sis_id
            enrollment_type[]  | |string  |When set, only return users where the user is enrolled as this type. `student_view` implies include[]=test_student. This argument is ignored if enrollment_role is given.                                           Allowed values: teacher, student, student_view, ta, observer, designer
            enrollment_role    | |string  |Deprecated When set, only return users enrolled with the specified course-level role.  This can be a role created with the Add Role API or a base role type of ‘StudentEnrollment’, ‘TeacherEnrollment’, ‘TaEnrollment’, ‘ObserverEnrollment’, or ‘DesignerEnrollment’.
            enrollment_role_id | |integer |When set, only return courses where the user is enrolled with the specified course-level role.  This can be a role created with the Add Role API or a built_in role id with type ‘StudentEnrollment’, ‘TeacherEnrollment’, ‘TaEnrollment’, ‘ObserverEnrollment’, or ‘DesignerEnrollment’.
            include[]          | |string  |`enrollments`:                                           Optionally include with each Course the user’s current and invited enrollments. If the user is enrolled as a student, and the account has permission to manage or view all grades, each enrollment will include a ‘grades’ key with ‘current_score’, ‘final_score’, ‘current_grade’ and ‘final_grade’ values.                                           `locked`: Optionally include whether an enrollment is locked.                                           `avatar_url`: Optionally include avatar_url.                                           `bio`: Optionally include each user’s bio.                                           `test_student`: Optionally include the course’s Test Student,                                           if present. Default is to not include Test Student.                                           `custom_links`: Optionally include plugin-supplied custom links for each student,                                           such as analytics information                                           `current_grading_period_scores`: if enrollments is included as                                           well as this directive, the scores returned in the enrollment will be for the current grading period if there is one. A ‘grading_period_id’ value will also be included with the scores. if grading_period_id is nil there is no current grading period and the score is a total score.                                           `uuid`: Optionally include the users uuid                                           Allowed values: enrollments, locked, avatar_url, test_student, bio, custom_links, current_grading_period_scores, uuid
            user_id            | |string  |If this parameter is given and it corresponds to a user in the course, the page parameter will be ignored and the page containing the specified user will be returned instead.
            user_ids[]         | |integer |If included, the course users set will only include users with IDs specified by the param. Note: this will not work in conjunction with the `user_id` argument but multiple user_ids can be included.
            enrollment_state[] | |string  |When set, only return users where the enrollment workflow state is of one of the given types. `active` and `invited` enrollments are returned by default.                                           Allowed values: active, invited, rejected, completed, inactive
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/users'
        return self.request(method, api, params)
        
    def recent_students(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#recent_students,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.recent_students
        
        Scope:
            url:GET|/api/v1/courses/:course_id/recent_students

        
        Module: Courses
        Function Description: List recently logged in students

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/recent_students'
        return self.request(method, api, params)
        
    def user(self, course_id, id, params={}):
        """
        Source Code:
            Code: CoursesController#user,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.user
        
        Scope:
            url:GET|/api/v1/courses/:course_id/users/:id

        
        Module: Courses
        Function Description: Get single user

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/users/{id}'
        return self.request(method, api, params)
        
    def content_share_users(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#content_share_users,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.content_share_users
        
        Scope:
            url:GET|/api/v1/courses/:course_id/content_share_users

        
        Module: Courses
        Function Description: Search for content share users

        Parameter Desc:
            search_term |Required |string |Term used to find users.  Will search available share users with the search term in their name.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/content_share_users'
        return self.request(method, api, params)
        
    def preview_html(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#preview_html,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.preview_html
        
        Scope:
            url:POST|/api/v1/courses/:course_id/preview_html

        
        Module: Courses
        Function Description: Preview processed html

        Parameter Desc:
            html | |string |The html content to process

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/preview_html \
                 -F 'html=<p><badhtml></badhtml>processed html</p>' \
                 -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "html": "<p>processed html</p>"
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/preview_html'
        return self.request(method, api, params)
        
    def activity_stream(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#activity_stream,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.activity_stream
        
        Scope:
            url:GET|/api/v1/courses/:course_id/activity_stream

        
        Module: Courses
        Function Description: Course activity stream

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/activity_stream'
        return self.request(method, api, params)
        
    def activity_stream_summary(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#activity_stream_summary,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.activity_stream_summary
        
        Scope:
            url:GET|/api/v1/courses/:course_id/activity_stream/summary

        
        Module: Courses
        Function Description: Course activity stream summary

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/activity_stream/summary'
        return self.request(method, api, params)
        
    def todo_items(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#todo_items,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.todo_items
        
        Scope:
            url:GET|/api/v1/courses/:course_id/todo

        
        Module: Courses
        Function Description: Course TODO items

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/todo'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: CoursesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:id

        
        Module: Courses
        Function Description: Delete/Conclude a course

        Parameter Desc:
            event |Required |string |The action to take on the course.                                     Allowed values: delete, conclude

        Response Example: 
            { "delete": "true" }
        """
        method = "DELETE"
        api = f'/api/v1/courses/{id}'
        return self.request(method, api, params)
        
    def api_settings(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#api_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.api_settings
        
        Scope:
            url:GET|/api/v1/courses/:course_id/settings

        
        Module: Courses
        Function Description: Get course settings


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/settings \
              -X GET \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "allow_student_discussion_topics": true,
              "allow_student_forum_attachments": false,
              "allow_student_discussion_editing": true,
              "grading_standard_enabled": true,
              "grading_standard_id": 137,
              "allow_student_organized_groups": true,
              "hide_final_grades": false,
              "hide_distribution_graphs": false,
              "hide_sections_on_course_users_page": false,
              "lock_all_announcements": true,
              "usage_rights_required": false,
              "homeroom_course": false,
              "default_due_time": "23:59:59",
              "conditional_release": false
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/settings'
        return self.request(method, api, params)
        
    def update_settings(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#update_settings,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.update_settings
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/settings

        
        Module: Courses
        Function Description: Update course settings

        Parameter Desc:
            allow_student_discussion_topics           | |boolean |Let students create discussion topics
            allow_student_forum_attachments           | |boolean |Let students attach files to discussions
            allow_student_discussion_editing          | |boolean |Let students edit or delete their own discussion replies
            allow_student_organized_groups            | |boolean |Let students organize their own groups
            allow_student_discussion_reporting        | |boolean |Let students report offensive discussion content
            allow_student_anonymous_discussion_topics | |boolean |Let students create anonymous discussion topics
            filter_speed_grader_by_student_group      | |boolean |Filter SpeedGrader to only the selected student group
            hide_final_grades                         | |boolean |Hide totals in student grades summary
            hide_distribution_graphs                  | |boolean |Hide grade distribution graphs from students
            hide_sections_on_course_users_page        | |boolean |Disallow students from viewing students in sections they do not belong to
            lock_all_announcements                    | |boolean |Disable comments on announcements
            usage_rights_required                     | |boolean |Copyright and license information must be provided for files before they are published.
            restrict_student_past_view                | |boolean |Restrict students from viewing courses after end date
            restrict_student_future_view              | |boolean |Restrict students from viewing courses before start date
            show_announcements_on_home_page           | |boolean |Show the most recent announcements on the Course home page (if a Wiki, defaults to five announcements, configurable via home_page_announcement_limit). Canvas for Elementary subjects ignore this setting.
            home_page_announcement_limit              | |integer |Limit the number of announcements on the home page if enabled via show_announcements_on_home_page
            syllabus_course_summary                   | |boolean |Show the course summary (list of assignments and calendar events) on the syllabus page. Default is true.
            default_due_time                          | |string  |Set the default due time for assignments. This is the time that will be pre-selected in the Canvas user interface when setting a due date for an assignment. It does not change when any existing assignment is due. It should be given in 24-hour HH:MM:SS format. The default is `23:59:59`. Use `inherit` to inherit the account setting.
            conditional_release                       | |boolean |Enable or disable individual learning paths for students based on assessment
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/settings'
        return self.request(method, api, params)
        
    def student_view_student(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#student_view_student,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.student_view_student
        
        Scope:
            url:GET|/api/v1/courses/:course_id/student_view_student

        
        Module: Courses
        Function Description: Return test student for course

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/student_view_student'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: CoursesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.show
        
        Scope:
            url:GET|/api/v1/courses/:id
            url:GET|/api/v1/accounts/:account_id/courses/:id

        
        Module: Courses
        Function Description: Get a single course

        Parameter Desc:
            include[]     | |string  |`all_courses`: Also search recently deleted courses.                                      `permissions`: Include permissions the current user has for the course.                                      `observed_users`: Include observed users in the enrollments                                      `course_image`: Include course image url if a course image has been set                                      `banner_image`: Include course banner image url if the course is a Canvas for Elementary subject and a banner image has been set                                      `concluded`: Optional information to include with Course. Indicates whether the course has been concluded, taking course and term dates into account.                                      Allowed values: needs_grading_count, syllabus_body, public_description, total_scores, current_grading_period_scores, term, account, course_progress, sections, storage_quota_used_mb, total_students, passback_status, favorites, teachers, observed_users, all_courses, permissions, course_image, banner_image, concluded
            teacher_limit | |integer |The maximum number of teacher enrollments to show. If the course contains more teachers than this, instead of giving the teacher enrollments, the count of teachers will be given under a teacher_count key.
        """
        method = "GET"
        api = f'/api/v1/courses/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: CoursesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.update
        
        Scope:
            url:PUT|/api/v1/courses/:id

        
        Module: Courses
        Function Description: Update a course

        Parameter Desc:
            course[account_id]                                | |integer                        |The unique ID of the account to move the course to.
            course[name]                                      | |string                         |The name of the course. If omitted, the course will be named `Unnamed Course.`
            course[course_code]                               | |string                         |The course code for the course.
            course[start_at]                                  | |DateTime                       |Course start date in ISO8601 format, e.g. 2011-01-01T01:00Z This value is ignored unless ‘restrict_enrollments_to_course_dates’ is set to true, or the course is already published.
            course[end_at]                                    | |DateTime                       |Course end date in ISO8601 format. e.g. 2011-01-01T01:00Z This value is ignored unless ‘restrict_enrollments_to_course_dates’ is set to true.
            course[license]                                   | |string                         |The name of the licensing. Should be one of the following abbreviations (a descriptive name is included in parenthesis for reference):                                                                                                 ‘private’ (Private Copyrighted)                                                                                                 ‘cc_by_nc_nd’ (CC Attribution Non-Commercial No Derivatives)                                                                                                 ‘cc_by_nc_sa’ (CC Attribution Non-Commercial Share Alike)                                                                                                 ‘cc_by_nc’ (CC Attribution Non-Commercial)                                                                                                 ‘cc_by_nd’ (CC Attribution No Derivatives)                                                                                                 ‘cc_by_sa’ (CC Attribution Share Alike)                                                                                                 ‘cc_by’ (CC Attribution)                                                                                                 ‘public_domain’ (Public Domain).
            course[is_public]                                 | |boolean                        |Set to true if course is public to both authenticated and unauthenticated users.
            course[is_public_to_auth_users]                   | |boolean                        |Set to true if course is public only to authenticated users.
            course[public_syllabus]                           | |boolean                        |Set to true to make the course syllabus public.
            course[public_syllabus_to_auth]                   | |boolean                        |Set to true to make the course syllabus to public for authenticated users.
            course[public_description]                        | |string                         |A publicly visible description of the course.
            course[allow_student_wiki_edits]                  | |boolean                        |If true, students will be able to modify the course wiki.
            course[allow_wiki_comments]                       | |boolean                        |If true, course members will be able to comment on wiki pages.
            course[allow_student_forum_attachments]           | |boolean                        |If true, students can attach files to forum posts.
            course[open_enrollment]                           | |boolean                        |Set to true if the course is open enrollment.
            course[self_enrollment]                           | |boolean                        |Set to true if the course is self enrollment.
            course[restrict_enrollments_to_course_dates]      | |boolean                        |Set to true to restrict user enrollments to the start and end dates of the course. Setting this value to false will remove the course end date (if it exists), as well as the course start date (if the course is unpublished).
            course[term_id]                                   | |integer                        |The unique ID of the term to create to course in.
            course[sis_course_id]                             | |string                         |The unique SIS identifier.
            course[integration_id]                            | |string                         |The unique Integration identifier.
            course[hide_final_grades]                         | |boolean                        |If this option is set to true, the totals in student grades summary will be hidden.
            course[time_zone]                                 | |string                         |The time zone for the course. Allowed time zones are IANA time zones or friendlier Ruby on Rails time zones.
            course[apply_assignment_group_weights]            | |boolean                        |Set to true to weight final grade based on assignment groups percentages.
            course[storage_quota_mb]                          | |integer                        |Set the storage quota for the course, in megabytes. The caller must have the `Manage storage quotas` account permission.
            offer                                             | |boolean                        |If this option is set to true, the course will be available to students immediately.
            course[event]                                     | |string                         |The action to take on each course.                                                                                                 ‘claim’ makes a course no longer visible to students. This action is also called `unpublish` on the web site. A course cannot be unpublished if students have received graded submissions.                                                                                                 ‘offer’ makes a course visible to students. This action is also called `publish` on the web site.                                                                                                 ‘conclude’ prevents future enrollments and makes a course read-only for all participants. The course still appears in prior-enrollment lists.                                                                                                 ‘delete’ completely removes the course from the web site (including course menus and prior-enrollment lists). All enrollments are deleted. Course content may be physically deleted at a future date.                                                                                                 ‘undelete’ attempts to recover a course that has been deleted. This action requires account administrative rights. (Recovery is not guaranteed; please conclude rather than delete a course if there is any possibility the course will be used again.) The recovered course will be unpublished. Deleted enrollments will not be recovered.                                                                                                 Allowed values: claim, offer, conclude, delete, undelete
            course[default_view]                              | |string                         |The type of page that users will see when they first visit the course                                                                                                 ‘feed’ Recent Activity Dashboard                                                                                                 ‘wiki’ Wiki Front Page                                                                                                 ‘modules’ Course Modules/Sections Page                                                                                                 ‘assignments’ Course Assignments List                                                                                                 ‘syllabus’ Course Syllabus Page                                                                                                 other types may be added in the future                                                                                                 Allowed values: feed, wiki, modules, syllabus, assignments
            course[syllabus_body]                             | |string                         |The syllabus body for the course
            course[syllabus_course_summary]                   | |boolean                        |Optional. Indicates whether the Course Summary (consisting of the course’s assignments and calendar events) is displayed on the syllabus page. Defaults to true.
            course[grading_standard_id]                       | |integer                        |The grading standard id to set for the course.  If no value is provided for this argument the current grading_standard will be un-set from this course.
            course[grade_passback_setting]                    | |string                         |Optional. The grade_passback_setting for the course. Only ‘nightly_sync’ and ` are allowed
            course[course_format]                             | |string                         |Optional. Specifies the format of the course. (Should be either ‘on_campus’ or ‘online’)
            course[image_id]                                  | |integer                        |This is a file ID corresponding to an image file in the course that will be used as the course image. This will clear the course’s image_url setting if set.  If you attempt to provide image_url and image_id in a request it will fail.
            course[image_url]                                 | |string                         |This is a URL to an image to be used as the course image. This will clear the course’s image_id setting if set.  If you attempt to provide image_url and image_id in a request it will fail.
            course[remove_image]                              | |boolean                        |If this option is set to true, the course image url and course image ID are both set to nil
            course[remove_banner_image]                       | |boolean                        |If this option is set to true, the course banner image url and course banner image ID are both set to nil
            course[blueprint]                                 | |boolean                        |Sets the course as a blueprint course.
            course[blueprint_restrictions]                    | |BlueprintRestriction           |Sets a default set to apply to blueprint course objects when restricted, unless use_blueprint_restrictions_by_object_type is enabled. See the Blueprint Restriction documentation
            course[use_blueprint_restrictions_by_object_type] | |boolean                        |When enabled, the blueprint_restrictions parameter will be ignored in favor of the blueprint_restrictions_by_object_type parameter
            course[blueprint_restrictions_by_object_type]     | |multiple BlueprintRestrictions |Allows setting multiple Blueprint Restriction to apply to blueprint course objects of the matching type when restricted. The possible object types are `assignment`, `attachment`, `discussion_topic`, `quiz` and `wiki_page`. Example usage:                                                                                                 course[blueprint_restrictions_by_object_type][assignment][content]=1
            course[homeroom_course]                           | |boolean                        |Sets the course as a homeroom course. The setting takes effect only when the course is associated with a Canvas for Elementary-enabled account.
            course[sync_enrollments_from_homeroom]            | |string                         |Syncs enrollments from the homeroom that is set in homeroom_course_id. The setting only takes effect when the course is associated with a Canvas for Elementary-enabled account and sync_enrollments_from_homeroom is enabled.
            course[homeroom_course_id]                        | |string                         |Sets the Homeroom Course id to be used with sync_enrollments_from_homeroom. The setting only takes effect when the course is associated with a Canvas for Elementary-enabled account and sync_enrollments_from_homeroom is enabled.
            course[template]                                  | |boolean                        |Enable or disable the course as a template that can be selected by an account
            course[course_color]                              | |string                         |Sets a color in hex code format to be associated with the course. The setting takes effect only when the course is associated with a Canvas for Elementary-enabled account.
            course[friendly_name]                             | |string                         |Set a friendly name for the course. If this is provided and the course is associated with a Canvas for Elementary account, it will be shown instead of the course name. This setting takes priority over course nicknames defined by individual users.
            course[enable_course_paces]                       | |boolean                        |Enable or disable Course Pacing for the course. This setting only has an effect when the Course Pacing feature flag is enabled for the sub-account. Otherwise, Course Pacing are always disabled.                                                                                                 Note: Course Pacing is in active development.
            course[conditional_release]                       | |boolean                        |Enable or disable individual learning paths for students based on assessment
            override_sis_stickiness                           | |boolean                        |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id> \
              -X PUT \
              -H 'Authorization: Bearer <token>' \
              -d 'course[name]=New course name' \
              -d 'course[start_at]=2012-05-05T00:00:00Z'

        Response Example: 
            {
              "name": "New course name",
              "course_code": "COURSE-001",
              "start_at": "2012-05-05T00:00:00Z",
              "end_at": "2012-08-05T23:59:59Z",
              "sis_course_id": "12345"
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{id}'
        return self.request(method, api, params)
        
    def batch_update(self, account_id, params={}):
        """
        Source Code:
            Code: CoursesController#batch_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.batch_update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/courses

        
        Module: Courses
        Function Description: Update courses

        Parameter Desc:
            course_ids[] |Required |string |List of ids of courses to update. At most 500 courses may be updated in one call.
            event        |Required |string |The action to take on each course.  Must be one of ‘offer’, ‘conclude’, ‘delete’, or ‘undelete’.                                            ‘offer’ makes a course visible to students. This action is also called `publish` on the web site.                                            ‘conclude’ prevents future enrollments and makes a course read-only for all participants. The course still appears in prior-enrollment lists.                                            ‘delete’ completely removes the course from the web site (including course menus and prior-enrollment lists). All enrollments are deleted. Course content may be physically deleted at a future date.                                            ‘undelete’ attempts to recover a course that has been deleted. (Recovery is not guaranteed; please conclude rather than delete a course if there is any possibility the course will be used again.) The recovered course will be unpublished. Deleted enrollments will not be recovered.                                            Allowed values: offer, conclude, delete, undelete
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/courses'
        return self.request(method, api, params)
        
    def reset_content(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#reset_content,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.reset_content
        
        Scope:
            url:POST|/api/v1/courses/:course_id/reset_content

        
        Module: Courses
        Function Description: Reset a course

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/reset_content'
        return self.request(method, api, params)
        
    def effective_due_dates(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#effective_due_dates,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.effective_due_dates
        
        Scope:
            url:GET|/api/v1/courses/:course_id/effective_due_dates

        
        Module: Courses
        Function Description: Get effective due dates

        Parameter Desc:
            assignment_ids[] | |string |no description

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/effective_due_dates
              -X GET \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "1": {
                 "14": { "due_at": "2015-09-05", "grading_period_id": null, "in_closed_grading_period": false },
                 "15": { due_at: null, "grading_period_id": 3, "in_closed_grading_period": true }
              },
              "2": {
                 "14": { "due_at": "2015-08-05", "grading_period_id": 3, "in_closed_grading_period": true }
              }
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/effective_due_dates'
        return self.request(method, api, params)
        
    def permissions(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#permissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.permissions
        
        Scope:
            url:GET|/api/v1/courses/:course_id/permissions

        
        Module: Courses
        Function Description: Permissions

        Parameter Desc:
            permissions[] | |string |List of permissions to check against the authenticated user. Permission names are documented in the Create a role endpoint.

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/permissions \
              -H 'Authorization: Bearer <token>' \
              -d 'permissions[]=manage_grades'
              -d 'permissions[]=send_messages'

        Response Example: 
            {'manage_grades': 'false', 'send_messages': 'true'}
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/permissions'
        return self.request(method, api, params)
        
    def bulk_user_progress(self, course_id, params={}):
        """
        Source Code:
            Code: CoursesController#bulk_user_progress,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.bulk_user_progress
        
        Scope:
            url:GET|/api/v1/courses/:course_id/bulk_user_progress

        
        Module: Courses
        Function Description: Get bulk user progress


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/bulk_user_progress \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            [
              {
                "id": 1,
                "display_name": "Test Student 1",
                "avatar_image_url": "https://<canvas>/images/messages/avatar-50.png",
                "html_url": "https://<canvas>/courses/1/users/1",
                "pronouns": null,
                "progress": {
                  "requirement_count": 2,
                  "requirement_completed_count": 1,
                  "next_requirement_url": "https://<canvas>/courses/<course_id>/modules/items/<item_id>",
                  "completed_at": null
                }
              },
              {
                "id": 2,
                "display_name": "Test Student 2",
                "avatar_image_url": "https://<canvas>/images/messages/avatar-50.png",
                "html_url": "https://<canvas>/courses/1/users/2",
                "pronouns": null,
                "progress": {
                  "requirement_count": 2,
                  "requirement_completed_count": 2,
                  "next_requirement_url": null,
                  "completed_at": "2021-08-10T16:26:08Z"
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/bulk_user_progress'
        return self.request(method, api, params)
        
    def dismiss_migration_limitation_msg(self, id, params={}):
        """
        Source Code:
            Code: CoursesController#dismiss_migration_limitation_msg,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/courses_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.courses.dismiss_migration_limitation_msg
        
        Scope:
            url:POST|/api/v1/courses/:id/dismiss_migration_limitation_message

        
        Module: Courses
        Function Description: Remove quiz migration alert


        Response Example: 
            { "success": "true" }
        """
        method = "POST"
        api = f'/api/v1/courses/{id}/dismiss_migration_limitation_message'
        return self.request(method, api, params)
        
    def copy_course_status(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContentImportsController#copy_course_status,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_imports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_imports.copy_course_status
        
        Scope:
            url:GET|/api/v1/courses/:course_id/course_copy/:id

        
        Module: Courses
        Function Description: Get course copy status


        Response Example: 
            {'progress':100, 'workflow_state':'completed', 'id':257, 'created_at':'2011-11-17T16:50:06Z', 'status_url':'/api/v1/courses/9457/course_copy/257'}
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/course_copy/{id}'
        return self.request(method, api, params)
        
    def copy_course_content(self, course_id, params={}):
        """
        Source Code:
            Code: ContentImportsController#copy_course_content,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_imports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_imports.copy_course_content
        
        Scope:
            url:POST|/api/v1/courses/:course_id/course_copy

        
        Module: Courses
        Function Description: Copy course content

        Parameter Desc:
            source_course | |string |ID or SIS-ID of the course to copy the content from
            except[]      | |string |A list of the course content types to exclude, all areas not listed will be copied.                                     Allowed values: course_settings, assignments, external_tools, files, topics, calendar_events, quizzes, wiki_pages, modules, outcomes
            only[]        | |string |A list of the course content types to copy, all areas not listed will not be copied.                                     Allowed values: course_settings, assignments, external_tools, files, topics, calendar_events, quizzes, wiki_pages, modules, outcomes
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/course_copy'
        return self.request(method, api, params)
        