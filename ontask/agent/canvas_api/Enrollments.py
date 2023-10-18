from .etc.conf import *
from .res import *

class Enrollments(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/enrollments
            url:GET|/api/v1/sections/:section_id/enrollments
            url:GET|/api/v1/users/:user_id/enrollments

        
        Module: Enrollments
        Function Description: List enrollments

        Parameter Desc:
            type[]               | |string  |A list of enrollment types to return. Accepted values are ‘StudentEnrollment’, ‘TeacherEnrollment’, ‘TaEnrollment’, ‘DesignerEnrollment’, and ‘ObserverEnrollment.’ If omitted, all enrollment types are returned. This argument is ignored if ‘role` is given.
            role[]               | |string  |A list of enrollment roles to return. Accepted values include course-level roles created by the Add Role API as well as the base enrollment types accepted by the ‘type` argument above.
            state[]              | |string  |Filter by enrollment state. If omitted, ‘active’ and ‘invited’ enrollments are returned. The following synthetic states are supported only when querying a user’s enrollments (either via user_id argument or via user enrollments endpoint): current_and_invited, current_and_future, current_and_concluded                                             Allowed values: active, invited, creation_pending, deleted, rejected, completed, inactive, current_and_invited, current_and_future, current_and_concluded
            include[]            | |string  |Array of additional information to include on the enrollment or user records. `avatar_url` and `group_ids` will be returned on the user record. If `current_points` is specified, the fields `current_points` and (if the caller has permissions to manage grades) `unposted_current_points` will be included in the `grades` hash for student enrollments.                                             Allowed values: avatar_url, group_ids, locked, observed_users, can_be_removed, uuid, current_points
            user_id              | |string  |Filter by user_id (only valid for course or section enrollment queries). If set to the current user’s id, this is a way to determine if the user has any enrollments in the course or section, independent of whether the user has permission to view other people on the roster.
            grading_period_id    | |integer |Return grades for the given grading_period.  If this parameter is not specified, the returned grades will be for the whole course.
            enrollment_term_id   | |integer |Returns only enrollments for the specified enrollment term. This parameter only applies to the user enrollments path. May pass the ID from the enrollment terms api or the SIS id prepended with ‘sis_term_id:’.
            sis_account_id[]     | |string  |Returns only enrollments for the specified SIS account ID(s). Does not look into sub_accounts. May pass in array or string.
            sis_course_id[]      | |string  |Returns only enrollments matching the specified SIS course ID(s). May pass in array or string.
            sis_section_id[]     | |string  |Returns only section enrollments matching the specified SIS section ID(s). May pass in array or string.
            sis_user_id[]        | |string  |Returns only enrollments for the specified SIS user ID(s). May pass in array or string.
            created_for_sis_id[] | |boolean |If sis_user_id is present and created_for_sis_id is true, Returns only enrollments for the specified SIS ID(s). If a user has two sis_id’s, one enrollment may be created using one of the two ids. This would limit the enrollments returned from the endpoint to enrollments that were created from a sis_import with that sis_user_id
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/enrollments'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/enrollments/:id

        
        Module: Enrollments
        Function Description: Enrollment by ID

        Parameter Desc:
            id |Required |integer |The ID of the enrollment object
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/enrollments/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/enrollments
            url:POST|/api/v1/sections/:section_id/enrollments

        
        Module: Enrollments
        Function Description: Enroll a user

        Parameter Desc:
            enrollment[start_at]                           |         |DateTime   |The start time of the enrollment, in ISO8601 format. e.g. 2012-04-18T23:08:51Z
            enrollment[end_at]                             |         |DateTime   |The end time of the enrollment, in ISO8601 format. e.g. 2012-04-18T23:08:51Z
            enrollment[user_id]                            |Required |string     |The ID of the user to be enrolled in the course.
            enrollment[type]                               |Required |string     |Enroll the user as a student, teacher, TA, observer, or designer. If no value is given, the type will be inferred by enrollment if supplied, otherwise ‘StudentEnrollment’ will be used.                                                                                  Allowed values: StudentEnrollment, TeacherEnrollment, TaEnrollment, ObserverEnrollment, DesignerEnrollment
            enrollment[role]                               |         |Deprecated |Assigns a custom course-level role to the user.
            enrollment[role_id]                            |         |integer    |Assigns a custom course-level role to the user.
            enrollment[enrollment_state]                   |         |string     |If set to ‘active,’ student will be immediately enrolled in the course. Otherwise they will be required to accept a course invitation. Default is ‘invited.’.                                                                                  If set to ‘inactive’, student will be listed in the course roster for teachers, but will not be able to participate in the course until their enrollment is activated.                                                                                  Allowed values: active, invited, inactive
            enrollment[course_section_id]                  |         |integer    |The ID of the course section to enroll the student in. If the section-specific URL is used, this argument is redundant and will be ignored.
            enrollment[limit_privileges_to_course_section] |         |boolean    |If set, the enrollment will only allow the user to see and interact with users enrolled in the section given by course_section_id.                                                                                  For teachers and TAs, this includes grading privileges.                                                                                  Section-limited students will not see any users (including teachers and TAs) not enrolled in their sections.                                                                                  Users may have other enrollments that grant privileges to multiple sections in the same course.
            enrollment[notify]                             |         |boolean    |If true, a notification will be sent to the enrolled user. Notifications are not sent by default.
            enrollment[self_enrollment_code]               |         |string     |If the current user is not allowed to manage enrollments in this course, but the course allows self-enrollment, the user can self- enroll as a student in the default section by passing in a valid code. When self-enrolling, the user_id must be ‘self’. The enrollment_state will be set to ‘active’ and all other arguments will be ignored.
            enrollment[self_enrolled]                      |         |boolean    |If true, marks the enrollment as a self-enrollment, which gives students the ability to drop the course if desired. Defaults to false.
            enrollment[associated_user_id]                 |         |integer    |For an observer enrollment, the ID of a student to observe. This is a one-off operation; to automatically observe all a student’s enrollments (for example, as a parent), please use the User Observees API.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/enrollments'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/enrollments/:id

        
        Module: Enrollments
        Function Description: Conclude, deactivate, or delete an enrollment

        Parameter Desc:
            task | |string |The action to take on the enrollment. When inactive, a user will still appear in the course roster to admins, but be unable to participate. (`inactivate` and `deactivate` are equivalent tasks)                            Allowed values: conclude, delete, inactivate, deactivate
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/enrollments/{id}'
        return self.request(method, api, params)
        
    def accept(self, course_id, id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#accept,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.accept
        
        Scope:
            url:POST|/api/v1/courses/:course_id/enrollments/:id/accept

        
        Module: Enrollments
        Function Description: Accept Course Invitation


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/enrollments/:id/accept \
              -X POST \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "success": true
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/enrollments/{id}/accept'
        return self.request(method, api, params)
        
    def reject(self, course_id, id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#reject,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.reject
        
        Scope:
            url:POST|/api/v1/courses/:course_id/enrollments/:id/reject

        
        Module: Enrollments
        Function Description: Reject Course Invitation


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/enrollments/:id/reject \
              -X POST \
              -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "success": true
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/enrollments/{id}/reject'
        return self.request(method, api, params)
        
    def reactivate(self, course_id, id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#reactivate,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.reactivate
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/enrollments/:id/reactivate

        
        Module: Enrollments
        Function Description: Re-activate an enrollment

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/enrollments/{id}/reactivate'
        return self.request(method, api, params)
        
    def last_attended(self, course_id, user_id, params={}):
        """
        Source Code:
            Code: EnrollmentsApiController#last_attended,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/enrollments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.enrollments_api.last_attended
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/users/:user_id/last_attended

        
        Module: Enrollments
        Function Description: Add last attended date

        Parameter Desc:
            date | |Date |The last attended date of a student enrollment in a course.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/users/{user_id}/last_attended'
        return self.request(method, api, params)
        