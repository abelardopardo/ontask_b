from .etc.conf import *
from .res import *

class NewQuizItems(Res):
    def show(self, course_id, assignment_id, item_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.show
        
        Scope:
            url:GET|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items/:item_id

        
        Module: New Quiz Items
        Function Description: Get a quiz item

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |The id of the assignment associated with the quiz.
            item_id       |Required |integer |The id of the item associated with the quiz.
        """
        method = "GET"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items/{item_id}'
        return self.request(method, api, params)
        
    def index(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.index
        
        Scope:
            url:GET|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items

        
        Module: New Quiz Items
        Function Description: List quiz items

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |no description
        """
        method = "GET"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items'
        return self.request(method, api, params)
        
    def create(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.create
        
        Scope:
            url:POST|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items

        
        Module: New Quiz Items
        Function Description: Create a quiz item

        Parameter Desc:
            course_id                          |Required |integer |no description
            assignment_id                      |Required |integer |The id of the assignment associated with the quiz.
            item[position]                     |         |integer |The position of the item within the quiz.
            item[points_possible]              |         |number  |The number of points available to score on this item. Must be positive.
            item[entry_type]                   |Required |string  |The type of the item.                                                                   Allowed values: Item
            item[entry][title]                 |         |string  |The question title.
            item[entry][item_body]             |Required |string  |The question stem (rich content).
            item[entry][calculator_type]       |         |string  |Type of calculator the user will have access to during the question.                                                                   Allowed values: none, basic, scientific
            item[entry][feedback][neutral]     |         |string  |General feedback to show regardless of answer (rich content).
            item[entry][feedback][correct]     |         |string  |Feedback to show if the question is answered correctly (rich content).
            item[entry][feedback][incorrect]   |         |string  |Feedback to show if the question is answered incorrectly (rich content).
            item[entry][interaction_type_slug] |Required |string  |The type of question. One of ‘multi-answer’, ‘matching’, ‘categorization’, ‘file-upload’, ‘formula’, ‘ordering’, ‘rich-fill-blank’, ‘hot-spot’, ‘choice’, ‘numeric’, ‘true-false’, or ‘essay’. See Appendix: Question Types for more info about each type.
            item[entry][interaction_data]      |Required |Object  |An object that contains the question data. See Appendix: Question Types for more info about this field.
            item[entry][properties]            |         |Object  |An object that contains additional properties for some question types. See Appendix: Question Types for more info about this field.
            item[entry][scoring_data]          |Required |Object  |An object that describes how to score the question. See Appendix: Question Types for more info about this field.
            item[entry][answer_feedback]       |         |Object  |Feedback provided for each answer (rich content, only available on ‘choice’ question types).
            item[entry][scoring_algorithm]     |Required |string  |The algorithm used to score the question. See Appendix: Question Types for more info about this field.
        """
        method = "POST"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items'
        return self.request(method, api, params)
        
    def update(self, course_id, assignment_id, item_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.update
        
        Scope:
            url:PATCH|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items/:item_id

        
        Module: New Quiz Items
        Function Description: Update a quiz item

        Parameter Desc:
            course_id                          |Required |integer |no description
            assignment_id                      |Required |integer |The id of the assignment associated with the quiz.
            item_id                            |Required |integer |The id of the item associated with the quiz.
            item[position]                     |         |integer |The position of the item within the quiz.
            item[points_possible]              |         |number  |The number of points available to score on this item. Must be positive.
            item[entry_type]                   |         |string  |The type of the item.                                                                   Allowed values: Item
            item[entry][title]                 |         |string  |The question title.
            item[entry][item_body]             |         |string  |The question stem (rich content).
            item[entry][calculator_type]       |         |string  |Type of calculator the user will have access to during the question.                                                                   Allowed values: none, basic, scientific
            item[entry][feedback][neutral]     |         |string  |General feedback to show regardless of answer (rich content).
            item[entry][feedback][correct]     |         |string  |Feedback to show if the question is answered correctly (rich content).
            item[entry][feedback][incorrect]   |         |string  |Feedback to show if the question is answered incorrectly (rich content).
            item[entry][interaction_type_slug] |         |string  |The type of question. One of ‘multi-answer’, ‘matching’, ‘categorization’, ‘file-upload’, ‘formula’, ‘ordering’, ‘rich-fill-blank’, ‘hot-spot’, ‘choice’, ‘numeric’, ‘true-false’, or ‘essay’. See Appendix: Question Types for more info about each type.
            item[entry][interaction_data]      |         |Object  |An object that contains the question data. See Appendix: Question Types for more info about this field.
            item[entry][properties]            |         |Object  |An object that contains additional properties for some question types. See Appendix: Question Types for more info about this field.
            item[entry][scoring_data]          |         |Object  |An object that describes how to score the question. See Appendix: Question Types for more info about this field.
            item[entry][answer_feedback]       |         |Object  |Feedback provided for each answer (rich content, only available on ‘choice’ question types).
            item[entry][scoring_algorithm]     |         |string  |The algorithm used to score the question. See Appendix: Question Types for more info about this field.
        """
        method = "PATCH"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items/{item_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, assignment_id, item_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.destroy
        
        Scope:
            url:DELETE|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items/:item_id

        
        Module: New Quiz Items
        Function Description: Delete a quiz item

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |The id of the assignment associated with the quiz.
            item_id       |Required |integer |The id of the item associated with the quiz.
        """
        method = "DELETE"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items/{item_id}'
        return self.request(method, api, params)
        
    def media_upload_url(self, course_id, assignment_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.new_quizzes/quiz_items_api.media_upload_url
        
        Scope:
            url:GET|/api/quiz/v1/courses/:course_id/quizzes/:assignment_id/items/media_upload_url

        
        Module: New Quiz Items
        Function Description: Get items media_upload_url

        Parameter Desc:
            course_id     |Required |integer |no description
            assignment_id |Required |integer |no description

        Request Example: 
            curl 'https://<canvas>/api/quiz/v1/courses/1/quizzes/1/items/media_upload_url' \
                 -H 'Authorization Bearer <token>'

        Response Example: 
            { "url": "http://s3_upload_url" }
        """
        method = "GET"
        api = f'/api/quiz/v1/courses/{course_id}/quizzes/{assignment_id}/items/media_upload_url'
        return self.request(method, api, params)
        