from .etc.conf import *
from .res import *

class CustomGradebookColumns(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_columns_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_columns_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/custom_gradebook_columns

        
        Module: Custom Gradebook Columns
        Function Description: List custom gradebook columns

        Parameter Desc:
            include_hidden | |boolean |Include hidden parameters (defaults to false)
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_columns_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_columns_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/custom_gradebook_columns

        
        Module: Custom Gradebook Columns
        Function Description: Create a custom gradebook column

        Parameter Desc:
            column[title]         |Required |string  |no description
            column[position]      |         |integer |The position of the column relative to other custom columns
            column[hidden]        |         |boolean |Hidden columns are not displayed in the gradebook
            column[teacher_notes] |         |boolean |Set this if the column is created by a teacher.  The gradebook only supports one teacher_notes column.
            column[read_only]     |         |boolean |Set this to prevent the column from being editable in the gradebook ui
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_columns_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_columns_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/custom_gradebook_columns/:id

        
        Module: Custom Gradebook Columns
        Function Description: Update a custom gradebook column

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_columns_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_columns_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/custom_gradebook_columns/:id

        
        Module: Custom Gradebook Columns
        Function Description: Delete a custom gradebook column

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns/{id}'
        return self.request(method, api, params)
        
    def reorder(self, course_id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnsApiController#reorder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_columns_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_columns_api.reorder
        
        Scope:
            url:POST|/api/v1/courses/:course_id/custom_gradebook_columns/reorder

        
        Module: Custom Gradebook Columns
        Function Description: Reorder custom columns

        Parameter Desc:
            order[] |Required |integer |no description
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns/reorder'
        return self.request(method, api, params)
        