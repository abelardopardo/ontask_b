from .etc.conf import *
from .res import *

class Submissions(Res):
    def create(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: SubmissionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions
            url:POST|/api/v1/sections/:section_id/assignments/:assignment_id/submissions

        
        Module: Submissions
        Function Description: Submit an assignment

        Parameter Desc:
            comment[text_comment]                 |         |string   |Include a textual comment with the submission.
            submission[submission_type]           |Required |string   |The type of submission being made. The assignment submission_types must include this submission type as an allowed option, or the submission will be rejected with a 400 error.                                                                       The submission_type given determines which of the following parameters is used. For instance, to submit a URL, submission [submission_type] must be set to `online_url`, otherwise the submission [url] parameter will be ignored.                                                                       `basic_lti_launch` requires the assignment submission_type `online` or `external_tool`                                                                       Allowed values: online_text_entry, online_url, online_upload, media_recording, basic_lti_launch, student_annotation
            submission[body]                      |         |string   |Submit the assignment as an HTML document snippet. Note this HTML snippet will be sanitized using the same ruleset as a submission made from the Canvas web UI. The sanitized HTML will be returned in the response as the submission body. Requires a submission_type of `online_text_entry`.
            submission[url]                       |         |string   |Submit the assignment as a URL. The URL scheme must be `http` or `https`, no `ftp` or other URL schemes are allowed. If no scheme is given (e.g. `www.example.com`) then `http` will be assumed. Requires a submission_type of `online_url` or `basic_lti_launch`.
            submission[file_ids][]                |         |integer  |Submit the assignment as a set of one or more previously uploaded files residing in the submitting user’s files section (or the group’s files section, for group assignments).                                                                       To upload a new file to submit, see the submissions Upload a file API.                                                                       Requires a submission_type of `online_upload`.
            submission[media_comment_id]          |         |string   |The media comment id to submit. Media comment ids can be submitted via this API, however, note that there is not yet an API to generate or list existing media comments, so this functionality is currently of limited use.                                                                       Requires a submission_type of `media_recording`.
            submission[media_comment_type]        |         |string   |The type of media comment being submitted.                                                                       Allowed values: audio, video
            submission[user_id]                   |         |integer  |Submit on behalf of the given user. Requires grading permission.
            submission[annotatable_attachment_id] |         |integer  |The Attachment ID of the document being annotated. This should match the annotatable_attachment_id on the assignment.                                                                       Requires a submission_type of `student_annotation`.
            submission[submitted_at]              |         |DateTime |Choose the time the submission is listed as submitted at.  Requires grading permission.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions'
        return self.request(method, api, params)
        
    def index(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions

        
        Module: Submissions
        Function Description: List assignment submissions

        Parameter Desc:
            include[] | |string  |Associations to include with the group.  `group` will add group_id and group_name.                                  Allowed values: submission_history, submission_comments, rubric_assessment, assignment, visibility, course, user, group, read_status
            grouped   | |boolean |If this argument is true, the response will be grouped by student groups.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions'
        return self.request(method, api, params)
        
    def for_students(self, course_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#for_students,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.for_students
        
        Scope:
            url:GET|/api/v1/courses/:course_id/students/submissions
            url:GET|/api/v1/sections/:section_id/students/submissions

        
        Module: Submissions
        Function Description: List submissions for multiple assignments

        Parameter Desc:
            student_ids[]       | |string   |List of student ids to return submissions for. If this argument is omitted, return submissions for the calling user. Students may only list their own submissions. Observers may only list those of associated students. The special id `all` will return submissions for all students in the course/section as appropriate.
            assignment_ids[]    | |string   |List of assignments to return submissions for. If none are given, submissions for all assignments are returned.
            grouped             | |boolean  |If this argument is present, the response will be grouped by student, rather than a flat array of submissions.
            post_to_sis         | |boolean  |If this argument is set to true, the response will only include submissions for assignments that have the post_to_sis flag set to true and user enrollments that were added through sis.
            submitted_since     | |DateTime |If this argument is set, the response will only include submissions that were submitted after the specified date_time. This will exclude submissions that do not have a submitted_at which will exclude unsubmitted submissions. The value must be formatted as ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            graded_since        | |DateTime |If this argument is set, the response will only include submissions that were graded after the specified date_time. This will exclude submissions that have not been graded. The value must be formatted as ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            grading_period_id   | |integer  |The id of the grading period in which submissions are being requested (Requires grading periods to exist on the account)
            workflow_state      | |string   |The current status of the submission                                             Allowed values: submitted, unsubmitted, graded, pending_review
            enrollment_state    | |string   |The current state of the enrollments. If omitted will include all enrollments that are not deleted.                                             Allowed values: active, concluded
            state_based_on_date | |boolean  |If omitted it is set to true. When set to false it will ignore the effective state of the student enrollments and use the workflow_state for the enrollments. The argument is ignored unless enrollment_state argument is also passed.
            order               | |string   |The order submissions will be returned in.  Defaults to `id`.  Doesn’t affect results for `grouped` mode.                                             Allowed values: id, graded_at
            order_direction     | |string   |Determines whether ordered results are returned in ascending or descending order.  Defaults to `ascending`.  Doesn’t affect results for `grouped` mode.                                             Allowed values: ascending, descending
            include[]           | |string   |Associations to include with the group. ‘total_scores` requires the `grouped` argument.                                             Allowed values: submission_history, submission_comments, rubric_assessment, assignment, total_scores, visibility, course, user

        Response Example: 
            # Without grouped:
            
            [
              { "assignment_id": 100, grade: 5, "user_id": 1, ... },
              { "assignment_id": 101, grade: 6, "user_id": 2, ... }
            
            # With grouped:
            
            [
              {
                "user_id": 1,
                "submissions": [
                  { "assignment_id": 100, grade: 5, ... },
                  { "assignment_id": 101, grade: 6, ... }
                ]
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/students/submissions'
        return self.request(method, api, params)
        
    def show(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id

        
        Module: Submissions
        Function Description: Get a single submission

        Parameter Desc:
            include[] | |string |Associations to include with the group.                                 Allowed values: submission_history, submission_comments, rubric_assessment, full_rubric_assessment, visibility, course, user, read_status
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}'
        return self.request(method, api, params)
        
    def show_anonymous(self, course_id, assignment_id, anonymous_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#show_anonymous,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.show_anonymous
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/anonymous_submissions/:anonymous_id
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/anonymous_submissions/:anonymous_id

        
        Module: Submissions
        Function Description: Get a single submission by anonymous id

        Parameter Desc:
            include[] | |string |Associations to include with the group.                                 Allowed values: submission_history, submission_comments, rubric_assessment, full_rubric_assessment, visibility, course, user, read_status
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/anonymous_submissions/{anonymous_id}'
        return self.request(method, api, params)
        
    def create_file(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.create_file
        
        Scope:
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/files
            url:POST|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/files

        
        Module: Submissions
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/files'
        return self.request(method, api, params)
        
    def update(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id

        
        Module: Submissions
        Function Description: Grade or comment on a submission

        Parameter Desc:
            comment[text_comment]             | |string           |Add a textual comment to the submission.
            comment[attempt]                  | |integer          |The attempt number (starts at 1) to associate the comment with.
            comment[group_comment]            | |boolean          |Whether or not this comment should be sent to the entire group (defaults to false). Ignored if this is not a group assignment or if no text_comment is provided.
            comment[media_comment_id]         | |string           |Add an audio/video comment to the submission. Media comments can be added via this API, however, note that there is not yet an API to generate or list existing media comments, so this functionality is currently of limited use.
            comment[media_comment_type]       | |string           |The type of media comment being added.                                                                   Allowed values: audio, video
            comment[file_ids][]               | |integer          |Attach files to this comment that were previously uploaded using the Submission Comment API’s files action
            include[visibility]               | |string           |Whether this assignment is visible to the owner of the submission
            prefer_points_over_scheme         | |boolean          |Treat posted_grade as points if the value matches a grading scheme value
            submission[posted_grade]          | |string           |Assign a score to the submission, updating both the `score` and `grade` fields on the submission record. This parameter can be passed in a few different formats:                                                                   points                                                                   A floating point or integral value, such as `13.5`. The grade                                                                   will be interpreted directly as the score of the assignment.                                                                   Values above assignment.points_possible are allowed, for awarding                                                                   extra credit.                                                                   percentage                                                                   A floating point value appended with a percent sign, such as                                                                   "40%". The grade will be interpreted as a percentage score on the                                                                   assignment, where 100% == assignment.points_possible. Values above 100%                                                                   are allowed, for awarding extra credit.                                                                   letter grade                                                                   A letter grade, following the assignment’s defined letter                                                                   grading scheme. For example, "A-". The resulting score will be the high                                                                   end of the defined range for the letter grade. For instance, if "B" is                                                                   defined as 86% to 84%, a letter grade of "B" will be worth 86%. The                                                                   letter grade will be rejected if the assignment does not have a defined                                                                   letter grading scheme. For more fine-grained control of scores, pass in                                                                   points or percentage rather than the letter grade.                                                                   `pass/complete/fail/incomplete`                                                                   A string value of `pass` or `complete`                                                                   will give a score of 100%. "fail" or "incomplete" will give a score of                                                                   0.                                                                   Note that assignments with grading_type of `pass_fail` can only be assigned a score of 0 or assignment.points_possible, nothing inbetween. If a posted_grade in the `points` or `percentage` format is sent, the grade will only be accepted if the grade equals one of those two values.
            submission[excuse]                | |boolean          |Sets the `excused` status of an assignment.
            submission[late_policy_status]    | |string           |Sets the late policy status to either `late`, `missing`, `extended`, `none`, or null.                                                                   NB: "extended" values can only be set in the UI when the "UI features for 'extended' Submissions" Account Feature is on
            submission[seconds_late_override] | |integer          |Sets the seconds late if late policy status is `late`
            rubric_assessment                 | |RubricAssessment |Assign a rubric assessment to this assignment submission. The sub-parameters here depend on the rubric for the assignment. The general format is, for each row in the rubric:                                                                   The points awarded for this row.                                                                   rubric_assessment[criterion_id][points]                                                                   The rating id for the row.                                                                   rubric_assessment[criterion_id][rating_id]                                                                   Comments to add for this row.                                                                   rubric_assessment[criterion_id][comments]                                                                   For example, if the assignment rubric is (in JSON format):                                                                   [                                                                     {                                                                       'id': 'crit1',                                                                       'points': 10,                                                                       'description': 'Criterion 1',                                                                       'ratings':                                                                       [                                                                         { 'id': 'rat1', 'description': 'Good', 'points': 10 },                                                                         { 'id': 'rat2', 'description': 'Poor', 'points': 3 }                                                                       ]                                                                     },                                                                     {                                                                       'id': 'crit2',                                                                       'points': 5,                                                                       'description': 'Criterion 2',                                                                       'ratings':                                                                       [                                                                         { 'id': 'rat1', 'description': 'Exemplary', 'points': 5 },                                                                         { 'id': 'rat2', 'description': 'Complete', 'points': 5 },                                                                         { 'id': 'rat3', 'description': 'Incomplete', 'points': 0 }                                                                       ]                                                                     }                                                                   ]                                                                   Then a possible set of values for rubric_assessment would be:                                                                   rubric_assessment[crit1][points]=3&rubric_assessment[crit1][rating_id]=rat1&rubric_assessment[crit2][points]=5&rubric_assessment[crit2][rating_id]=rat2&rubric_assessment[crit2][comments]=Well%20Done.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}'
        return self.request(method, api, params)
        
    def update_anonymous(self, course_id, assignment_id, anonymous_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#update_anonymous,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.update_anonymous
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/anonymous_submissions/:anonymous_id
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/anonymous_submissions/:anonymous_id

        
        Module: Submissions
        Function Description: Grade or comment on a submission by anonymous id

        Parameter Desc:
            comment[text_comment]             | |string           |Add a textual comment to the submission.
            comment[group_comment]            | |boolean          |Whether or not this comment should be sent to the entire group (defaults to false). Ignored if this is not a group assignment or if no text_comment is provided.
            comment[media_comment_id]         | |string           |Add an audio/video comment to the submission. Media comments can be added via this API, however, note that there is not yet an API to generate or list existing media comments, so this functionality is currently of limited use.
            comment[media_comment_type]       | |string           |The type of media comment being added.                                                                   Allowed values: audio, video
            comment[file_ids][]               | |integer          |Attach files to this comment that were previously uploaded using the Submission Comment API’s files action
            include[visibility]               | |string           |Whether this assignment is visible to the owner of the submission
            submission[posted_grade]          | |string           |Assign a score to the submission, updating both the `score` and `grade` fields on the submission record. This parameter can be passed in a few different formats:                                                                   points                                                                   A floating point or integral value, such as `13.5`. The grade                                                                   will be interpreted directly as the score of the assignment.                                                                   Values above assignment.points_possible are allowed, for awarding                                                                   extra credit.                                                                   percentage                                                                   A floating point value appended with a percent sign, such as                                                                   "40%". The grade will be interpreted as a percentage score on the                                                                   assignment, where 100% == assignment.points_possible. Values above 100%                                                                   are allowed, for awarding extra credit.                                                                   letter grade                                                                   A letter grade, following the assignment’s defined letter                                                                   grading scheme. For example, "A-". The resulting score will be the high                                                                   end of the defined range for the letter grade. For instance, if "B" is                                                                   defined as 86% to 84%, a letter grade of "B" will be worth 86%. The                                                                   letter grade will be rejected if the assignment does not have a defined                                                                   letter grading scheme. For more fine-grained control of scores, pass in                                                                   points or percentage rather than the letter grade.                                                                   `pass/complete/fail/incomplete`                                                                   A string value of `pass` or `complete`                                                                   will give a score of 100%. "fail" or "incomplete" will give a score of                                                                   0.                                                                   Note that assignments with grading_type of `pass_fail` can only be assigned a score of 0 or assignment.points_possible, nothing inbetween. If a posted_grade in the `points` or `percentage` format is sent, the grade will only be accepted if the grade equals one of those two values.
            submission[excuse]                | |boolean          |Sets the `excused` status of an assignment.
            submission[late_policy_status]    | |string           |Sets the late policy status to either `late`, `missing`, `extended`, `none`, or null.                                                                   NB: "extended" values can only be set in the UI when the "UI features for 'extended' Submissions" Account Feature is on
            submission[seconds_late_override] | |integer          |Sets the seconds late if late policy status is `late`
            rubric_assessment                 | |RubricAssessment |Assign a rubric assessment to this assignment submission. The sub-parameters here depend on the rubric for the assignment. The general format is, for each row in the rubric:                                                                   The points awarded for this row.                                                                   rubric_assessment[criterion_id][points]                                                                   The rating id for the row.                                                                   rubric_assessment[criterion_id][rating_id]                                                                   Comments to add for this row.                                                                   rubric_assessment[criterion_id][comments]                                                                   For example, if the assignment rubric is (in JSON format):                                                                   [                                                                     {                                                                       'id': 'crit1',                                                                       'points': 10,                                                                       'description': 'Criterion 1',                                                                       'ratings':                                                                       [                                                                         { 'id': 'rat1', 'description': 'Good', 'points': 10 },                                                                         { 'id': 'rat2', 'description': 'Poor', 'points': 3 }                                                                       ]                                                                     },                                                                     {                                                                       'id': 'crit2',                                                                       'points': 5,                                                                       'description': 'Criterion 2',                                                                       'ratings':                                                                       [                                                                         { 'id': 'rat1', 'description': 'Exemplary', 'points': 5 },                                                                         { 'id': 'rat2', 'description': 'Complete', 'points': 5 },                                                                         { 'id': 'rat3', 'description': 'Incomplete', 'points': 0 }                                                                       ]                                                                     }                                                                   ]                                                                   Then a possible set of values for rubric_assessment would be:                                                                   rubric_assessment[crit1][points]=3&rubric_assessment[crit1][rating_id]=rat1&rubric_assessment[crit2][points]=5&rubric_assessment[crit2][rating_id]=rat2&rubric_assessment[crit2][comments]=Well%20Done.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/anonymous_submissions/{anonymous_id}'
        return self.request(method, api, params)
        
    def gradeable_students(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#gradeable_students,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.gradeable_students
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/gradeable_students

        
        Module: Submissions
        Function Description: List gradeable students

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/gradeable_students'
        return self.request(method, api, params)
        
    def multiple_gradeable_students(self, course_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#multiple_gradeable_students,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.multiple_gradeable_students
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/gradeable_students

        
        Module: Submissions
        Function Description: List multiple assignments gradeable students

        Parameter Desc:
            assignment_ids[] | |string |Assignments being requested

        Response Example: 
            A [UserDisplay] with an extra assignment_ids field to indicate what assignments
            that user can submit
            
            [
              {
                "id": 2,
                "display_name": "Display Name",
                "avatar_image_url": "http://avatar-image-url.jpeg",
                "html_url": "http://canvas.com",
                "assignment_ids": [1, 2, 3]
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/gradeable_students'
        return self.request(method, api, params)
        
    def bulk_update(self, course_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#bulk_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.bulk_update
        
        Scope:
            url:POST|/api/v1/courses/:course_id/submissions/update_grades
            url:POST|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/update_grades
            url:POST|/api/v1/sections/:section_id/submissions/update_grades
            url:POST|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/update_grades

        
        Module: Submissions
        Function Description: Grade or comment on multiple submissions

        Parameter Desc:
            grade_data[<student_id>][posted_grade]       | |string           |See documentation for the posted_grade argument in the Submissions Update documentation
            grade_data[<student_id>][excuse]             | |boolean          |See documentation for the excuse argument in the Submissions Update documentation
            grade_data[<student_id>][rubric_assessment]  | |RubricAssessment |See documentation for the rubric_assessment argument in the Submissions Update documentation
            grade_data[<student_id>][text_comment]       | |string           |no description
            grade_data[<student_id>][group_comment]      | |boolean          |no description
            grade_data[<student_id>][media_comment_id]   | |string           |no description
            grade_data[<student_id>][media_comment_type] | |string           |no description                                                                              Allowed values: audio, video
            grade_data[<student_id>][file_ids][]         | |integer          |See documentation for the comment[] arguments in the Submissions Update documentation
            grade_data[<assignment_id>][<student_id>]    | |integer          |Specifies which assignment to grade.  This argument is not necessary when using the assignment-specific endpoints.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/submissions/update_grades'
        return self.request(method, api, params)
        
    def mark_submission_read(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_submission_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_submission_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/read
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/read

        
        Module: Submissions
        Function Description: Mark submission as read

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/read'
        return self.request(method, api, params)
        
    def mark_submission_unread(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_submission_unread,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_submission_unread
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/read
            url:DELETE|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/read

        
        Module: Submissions
        Function Description: Mark submission as unread

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/read'
        return self.request(method, api, params)
        
    def mark_bulk_submissions_as_read(self, course_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_bulk_submissions_as_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_bulk_submissions_as_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/submissions/bulk_mark_read
            url:PUT|/api/v1/sections/:section_id/submissions/bulk_mark_read

        
        Module: Submissions
        Function Description: Mark bulk submissions as read

        Parameter Desc:
            submissionIds[] | |string |no description
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/submissions/bulk_mark_read'
        return self.request(method, api, params)
        
    def mark_submission_item_read(self, course_id, assignment_id, user_id, item, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_submission_item_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_submission_item_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/read/:item
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/read/:item

        
        Module: Submissions
        Function Description: Mark submission item as read

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/read/{item}'
        return self.request(method, api, params)
        
    def submissions_clear_unread(self, course_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#submissions_clear_unread,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.submissions_clear_unread
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/submissions/:user_id/clear_unread
            url:PUT|/api/v1/sections/:section_id/submissions/:user_id/clear_unread

        
        Module: Submissions
        Function Description: Clear unread status for all submissions.

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/submissions/{user_id}/clear_unread'
        return self.request(method, api, params)
        
    def rubric_assessments_read_state(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#rubric_assessments_read_state,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.rubric_assessments_read_state
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/rubric_comments/read
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/rubric_assessments/read
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/rubric_comments/read
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/rubric_assessments/read

        
        Module: Submissions
        Function Description: Get rubric assessments read state


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/rubric_comments/read' \
                 -H "Authorization: Bearer <token>"
            
            # or
            
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/rubric_assessments/read' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            {
              "read": false
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/rubric_comments/read'
        return self.request(method, api, params)
        
    def mark_rubric_assessments_read(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_rubric_assessments_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_rubric_assessments_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/rubric_comments/read
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/rubric_assessments/read
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/rubric_comments/read
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/rubric_assessments/read

        
        Module: Submissions
        Function Description: Mark rubric assessments as read


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/rubric_comments/read' \
                 -X PUT \
                 -H "Authorization: Bearer <token>" \
                 -H "Content-Length: 0"
            
            # or
            
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/rubric_assessments/read' \
                 -X PUT \
                 -H "Authorization: Bearer <token>" \
                 -H "Content-Length: 0"

        Response Example: 
            {
              "read": true
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/rubric_comments/read'
        return self.request(method, api, params)
        
    def document_annotations_read_state(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#document_annotations_read_state,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.document_annotations_read_state
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/document_annotations/read
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/document_annotations/read

        
        Module: Submissions
        Function Description: Get document annotations read state


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/document_annotations/read' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            {
              "read": false
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/document_annotations/read'
        return self.request(method, api, params)
        
    def mark_document_annotations_read(self, course_id, assignment_id, user_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#mark_document_annotations_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.mark_document_annotations_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id/document_annotations/read
            url:PUT|/api/v1/sections/:section_id/assignments/:assignment_id/submissions/:user_id/document_annotations/read

        
        Module: Submissions
        Function Description: Mark document annotations as read


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/assignments/<assignment_id>/submissions/<user_id>/document_annotations/read' \
                 -X PUT \
                 -H "Authorization: Bearer <token>" \
                 -H "Content-Length: 0"

        Response Example: 
            {
              "read": true
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/document_annotations/read'
        return self.request(method, api, params)
        
    def submission_summary(self, course_id, assignment_id, params={}):
        """
        Source Code:
            Code: SubmissionsApiController#submission_summary,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/submissions_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.submissions_api.submission_summary
        
        Scope:
            url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submission_summary
            url:GET|/api/v1/sections/:section_id/assignments/:assignment_id/submission_summary

        
        Module: Submissions
        Function Description: Submission Summary

        Parameter Desc:
            grouped | |boolean |If this argument is true, the response will take into account student groups.

        Response Example: 
            {
              "graded": 5,
              "ungraded": 10,
              "not_submitted": 42
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/assignments/{assignment_id}/submission_summary'
        return self.request(method, api, params)
        