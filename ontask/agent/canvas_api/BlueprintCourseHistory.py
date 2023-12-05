from .etc.conf import *
from .res import *

class BlueprintCourseHistory(Res):
    def migrations_index(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#migrations_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.migrations_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id/migrations

        
        Module: Blueprint Course History
        Function Description: List blueprint migrations

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/migrations'
        return self.request(method, api, params)
        
    def migrations_show(self, course_id, template_id, id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#migrations_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.migrations_show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id/migrations/:id

        
        Module: Blueprint Course History
        Function Description: Show a blueprint migration

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/migrations/{id}'
        return self.request(method, api, params)
        
    def migration_details(self, course_id, template_id, id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#migration_details,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.migration_details
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id/migrations/:id/details

        
        Module: Blueprint Course History
        Function Description: Get migration details

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/migrations/{id}/details'
        return self.request(method, api, params)
        