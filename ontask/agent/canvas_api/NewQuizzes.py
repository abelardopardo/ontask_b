from .etc.conf import *
from .res import *

class NewQuizzes(Res):
    def show(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quizzes_api.show
        
        Scope:
            url:GET|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id

        
        Module: New Quizzes
        Function Description: Get a new quiz

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |The id of the assignment associated with the quiz.
        """
        method = "GET"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}'
        return self.request(method, api, params)
        
    def index(self, course_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quizzes_api.index
        
        Scope:
            url:GET|/api/quiz/v1/courses/:course_id/quizzes

        
        Module: New Quizzes
        Function Description: List new quizzes

        Parameter Desc:
            course_id |Required |integer |no description
        """
        method = "GET"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quizzes_api.create
        
        Scope:
            url:POST|/api/quiz/v1/courses/:course_id/quizzes

        
        Module: New Quizzes
        Function Description: Create a new quiz

        Parameter Desc:
            course_id                                                                     |Required |integer          |no description
            quiz[title]                                                                   |         |string           |The title of the quiz.
            quiz[assignment_group_id]                                                     |         |integer          |The ID of the quiz’s assignment group.
            quiz[points_possible]                                                         |         |number           |The total point value given to the quiz. Must be positive.
            quiz[due_at]                                                                  |         |DateTime         |When the quiz is due.
            quiz[lock_at]                                                                 |         |DateTime         |When to lock the quiz.
            quiz[unlock_at]                                                               |         |DateTime         |When to unlock the quiz.
            quiz[grading_type]                                                            |         |string           |The type of grading the assignment receives.                                                                                                                       Allowed values: pass_fail, percent, letter_grade, gpa_scale, points
            quiz[instructions]                                                            |         |string           |Instructions for the quiz.
            quiz[quiz_settings][calculator_type]                                          |         |string           |Specifies which type of Calculator a student can use during Quiz taking. Should be null if no calculator is allowed.                                                                                                                       Allowed values: none, basic, scientific
            quiz[quiz_settings][filter_ip_address]                                        |         |boolean          |Whether IP filtering is needed.  Must be true for filters to take effect.
            quiz[quiz_settings][filters][ips][]                                           |         |string           |Specifies ranges of IP addresses where the quiz can be taken from. Each range is an array like [start address, end address], or null if there’s no restriction.
            quiz[quiz_settings][multiple_attempts][multiple_attempts_enabled]             |         |boolean          |Whether multiple attempts for this quiz is true.
            quiz[quiz_settings][multiple_attempts][attempt_limit]                         |         |boolean          |Whether there is an attempt limit.  Only set if multiple_attempts_enabled is true.
            quiz[quiz_settings][multiple_attempts][max_attempts]                          |         |Positive Integer |The allowed attempts a student can take. If null, the allowed attempts are unlimited.  Only used if attempt_limit is true.
            quiz[quiz_settings][multiple_attempts][score_to_keep]                         |         |string           |Whichever score to keep for the attempts.  Only used if multiple_attempts_enabled is true.                                                                                                                       Allowed values: average, first, highest, latest
            quiz[quiz_settings][multiple_attempts][cooling_period]                        |         |boolean          |Whether there is a cooling (waiting) period.  Only used if multiple_attempts_enabled is true.
            quiz[quiz_settings][multiple_attempts][cooling_period_in_seconds]             |         |Positive Integer |Required waiting period in seconds between attempts. If null, there is no required time. Only used if cooling_period is true
            quiz[quiz_settings][one_at_a_time_type]                                       |         |string           |Specifies the settings for questions to display when quiz taking.                                                                                                                       Allowed values: none, question
            quiz[quiz_settings][allow_backtracking]                                       |         |boolean          |Whether to allow user to return to previous questions when ‘one_at_a_time_type’ is set to ‘question’.
            quiz[quiz_settings][results_view_settings][result_view_restricted]            |         |boolean          |Whether the results view is restricted for students.  Must be true for any student restrictions to be set
            quiz[quiz_settings][results_view_settings][display_points_awarded]            |         |boolean          |Whether points are shown. Must set result_view_restricted to true to use this parameter.
            quiz[quiz_settings][results_view_settings][display_points_possible]           |         |boolean          |Whether points possible is shown. Must set result_view_restricted to true to use this parameter.
            quiz[quiz_settings][results_view_settings][display_items]                     |         |boolean          |Whether to show items in the results view.  Must be true for any items restrictions to be set
            quiz[quiz_settings][results_view_settings][display_item_response]             |         |boolean          |Whether item response is shown.  Only set if display_items is true.  Must be true for display_item_response_correctness to be set.
            quiz[quiz_settings][results_view_settings][display_item_response_correctness] |         |boolean          |Whether item correctness is shown.  Only set if display_item_response is true.  Must be true for display_item_correct_answer to be set.
            quiz[quiz_settings][results_view_settings][display_item_correct_answer]       |         |boolean          |Whether correct answer is shown.  Only set if display_item_response_correctness is true
            quiz[quiz_settings][results_view_settings][display_item_feedback]             |         |boolean          |Whether Item feedback is shown.  Only set if display_items is true
            quiz[quiz_settings][shuffle_answers]                                          |         |boolean          |Whether answers should be shuffled for students.
            quiz[quiz_settings][shuffle_questions]                                        |         |boolean          |Whether questions should be shuffled for students.
            quiz[quiz_settings][require_student_access_code]                              |         |boolean          |Whether an access code is needed to take the quiz.
            quiz[quiz_settings][student_access_code]                                      |         |string           |Access code to restrict quiz access. Should be null if no restriction.
            quiz[quiz_settings][has_time_limit]                                           |         |boolean          |Whether there is a time limit for the quiz.
            quiz[quiz_settings][session_time_limit_in_seconds]                            |         |Positive Integer |Limit the time a student can work on the quiz. Should be null if no restriction.
        """
        method = "POST"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes'
        return self.request(method, api, params)
        
    def update(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quizzes_api.update
        
        Scope:
            url:PATCH|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id

        
        Module: New Quizzes
        Function Description: Update a single quiz

        Parameter Desc:
            course_id                                                                     |Required |integer          |no description
            assignment_id                                                                 |Required |integer          |The id of the assignment associated with the quiz.
            quiz[title]                                                                   |         |string           |The title of the quiz.
            quiz[assignment_group_id]                                                     |         |integer          |The ID of the quiz’s assignment group.
            quiz[points_possible]                                                         |         |number           |The total point value given to the quiz. Must be positive.
            quiz[due_at]                                                                  |         |DateTime         |When the quiz is due.
            quiz[lock_at]                                                                 |         |DateTime         |When to lock the quiz.
            quiz[unlock_at]                                                               |         |DateTime         |When to unlock the quiz.
            quiz[grading_type]                                                            |         |string           |The type of grading the assignment receives.                                                                                                                       Allowed values: pass_fail, percent, letter_grade, gpa_scale, points
            quiz[instructions]                                                            |         |string           |Instructions for the quiz.
            quiz[quiz_settings][calculator_type]                                          |         |string           |Specifies which type of Calculator a student can use during Quiz taking. Should be null if no calculator is allowed.                                                                                                                       Allowed values: none, basic, scientific
            quiz[quiz_settings][filter_ip_address]                                        |         |boolean          |Whether IP filtering is needed. Must be true for filters to take effect.
            quiz[quiz_settings][filters][ips][]                                           |         |string           |Specifies ranges of IP addresses where the quiz can be taken from. Each range is an array like [start address, end address], or null if there’s no restriction. Specifies the range of IP addresses where the quiz can be taken from. Should be null if there’s no restriction.
            quiz[quiz_settings][multiple_attempts][multiple_attempts_enabled]             |         |boolean          |Whether multiple attempts for this quiz is true.
            quiz[quiz_settings][multiple_attempts][attempt_limit]                         |         |boolean          |Whether there is an attempt limit.  Only set if multiple_attempts_enabled is true.
            quiz[quiz_settings][multiple_attempts][max_attempts]                          |         |Positive Integer |The allowed attempts a student can take. If null, the allowed attempts are unlimited. Only used if attempt_limit is true.
            quiz[quiz_settings][multiple_attempts][score_to_keep]                         |         |string           |Whichever score to keep for the attempts. Only used if multiple_attempts_enabled is true.                                                                                                                       Allowed values: average, first, highest, latest
            quiz[quiz_settings][multiple_attempts][cooling_period]                        |         |boolean          |Whether there is a cooling period. Only used if multiple_attempts_enabled is true.
            quiz[quiz_settings][multiple_attempts][cooling_period_in_seconds]             |         |Positive Integer |Required waiting period in seconds between attempts. If null, there is no required time.  Only used if cooling_period is true.
            quiz[quiz_settings][one_at_a_time_type]                                       |         |string           |Specifies the settings for questions to display when quiz taking.                                                                                                                       Allowed values: none, question
            quiz[quiz_settings][allow_backtracking]                                       |         |boolean          |Whether to allow user to return to previous questions when ‘one_at_a_time_type’ is set to ‘question’.
            quiz[quiz_settings][results_view_settings][result_view_restricted]            |         |boolean          |Whether the results view is restricted for students.
            quiz[quiz_settings][results_view_settings][display_points_awarded]            |         |boolean          |Whether points are shown.  Must set result_view_restricted to true to use this parameter.
            quiz[quiz_settings][results_view_settings][display_points_possible]           |         |boolean          |Whether points possible is shown. Must set result_view_restricted to true to use this parameter.
            quiz[quiz_settings][results_view_settings][display_items]                     |         |boolean          |Whether to show items in the results view.  Must be true for any items restrictions to be set.
            quiz[quiz_settings][results_view_settings][display_item_response]             |         |boolean          |Whether item response is shown.  Only set if display_items is true.  Must be true for display_item_response_correctness to be set.
            quiz[quiz_settings][results_view_settings][display_item_response_correctness] |         |boolean          |Whether item correctness is shown.  Only set if display_item_response is true.  Must be true for display_item_correct_answer to be set.
            quiz[quiz_settings][results_view_settings][display_item_correct_answer]       |         |boolean          |Whether correct answer is shown.  Only set if display_item_response_correctness is true.
            quiz[quiz_settings][results_view_settings][display_item_feedback]             |         |boolean          |Whether Item feedback is shown. Only set if display_items is true.
            quiz[quiz_settings][shuffle_answers]                                          |         |boolean          |Whether answers should be shuffled for students.
            quiz[quiz_settings][shuffle_questions]                                        |         |boolean          |Whether questions should be shuffled for students.
            quiz[quiz_settings][require_student_access_code]                              |         |boolean          |Whether an access code is needed to take the quiz.
            quiz[quiz_settings][student_access_code]                                      |         |string           |Access code to restrict quiz access. Should be null if no restriction.
            quiz[quiz_settings][has_time_limit]                                           |         |boolean          |Whether there is a time limit for the quiz.
            quiz[quiz_settings][session_time_limit_in_seconds]                            |         |Positive Integer |Limit the time a student can work on the quiz. Should be null if no restriction.
        """
        method = "PATCH"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quizzes_api.destroy
        
        Scope:
            url:DELETE|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id

        
        Module: New Quizzes
        Function Description: Delete a new quiz

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |The id of the assignment associated with the quiz.
        """
        method = "DELETE"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}'
        return self.request(method, api, params)
        