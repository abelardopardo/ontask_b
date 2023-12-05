from .etc.conf import *
from .res import *

class CustomGradebookColumnData(Res):
    def index(self, course_id, id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnDataApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_column_data_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_column_data_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/custom_gradebook_columns/:id/data

        
        Module: Custom Gradebook Column Data
        Function Description: List entries for a column

        Parameter Desc:
            include_hidden | |boolean |If true, hidden columns will be included in the result. If false or absent, only visible columns will be returned.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns/{id}/data'
        return self.request(method, api, params)
        
    def update(self, course_id, id, user_id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnDataApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_column_data_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_column_data_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

        
        Module: Custom Gradebook Column Data
        Function Description: Update column data

        Parameter Desc:
            column_data[content] |Required |string |Column content.  Setting this to blank will delete the datum object.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_columns/{id}/data/{user_id}'
        return self.request(method, api, params)
        
    def bulk_update(self, course_id, params={}):
        """
        Source Code:
            Code: CustomGradebookColumnDataApiController#bulk_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/custom_gradebook_column_data_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.custom_gradebook_column_data_api.bulk_update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/custom_gradebook_column_data

        
        Module: Custom Gradebook Column Data
        Function Description: Bulk update column data

        Parameter Desc:
            column_data[] |Required |Array |Column content. Setting this to an empty string will delete the data object.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/custom_gradebook_column_data'
        return self.request(method, api, params)
        