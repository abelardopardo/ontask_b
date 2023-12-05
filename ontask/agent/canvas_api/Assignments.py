from .etc.conf import *
from .res import *

class Assignments(Res):
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: AssignmentsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignments/:id

        
        Module: Assignments
        Function Description: Delete an assignment

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignments/{id}'
        return self.request(method, api, params)
        
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments
            url:GET|/api/v1/courses/:course_id/assignment_groups/:assignment_group_id/assignments

        
        Module: Assignments
        Function Description: List assignments

        Parameter Desc:
            include[]                      | |string  |Optional information to include with each assignment:                                                       submission                                                       The current user’s current Submission                                                       assignment_visibility                                                       An array of ids of students who can see the assignment                                                       all_dates                                                       An array of AssignmentDate structures, one for each override, and also a base if the assignment has an `Everyone` / `Everyone Else` date                                                       overrides                                                       An array of AssignmentOverride structures                                                       observed_users                                                       An array of submissions for observed users                                                       can_edit                                                       an extra Boolean value will be included with each Assignment (and AssignmentDate if all_dates is supplied) to indicate whether the caller can edit the assignment or date. Moderated grading and closed grading periods may restrict a user’s ability to edit an assignment.                                                       score_statistics                                                       An object containing min, max, and mean score on this assignment. This will not be included for students if there are less than 5 graded assignments or if disabled by the instructor. Only valid if ‘submission’ is also included.                                                       Allowed values: submission, assignment_visibility, all_dates, overrides, observed_users, can_edit, score_statistics
            search_term                    | |string  |The partial title of the assignments to match and return.
            override_assignment_dates      | |boolean |Apply assignment overrides for each assignment, defaults to true.
            needs_grading_count_by_section | |boolean |Split up `needs_grading_count` by sections into the `needs_grading_count_by_section` key, defaults to false
            bucket                         | |string  |If included, only return certain assignments depending on due date and submission status.                                                       Allowed values: past, overdue, undated, ungraded, unsubmitted, upcoming, future
            assignment_ids[]               | |string  |if set, return only assignments specified
            order_by                       | |string  |Determines the order of the assignments. Defaults to `position`.                                                       Allowed values: position, name, due_at
            post_to_sis                    | |boolean |Return only assignments that have post_to_sis set or not set.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments'
        return self.request(method, api, params)
        
    def user_index(self, user_id, course_id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#user_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.user_index
        
        Scope:
            url:GET|/api/v1/users/:user_id/courses/:course_id/assignments

        
        Module: Assignments
        Function Description: List assignments for user

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/courses/{course_id}/assignments'
        return self.request(method, api, params)
        
    def duplicate(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#duplicate,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.duplicate
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/duplicate

        
        Module: Assignments
        Function Description: Duplicate assignnment

        Parameter Desc:
            result_type | |string |Optional information: When the root account has the feature ‘newquizzes_on_quiz_page` enabled and this argument is set to `Quiz` the response will be serialized into a quiz format(quizzes); When this argument isn’t specified the response will be serialized into an assignment format;                                   Allowed values: Quiz
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/duplicate'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:id

        
        Module: Assignments
        Function Description: Get a single assignment

        Parameter Desc:
            include[]                      | |string  |Associations to include with the assignment. The `assignment_visibility` option requires that the Differentiated Assignments course feature be turned on. If `observed_users` is passed, submissions for observed users will also be included. For `score_statistics` to be included, the `submission` option must also be set.                                                       Allowed values: submission, assignment_visibility, overrides, observed_users, can_edit, score_statistics
            override_assignment_dates      | |boolean |Apply assignment overrides to the assignment, defaults to true.
            needs_grading_count_by_section | |boolean |Split up `needs_grading_count` by sections into the `needs_grading_count_by_section` key, defaults to false
            all_dates                      | |boolean |All dates associated with the assignment, if applicable
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments

        
        Module: Assignments
        Function Description: Create an assignment

        Parameter Desc:
            assignment[name]                                  |Required |string             |The assignment name.
            assignment[position]                              |         |integer            |The position of this assignment in the group when displaying assignment lists.
            assignment[submission_types][]                    |         |string             |List of supported submission types for the assignment. Unless the assignment is allowing online submissions, the array should only have one element.                                                                                             If not allowing online submissions, your options are:                                                                                             "online_quiz"                                                                                             "none"                                                                                             "on_paper"                                                                                             "discussion_topic"                                                                                             "external_tool"                                                                                             If you are allowing online submissions, you can have one or many allowed submission types:                                                                                             "online_upload"                                                                                             "online_text_entry"                                                                                             "online_url"                                                                                             "media_recording" (Only valid when the Kaltura plugin is enabled)                                                                                             "student_annotation"                                                                                             Allowed values: online_quiz, none, on_paper, discussion_topic, external_tool, online_upload, online_text_entry, online_url, media_recording, student_annotation
            assignment[allowed_extensions][]                  |         |string             |Allowed extensions if submission_types includes `online_upload`                                                                                             Example:                                                                                             allowed_extensions: ["docx","ppt"]
            assignment[turnitin_enabled]                      |         |boolean            |Only applies when the Turnitin plugin is enabled for a course and the submission_types array includes `online_upload`. Toggles Turnitin submissions for the assignment. Will be ignored if Turnitin is not available for the course.
            assignment[vericite_enabled]                      |         |boolean            |Only applies when the VeriCite plugin is enabled for a course and the submission_types array includes `online_upload`. Toggles VeriCite submissions for the assignment. Will be ignored if VeriCite is not available for the course.
            assignment[turnitin_settings]                     |         |string             |Settings to send along to turnitin. See Assignment object definition for format.
            assignment[integration_data]                      |         |string             |Data used for SIS integrations. Requires admin-level token with the `Manage SIS` permission. JSON string required.
            assignment[integration_id]                        |         |string             |Unique ID from third party integrations
            assignment[peer_reviews]                          |         |boolean            |If submission_types does not include external_tool,discussion_topic, online_quiz, or on_paper, determines whether or not peer reviews will be turned on for the assignment.
            assignment[automatic_peer_reviews]                |         |boolean            |Whether peer reviews will be assigned automatically by Canvas or if teachers must manually assign peer reviews. Does not apply if peer reviews are not enabled.
            assignment[notify_of_update]                      |         |boolean            |If true, Canvas will send a notification to students in the class notifying them that the content has changed.
            assignment[group_category_id]                     |         |integer            |If present, the assignment will become a group assignment assigned to the group.
            assignment[grade_group_students_individually]     |         |integer            |If this is a group assignment, teachers have the options to grade students individually. If false, Canvas will apply the assignment’s score to each member of the group. If true, the teacher can manually assign scores to each member of the group.
            assignment[external_tool_tag_attributes]          |         |string             |Hash of external tool parameters if submission_types is [`external_tool`]. See Assignment object definition for format.
            assignment[points_possible]                       |         |number             |The maximum points possible on the assignment.
            assignment[grading_type]                          |         |string             |The strategy used for grading the assignment. The assignment defaults to `points` if this field is omitted.                                                                                             Allowed values: pass_fail, percent, letter_grade, gpa_scale, points, not_graded
            assignment[due_at]                                |         |DateTime           |The day/time the assignment is due. Must be between the lock dates if there are lock dates. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z.
            assignment[lock_at]                               |         |DateTime           |The day/time the assignment is locked after. Must be after the due date if there is a due date. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z.
            assignment[unlock_at]                             |         |DateTime           |The day/time the assignment is unlocked. Must be before the due date if there is a due date. Accepts times in ISO 8601 format, e.g. 2014-10-21T18:48:00Z.
            assignment[description]                           |         |string             |The assignment’s description, supports HTML.
            assignment[assignment_group_id]                   |         |integer            |The assignment group id to put the assignment in. Defaults to the top assignment group in the course.
            assignment[assignment_overrides][]                |         |AssignmentOverride |List of overrides for the assignment.
            assignment[only_visible_to_overrides]             |         |boolean            |Whether this assignment is only visible to overrides (Only useful if ‘differentiated assignments’ account setting is on)
            assignment[published]                             |         |boolean            |Whether this assignment is published. (Only useful if ‘draft state’ account setting is on) Unpublished assignments are not visible to students.
            assignment[grading_standard_id]                   |         |integer            |The grading standard id to set for the course.  If no value is provided for this argument the current grading_standard will be un-set from this course. This will update the grading_type for the course to ‘letter_grade’ unless it is already ‘gpa_scale’.
            assignment[omit_from_final_grade]                 |         |boolean            |Whether this assignment is counted towards a student’s final grade.
            assignment[hide_in_gradebook]                     |         |boolean            |Whether this assignment is shown in the gradebook.
            assignment[quiz_lti]                              |         |boolean            |Whether this assignment should use the Quizzes 2 LTI tool. Sets the submission type to ‘external_tool’ and configures the external tool attributes to use the Quizzes 2 LTI tool configured for this course. Has no effect if no Quizzes 2 LTI tool is configured.
            assignment[moderated_grading]                     |         |boolean            |Whether this assignment is moderated.
            assignment[grader_count]                          |         |integer            |The maximum number of provisional graders who may issue grades for this assignment. Only relevant for moderated assignments. Must be a positive value, and must be set to 1 if the course has fewer than two active instructors. Otherwise, the maximum value is the number of active instructors in the course minus one, or 10 if the course has more than 11 active instructors.
            assignment[final_grader_id]                       |         |integer            |The user ID of the grader responsible for choosing final grades for this assignment. Only relevant for moderated assignments.
            assignment[grader_comments_visible_to_graders]    |         |boolean            |Boolean indicating if provisional graders’ comments are visible to other provisional graders. Only relevant for moderated assignments.
            assignment[graders_anonymous_to_graders]          |         |boolean            |Boolean indicating if provisional graders’ identities are hidden from other provisional graders. Only relevant for moderated assignments.
            assignment[graders_names_visible_to_final_grader] |         |boolean            |Boolean indicating if provisional grader identities are visible to the the final grader. Only relevant for moderated assignments.
            assignment[anonymous_grading]                     |         |boolean            |Boolean indicating if the assignment is graded anonymously. If true, graders cannot see student identities.
            assignment[allowed_attempts]                      |         |integer            |The number of submission attempts allowed for this assignment. Set to -1 for unlimited attempts.
            assignment[annotatable_attachment_id]             |         |integer            |The Attachment ID of the document being annotated.                                                                                             Only applies when submission_types includes `student_annotation`.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:id

        
        Module: Assignments
        Function Description: Edit an assignment

        Parameter Desc:
            assignment[name]                                  | |string             |
            assignment[position]                              | |integer            |
            assignment[submission_types][]                    | |string             |
            assignment[allowed_extensions][]                  | |string             |
            assignment[turnitin_enabled]                      | |boolean            |
            assignment[vericite_enabled]                      | |boolean            |
            assignment[turnitin_settings]                     | |string             |
            assignment[sis_assignment_id]                     | |string             |
            assignment[integration_data]                      | |string             |
            assignment[integration_id]                        | |string             |
            assignment[peer_reviews]                          | |boolean            |
            assignment[automatic_peer_reviews]                | |boolean            |
            assignment[notify_of_update]                      | |boolean            |
            assignment[group_category_id]                     | |integer            |
            assignment[grade_group_students_individually]     | |integer            |
            assignment[external_tool_tag_attributes]          | |string             |
            assignment[points_possible]                       | |number             |
            assignment[grading_type]                          | |string             |
            assignment[due_at]                                | |DateTime           |
            assignment[lock_at]                               | |DateTime           |
            assignment[unlock_at]                             | |DateTime           |
            assignment[description]                           | |string             |
            assignment[assignment_group_id]                   | |integer            |
            assignment[assignment_overrides][]                | |AssignmentOverride |
            assignment[only_visible_to_overrides]             | |boolean            |
            assignment[published]                             | |boolean            |
            assignment[grading_standard_id]                   | |integer            |
            assignment[omit_from_final_grade]                 | |boolean            |
            assignment[hide_in_gradebook]                     | |boolean            |
            assignment[moderated_grading]                     | |boolean            |
            assignment[grader_count]                          | |integer            |
            assignment[final_grader_id]                       | |integer            |
            assignment[grader_comments_visible_to_graders]    | |boolean            |
            assignment[graders_anonymous_to_graders]          | |boolean            |
            assignment[graders_names_visible_to_final_grader] | |boolean            |
            assignment[anonymous_grading]                     | |boolean            |
            assignment[allowed_attempts]                      | |integer            |
            assignment[annotatable_attachment_id]             | |integer            |
            assignment[force_updated_at]                      | |boolean            |
            assignment[submission_types][]                    | |string             |[DEPRECATED]                                                                                     Effective 2021-05-26 (notice given 2021-02-18)
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{id}'
        return self.request(method, api, params)
        
    def bulk_update(self, course_id, params={}):
        """
        Source Code:
            Code: AssignmentsApiController#bulk_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/assignments_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.bulk_update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/bulk_update

        
        Module: Assignments
        Function Description: Bulk update assignment dates

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/bulk_update'
        return self.request(method, api, params)
        