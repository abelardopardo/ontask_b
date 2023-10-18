from .etc.conf import *
from .res import *

class AssociatedCourseHistory(Res):
    def subscriptions_index(self, course_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#subscriptions_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.subscriptions_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_subscriptions

        
        Module: Associated Course History
        Function Description: List blueprint subscriptions

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_subscriptions'
        return self.request(method, api, params)
        
    def imports_index(self, course_id, subscription_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#imports_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.imports_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_subscriptions/:subscription_id/migrations

        
        Module: Associated Course History
        Function Description: List blueprint imports

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_subscriptions/{subscription_id}/migrations'
        return self.request(method, api, params)
        
    def imports_show(self, course_id, subscription_id, id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#imports_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.imports_show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_subscriptions/:subscription_id/migrations/:id

        
        Module: Associated Course History
        Function Description: Show a blueprint import

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_subscriptions/{subscription_id}/migrations/{id}'
        return self.request(method, api, params)
        
    def import_details(self, course_id, subscription_id, id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#import_details,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.import_details
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_subscriptions/:subscription_id/migrations/:id/details

        
        Module: Associated Course History
        Function Description: Get import details

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_subscriptions/{subscription_id}/migrations/{id}/details'
        return self.request(method, api, params)
        