from .etc.conf import *
from .res import *

class QuizQuestionGroups(Res):
    def show(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizGroupsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_groups.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/quizzes/:quiz_id/groups/:id

        
        Module: Quiz Question Groups
        Function Description: Get a single quiz group

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/groups/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, quiz_id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizGroupsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_groups.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/groups

        
        Module: Quiz Question Groups
        Function Description: Create a question group

        Parameter Desc:
            quiz_groups[][name]                        | |string  |The name of the question group.
            quiz_groups[][pick_count]                  | |integer |The number of questions to randomly select for this group.
            quiz_groups[][question_points]             | |integer |The number of points to assign to each question in the group.
            quiz_groups[][assessment_question_bank_id] | |integer |The id of the assessment question bank to pull questions from.

        Response Example: 
            {
              "quiz_groups": [QuizGroup]
            }
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/groups'
        return self.request(method, api, params)
        
    def update(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizGroupsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_groups.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/quizzes/:quiz_id/groups/:id

        
        Module: Quiz Question Groups
        Function Description: Update a question group

        Parameter Desc:
            quiz_groups[][name]            | |string  |The name of the question group.
            quiz_groups[][pick_count]      | |integer |The number of questions to randomly select for this group.
            quiz_groups[][question_points] | |integer |The number of points to assign to each question in the group.

        Response Example: 
            {
              "quiz_groups": [QuizGroup]
            }
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/groups/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizGroupsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_groups.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/quizzes/:quiz_id/groups/:id

        
        Module: Quiz Question Groups
        Function Description: Delete a question group

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/groups/{id}'
        return self.request(method, api, params)
        
    def reorder(self, course_id, quiz_id, id, params={}):
        """
        Source Code:
            Code: Quizzes::QuizGroupsController#reorder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/quizzes/quiz_groups_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quiz_groups.reorder
        
        Scope:
            url:POST|/api/v1/courses/:course_id/quizzes/:quiz_id/groups/:id/reorder

        
        Module: Quiz Question Groups
        Function Description: Reorder question groups

        Parameter Desc:
            order[][id]   |Required |integer |The associated item’s unique identifier
            order[][type] |         |string  |The type of item is always ‘question’ for a group                                              Allowed values: question
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/quizzes/{quiz_id}/groups/{id}/reorder'
        return self.request(method, api, params)
        