from .etc.conf import *
from .res import *

class Quizzes(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes

        
        Module: Quizzes
        Function Description: List quizzes in a course

        Parameter Desc:
            search_term | |string |The partial title of the quizzes to match and return.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:id

        
        Module: Quizzes
        Function Description: Get a single quiz

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes

        
        Module: Quizzes
        Function Description: Create a quiz

        Parameter Desc:
            quiz[title]                             |Required |string   |The quiz title.
            quiz[description]                       |         |string   |A description of the quiz.
            quiz[quiz_type]                         |         |string   |The type of quiz.    Allowed values: practice_quiz, assignment, graded_survey, survey
            quiz[assignment_group_id]               |         |integer  |The assignment group id to put the assignment in. Defaults to the top assignment group in the course. Only valid if the quiz is graded, i.e. if quiz_type is `assignment` or `graded_survey`.
            quiz[time_limit]                        |         |integer  |Time limit to take this quiz, in minutes. Set to null for no time limit. Defaults to null.
            quiz[shuffle_answers]                   |         |boolean  |If true, quiz answers for multiple choice questions will be randomized for each student. Defaults to false.
            quiz[hide_results]                      |         |string   |Dictates whether or not quiz results are hidden from students. If null, students can see their results after any attempt. If `always`, students can never see their results. If `until_after_last_attempt`, students can only see results after their last attempt. (Only valid if allowed_attempts > 1). Defaults to null.                                                                         Allowed values: always, until_after_last_attempt
            quiz[show_correct_answers]              |         |boolean  |Only valid if hide_results=null If false, hides correct answers from students when quiz results are viewed. Defaults to true.
            quiz[show_correct_answers_last_attempt] |         |boolean  |Only valid if show_correct_answers=true and allowed_attempts > 1 If true, hides correct answers from students when quiz results are viewed until they submit the last attempt for the quiz. Defaults to false.
            quiz[show_correct_answers_at]           |         |DateTime |Only valid if show_correct_answers=true If set, the correct answers will be visible by students only after this date, otherwise the correct answers are visible once the student hands in their quiz submission.
            quiz[hide_correct_answers_at]           |         |DateTime |Only valid if show_correct_answers=true If set, the correct answers will stop being visible once this date has passed. Otherwise, the correct answers will be visible indefinitely.
            quiz[allowed_attempts]                  |         |integer  |Number of times a student is allowed to take a quiz. Set to -1 for unlimited attempts. Defaults to 1.
            quiz[scoring_policy]                    |         |string   |Required and only valid if allowed_attempts > 1. Scoring policy for a quiz that students can take multiple times. Defaults to `keep_highest`.                                                                         Allowed values: keep_highest, keep_latest
            quiz[one_question_at_a_time]            |         |boolean  |If true, shows quiz to student one question at a time. Defaults to false.
            quiz[cant_go_back]                      |         |boolean  |Only valid if one_question_at_a_time=true If true, questions are locked after answering. Defaults to false.
            quiz[access_code]                       |         |string   |Restricts access to the quiz with a password. For no access code restriction, set to null. Defaults to null.
            quiz[ip_filter]                         |         |string   |Restricts access to the quiz to computers in a specified IP range. Filters can be a comma-separated list of addresses, or an address followed by a mask                                                                         Examples:                                                                         "192.168.217.1"                                                                         "192.168.217.1/24"                                                                         "192.168.217.1/255.255.255.0"                                                                         For no IP filter restriction, set to null. Defaults to null.
            quiz[due_at]                            |         |DateTime |The day/time the quiz is due. Accepts times in ISO 8601 format, e.g. 2011-10-21T18:48Z.
            quiz[lock_at]                           |         |DateTime |The day/time the quiz is locked for students. Accepts times in ISO 8601 format, e.g. 2011-10-21T18:48Z.
            quiz[unlock_at]                         |         |DateTime |The day/time the quiz is unlocked for students. Accepts times in ISO 8601 format, e.g. 2011-10-21T18:48Z.
            quiz[published]                         |         |boolean  |Whether the quiz should have a draft state of published or unpublished. NOTE: If students have started taking the quiz, or there are any submissions for the quiz, you may not unpublish a quiz and will recieve an error.
            quiz[one_time_results]                  |         |boolean  |Whether students should be prevented from viewing their quiz results past the first time (right after they turn the quiz in.) Only valid if `hide_results` is not set to `always`. Defaults to false.
            quiz[only_visible_to_overrides]         |         |boolean  |Whether this quiz is only visible to overrides (Only useful if ‘differentiated assignments’ account setting is on) Defaults to false.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/quizzes/:id

        
        Module: Quizzes
        Function Description: Edit a quiz

        Parameter Desc:
            quiz[notify_of_update] | |boolean |If true, notifies users that the quiz has changed. Defaults to true
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/quizzes/:id

        
        Module: Quizzes
        Function Description: Delete a quiz

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}'
        return self.request(method, api, params)
        
    def reorder(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#reorder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.reorder
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:id/reorder

        
        Module: Quizzes
        Function Description: Reorder quiz items

        Parameter Desc:
            order[][id]   |Required |integer |The associated item’s unique identifier
            order[][type] |         |string  |The type of item is either ‘question’ or ‘group’                                              Allowed values: question, group
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}/reorder'
        return self.request(method, api, params)
        
    def validate_access_code(self, course_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizzesApiController#validate_access_code,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quizzes_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.validate_access_code
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:id/validate_access_code

        
        Module: Quizzes
        Function Description: Validate quiz access code

        Parameter Desc:
            access_code |Required |string |The access code being validated
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{id}/validate_access_code'
        return self.request(method, api, params)
        