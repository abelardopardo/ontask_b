from .etc.conf import *
from .res import *

class Modules(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/modules

        
        Module: Modules
        Function Description: List modules

        Parameter Desc:
            include[]   | |string |`items`: Return module items inline if possible. This parameter suggests that Canvas return module items directly in the Module object JSON, to avoid having to make separate API requests for each module when enumerating modules and items. Canvas is free to omit ‘items’ for any particular module if it deems them too numerous to return inline. Callers must be prepared to use the List Module Items API if items are not returned.                                   `content_details`: Requires ‘items’. Returns additional details with module items specific to their associated content items. Includes standard lock information for each item.                                   Allowed values: items, content_details
            search_term | |string |The partial name of the modules (and module items, if ‘items’ is specified with include[]) to match and return.
            student_id  | |string |Returns module completion information for the student with this id.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/modules'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/modules/:id

        
        Module: Modules
        Function Description: Show module

        Parameter Desc:
            include[]  | |string |`items`: Return module items inline if possible. This parameter suggests that Canvas return module items directly in the Module object JSON, to avoid having to make separate API requests for each module when enumerating modules and items. Canvas is free to omit ‘items’ for any particular module if it deems them too numerous to return inline. Callers must be prepared to use the List Module Items API if items are not returned.                                  `content_details`: Requires ‘items’. Returns additional details with module items specific to their associated content items. Includes standard lock information for each item.                                  Allowed values: items, content_details
            student_id | |string |Returns module completion information for the student with this id.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/modules/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/modules

        
        Module: Modules
        Function Description: Create a module

        Parameter Desc:
            module[name]                        |Required |string   |The name of the module
            module[unlock_at]                   |         |DateTime |The date the module will unlock
            module[position]                    |         |integer  |The position of this module in the course (1-based)
            module[require_sequential_progress] |         |boolean  |Whether module items must be unlocked in order
            module[prerequisite_module_ids][]   |         |string   |IDs of Modules that must be completed before this one is unlocked. Prerequisite modules must precede this module (i.e. have a lower position value), otherwise they will be ignored
            module[publish_final_grade]         |         |boolean  |Whether to publish the student’s final grade for the course upon completion of this module.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/modules'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/modules/:id

        
        Module: Modules
        Function Description: Update a module

        Parameter Desc:
            module[name]                        | |string   |The name of the module
            module[unlock_at]                   | |DateTime |The date the module will unlock
            module[position]                    | |integer  |The position of the module in the course (1-based)
            module[require_sequential_progress] | |boolean  |Whether module items must be unlocked in order
            module[prerequisite_module_ids][]   | |string   |IDs of Modules that must be completed before this one is unlocked Prerequisite modules must precede this module (i.e. have a lower position value), otherwise they will be ignored
            module[publish_final_grade]         | |boolean  |Whether to publish the student’s final grade for the course upon completion of this module.
            module[published]                   | |boolean  |Whether the module is published and visible to students
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/modules/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/modules/:id

        
        Module: Modules
        Function Description: Delete module

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/modules/{id}'
        return self.request(method, api, params)
        
    def relock(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContextModulesApiController#relock,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_modules_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_modules_api.relock
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/modules/:id/relock

        
        Module: Modules
        Function Description: Re-lock module progressions

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/modules/{id}/relock'
        return self.request(method, api, params)
        