from .etc.conf import *
from .res import *

class BlueprintManagement(Res):
    def show(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id

        
        Module: Blueprint Management
        Function Description: Get blueprint information

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}'
        return self.request(method, api, params)
        
    def associated_courses(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#associated_courses,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.associated_courses
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id/associated_courses

        
        Module: Blueprint Management
        Function Description: Get associated course information

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/associated_courses'
        return self.request(method, api, params)
        
    def update_associations(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#update_associations,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.update_associations
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/blueprint_templates/:template_id/update_associations

        
        Module: Blueprint Management
        Function Description: Update associated courses

        Parameter Desc:
            course_ids_to_add    | |Array |Courses to add as associated courses
            course_ids_to_remove | |Array |Courses to remove as associated courses
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/update_associations'
        return self.request(method, api, params)
        
    def queue_migration(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#queue_migration,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.queue_migration
        
        Scope:
            url:POST|/api/v1/courses/:course_id/blueprint_templates/:template_id/migrations

        
        Module: Blueprint Management
        Function Description: Begin a migration to push to associated courses

        Parameter Desc:
            comment                    | |string  |An optional comment to be included in the sync history.
            send_notification          | |boolean |Send a notification to the calling user when the sync completes.
            copy_settings              | |boolean |Whether course settings should be copied over to associated courses. Defaults to true for newly associated courses.
            publish_after_initial_sync | |boolean |If set, newly associated courses will be automatically published after the sync completes
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/migrations'
        return self.request(method, api, params)
        
    def restrict_item(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#restrict_item,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.restrict_item
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/blueprint_templates/:template_id/restrict_item

        
        Module: Blueprint Management
        Function Description: Set or remove restrictions on a blueprint course object

        Parameter Desc:
            content_type | |string               |String, `assignment`|`attachment`|`discussion_topic`|`external_tool`|`lti-quiz`|`quiz`|`wiki_page`                                                  The type of the object.
            content_id   | |integer              |The ID of the object.
            restricted   | |boolean              |Whether to apply restrictions.
            restrictions | |BlueprintRestriction |(Optional) If the object is restricted, this specifies a set of restrictions. If not specified, the course-level restrictions will be used. See Course API update documentation
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/restrict_item'
        return self.request(method, api, params)
        
    def unsynced_changes(self, course_id, template_id, params={}):
        """
        Source Code:
            Code: MasterCourses::MasterTemplatesController#unsynced_changes,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/master_courses/master_templates_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.master_courses/master_templates.unsynced_changes
        
        Scope:
            url:GET|/api/v1/courses/:course_id/blueprint_templates/:template_id/unsynced_changes

        
        Module: Blueprint Management
        Function Description: Get unsynced changes

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/blueprint_templates/{template_id}/unsynced_changes'
        return self.request(method, api, params)
        