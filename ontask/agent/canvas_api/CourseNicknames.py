from .etc.conf import *
from .res import *

class CourseNicknames(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: CourseNicknamesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_nicknames_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_nicknames.index
        
        Scope:
            url:GET|/api/v1/users/self/course_nicknames

        
        Module: Course Nicknames
        Function Description: List course nicknames

        """
        method = "GET"
        api = f'/api/v1/users/self/course_nicknames'
        return self.request(method, api, params)
        
    def show(self, course_id, params={}):
        """
        Source Code:
            Code: CourseNicknamesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_nicknames_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_nicknames.show
        
        Scope:
            url:GET|/api/v1/users/self/course_nicknames/:course_id

        
        Module: Course Nicknames
        Function Description: Get course nickname

        """
        method = "GET"
        api = f'/api/v1/users/self/course_nicknames/{course_id}'
        return self.request(method, api, params)
        
    def update(self, course_id, params={}):
        """
        Source Code:
            Code: CourseNicknamesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_nicknames_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_nicknames.update
        
        Scope:
            url:PUT|/api/v1/users/self/course_nicknames/:course_id

        
        Module: Course Nicknames
        Function Description: Set course nickname

        Parameter Desc:
            nickname |Required |string |The nickname to set.  It must be non-empty and shorter than 60 characters.
        """
        method = "PUT"
        api = f'/api/v1/users/self/course_nicknames/{course_id}'
        return self.request(method, api, params)
        
    def delete(self, course_id, params={}):
        """
        Source Code:
            Code: CourseNicknamesController#delete,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_nicknames_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_nicknames.delete
        
        Scope:
            url:DELETE|/api/v1/users/self/course_nicknames/:course_id

        
        Module: Course Nicknames
        Function Description: Remove course nickname

        """
        method = "DELETE"
        api = f'/api/v1/users/self/course_nicknames/{course_id}'
        return self.request(method, api, params)
        
    def clear(self, params={}):
        """
        Source Code:
            Code: CourseNicknamesController#clear,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/course_nicknames_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.course_nicknames.clear
        
        Scope:
            url:DELETE|/api/v1/users/self/course_nicknames

        
        Module: Course Nicknames
        Function Description: Clear course nicknames

        """
        method = "DELETE"
        api = f'/api/v1/users/self/course_nicknames'
        return self.request(method, api, params)
        