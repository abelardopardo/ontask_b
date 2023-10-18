from .etc.conf import *
from .res import *

class CoursePace(Res):
    def api_show(self, course_id, id, params={}):
        """
        Source Code:
            Code: CoursePacesController#api_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_paces_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_paces.api_show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/course_pacing/:id

        
        Module: Course Pace
        Function Description: Show a Course pace

        Parameter Desc:
            course_id      |Required |integer |The id of the course
            course_pace_id |Required |integer |The id of the course_pace
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/course_pacing/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: CoursePacesController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_paces_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_paces.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/course_pacing

        
        Module: Course Pace
        Function Description: Create a Course pace

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/course_pacing'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: CoursePacesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_paces_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_paces.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/course_pacing/:id

        
        Module: Course Pace
        Function Description: Update a Course pace

        Parameter Desc:
            course_id                            |Required |integer  |The id of the course
            course_pace_id                       |Required |integer  |The id of the course pace
            end_date                             |         |Datetime |End date of the course pace
            exclude_weekends                     |         |boolean  |Course pace dates excludes weekends if true
            hard_end_dates                       |         |boolean  |Course pace uess hard end dates if true
            workflow_state                       |         |string   |The state of the course pace
            course_pace_module_item_attributes[] |         |string   |Module Items attributes
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/course_pacing/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: CoursePacesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_paces_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_paces.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/course_pacing/:id

        
        Module: Course Pace
        Function Description: Delete a Course pace

        Parameter Desc:
            course_id      |Required |integer |The id of the course
            course_pace_id |Required |integer |The id of the course_pace
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/course_pacing/{id}'
        return self.request(method, api, params)
        