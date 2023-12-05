from .etc.conf import *
from .res import *

class QuizQuestions(Res):
    def index(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizQuestionsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_questions.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/questions

        
        Module: Quiz Questions
        Function Description: List questions in a quiz or a submission

        Parameter Desc:
            quiz_submission_id      | |integer |If specified, the endpoint will return the questions that were presented for that submission. This is useful if the quiz has been modified after the submission was created and the latest quiz version’s set of questions does not match the submission’s. NOTE: you must specify quiz_submission_attempt as well if you specify this parameter.
            quiz_submission_attempt | |integer |The attempt of the submission you want the questions for.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions'
        return self.request(method, api, params)
        
    def show(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizQuestionsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_questions.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/questions/:id

        
        Module: Quiz Questions
        Function Description: Get a single quiz question

        Parameter Desc:
            id |Required |integer |The quiz question unique identifier.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizQuestionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_questions.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/questions

        
        Module: Quiz Questions
        Function Description: Create a single quiz question

        Parameter Desc:
            question[question_name]      | |string   |The name of the question.
            question[question_text]      | |string   |The text of the question.
            question[quiz_group_id]      | |integer  |The id of the quiz group to assign the question to.
            question[question_type]      | |string   |The type of question. Multiple optional fields depend upon the type of question to be used.                                                      Allowed values: calculated_question, essay_question, file_upload_question, fill_in_multiple_blanks_question, matching_question, multiple_answers_question, multiple_choice_question, multiple_dropdowns_question, numerical_question, short_answer_question, text_only_question, true_false_question
            question[position]           | |integer  |The order in which the question will be displayed in the quiz in relation to other questions.
            question[points_possible]    | |integer  |The maximum amount of points received for answering this question correctly.
            question[correct_comments]   | |string   |The comment to display if the student answers the question correctly.
            question[incorrect_comments] | |string   |The comment to display if the student answers incorrectly.
            question[neutral_comments]   | |string   |The comment to display regardless of how the student answered.
            question[text_after_answers] | |string   |no description
            question[answers]            | |[Answer] |no description
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions'
        return self.request(method, api, params)
        
    def update(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizQuestionsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_questions.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/quizzes/:quiz_id/questions/:id

        
        Module: Quiz Questions
        Function Description: Update an existing quiz question

        Parameter Desc:
            quiz_id                      |Required |integer  |The associated quiz’s unique identifier.
            id                           |Required |integer  |The quiz question’s unique identifier.
            question[question_name]      |         |string   |The name of the question.
            question[question_text]      |         |string   |The text of the question.
            question[quiz_group_id]      |         |integer  |The id of the quiz group to assign the question to.
            question[question_type]      |         |string   |The type of question. Multiple optional fields depend upon the type of question to be used.                                                              Allowed values: calculated_question, essay_question, file_upload_question, fill_in_multiple_blanks_question, matching_question, multiple_answers_question, multiple_choice_question, multiple_dropdowns_question, numerical_question, short_answer_question, text_only_question, true_false_question
            question[position]           |         |integer  |The order in which the question will be displayed in the quiz in relation to other questions.
            question[points_possible]    |         |integer  |The maximum amount of points received for answering this question correctly.
            question[correct_comments]   |         |string   |The comment to display if the student answers the question correctly.
            question[incorrect_comments] |         |string   |The comment to display if the student answers incorrectly.
            question[neutral_comments]   |         |string   |The comment to display regardless of how the student answered.
            question[text_after_answers] |         |string   |no description
            question[answers]            |         |[Answer] |no description
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizQuestionsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_questions.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/quizzes/:quiz_id/questions/:id

        
        Module: Quiz Questions
        Function Description: Delete a quiz question

        Parameter Desc:
            quiz_id |Required |integer |The associated quiz’s unique identifier
            id      |Required |integer |The quiz question’s unique identifier
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{id}'
        return self.request(method, api, params)
        