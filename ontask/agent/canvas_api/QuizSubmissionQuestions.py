from .etc.conf import *
from .res import *

class QuizSubmissionQuestions(Res):
    def index(self, quiz_submission_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionQuestionsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_questions.index
        
        Scope:
            url:GET|/api/v1/quiz_submissions/:quiz_submission_id/questions

        
        Module: Quiz Submission Questions
        Function Description: Get all quiz submission questions.

        Parameter Desc:
            include[] | |string |Associations to include with the quiz submission question.                                 Allowed values: quiz_question

        Response Example: 
            {
              "quiz_submission_questions": [QuizSubmissionQuestion]
            }
        """
        method = "GET"
        api = f'/api/v1/quiz_submissions/{quiz_submission_id}/questions'
        return self.request(method, api, params)
        
    def answer(self, quiz_submission_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionQuestionsController#answer,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_questions.answer
        
        Scope:
            url:POST|/api/v1/quiz_submissions/:quiz_submission_id/questions

        
        Module: Quiz Submission Questions
        Function Description: Answering questions

        Parameter Desc:
            attempt          |Required |integer                |The attempt number of the quiz submission being taken. Note that this must be the latest attempt index, as questions for earlier attempts can not be modified.
            validation_token |Required |string                 |The unique validation token you received when the Quiz Submission was created.
            access_code      |         |string                 |Access code for the Quiz, if any.
            quiz_questions[] |         |QuizSubmissionQuestion |Set of question IDs and the answer value.                                                                See Appendix: Question Answer Formats for the accepted answer formats for each question type.
        """
        method = "POST"
        api = f'/api/v1/quiz_submissions/{quiz_submission_id}/questions'
        return self.request(method, api, params)
        
    def formatted_answer(self, quiz_submission_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionQuestionsController#formatted_answer,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_questions.formatted_answer
        
        Scope:
            url:GET|/api/v1/quiz_submissions/:quiz_submission_id/questions/:id/formatted_answer

        
        Module: Quiz Submission Questions
        Function Description: Get a formatted student numerical answer.

        Parameter Desc:
            answer |Required |Numeric |no description

        Response Example: 
            {
              "formatted_answer": 12.1234
            }
        """
        method = "GET"
        api = f'/api/v1/quiz_submissions/{quiz_submission_id}/questions/{id}/formatted_answer'
        return self.request(method, api, params)
        
    def flag(self, quiz_submission_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionQuestionsController#flag,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_questions.flag
        
        Scope:
            url:PUT|/api/v1/quiz_submissions/:quiz_submission_id/questions/:id/flag

        
        Module: Quiz Submission Questions
        Function Description: Flagging a question.

        Parameter Desc:
            attempt          |Required |integer |The attempt number of the quiz submission being taken. Note that this must be the latest attempt index, as questions for earlier attempts can not be modified.
            validation_token |Required |string  |The unique validation token you received when the Quiz Submission was created.
            access_code      |         |string  |Access code for the Quiz, if any.
        """
        method = "PUT"
        api = f'/api/v1/quiz_submissions/{quiz_submission_id}/questions/{id}/flag'
        return self.request(method, api, params)
        
    def unflag(self, quiz_submission_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizSubmissionQuestionsController#unflag,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_submission_questions_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_submission_questions.unflag
        
        Scope:
            url:PUT|/api/v1/quiz_submissions/:quiz_submission_id/questions/:id/unflag

        
        Module: Quiz Submission Questions
        Function Description: Unflagging a question.

        Parameter Desc:
            attempt          |Required |integer |The attempt number of the quiz submission being taken. Note that this must be the latest attempt index, as questions for earlier attempts can not be modified.
            validation_token |Required |string  |The unique validation token you received when the Quiz Submission was created.
            access_code      |         |string  |Access code for the Quiz, if any.
        """
        method = "PUT"
        api = f'/api/v1/quiz_submissions/{quiz_submission_id}/questions/{id}/unflag'
        return self.request(method, api, params)
        