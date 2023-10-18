from .etc.conf import *
from .res import *

class Sections(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: SectionsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/sections

        
        Module: Sections
        Function Description: List course sections

        Parameter Desc:
            include[] | |string |`students`: Associations to include with the group. Note: this is only available if you have permission to view users or grades in the course                                 `avatar_url`: Include the avatar URLs for students returned.                                 `enrollments`: If ‘students’ is also included, return the section enrollment for each student                                 `total_students`: Returns the total amount of active and invited students for the course section                                 `passback_status`: Include the grade passback status.                                 `permissions`: Include whether section grants :manage_calendar permission to the caller                                 Allowed values: students, avatar_url, enrollments, total_students, passback_status, permissions
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/sections'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: SectionsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/sections

        
        Module: Sections
        Function Description: Create course section

        Parameter Desc:
            course_section[name]                                  | |string   |The name of the section
            course_section[sis_section_id]                        | |string   |The sis ID of the section. Must have manage_sis permission to set. This is ignored if caller does not have permission to set.
            course_section[integration_id]                        | |string   |The integration_id of the section. Must have manage_sis permission to set. This is ignored if caller does not have permission to set.
            course_section[start_at]                              | |DateTime |Section start date in ISO8601 format, e.g. 2011-01-01T01:00Z
            course_section[end_at]                                | |DateTime |Section end date in ISO8601 format. e.g. 2011-01-01T01:00Z
            course_section[restrict_enrollments_to_section_dates] | |boolean  |Set to true to restrict user enrollments to the start and end dates of the section.
            enable_sis_reactivation                               | |boolean  |When true, will first try to re-activate a deleted section with matching sis_section_id if possible.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/sections'
        return self.request(method, api, params)
        
    def crosslist(self, id, new_course_id, params={}):
        """
        Source Code:
            Code: SectionsController#crosslist,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.crosslist
        
        Scope:
            url:POST|/api/v1/sections/:id/crosslist/:new_course_id

        
        Module: Sections
        Function Description: Cross-list a Section

        Parameter Desc:
            override_sis_stickiness | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "POST"
        api = f'/api/v1/sections/{id}/crosslist/{new_course_id}'
        return self.request(method, api, params)
        
    def uncrosslist(self, id, params={}):
        """
        Source Code:
            Code: SectionsController#uncrosslist,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.uncrosslist
        
        Scope:
            url:DELETE|/api/v1/sections/:id/crosslist

        
        Module: Sections
        Function Description: De-cross-list a Section

        Parameter Desc:
            override_sis_stickiness | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "DELETE"
        api = f'/api/v1/sections/{id}/crosslist'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: SectionsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.update
        
        Scope:
            url:PUT|/api/v1/sections/:id

        
        Module: Sections
        Function Description: Edit a section

        Parameter Desc:
            course_section[name]                                  | |string   |The name of the section
            course_section[sis_section_id]                        | |string   |The sis ID of the section. Must have manage_sis permission to set.
            course_section[integration_id]                        | |string   |The integration_id of the section. Must have manage_sis permission to set.
            course_section[start_at]                              | |DateTime |Section start date in ISO8601 format, e.g. 2011-01-01T01:00Z
            course_section[end_at]                                | |DateTime |Section end date in ISO8601 format. e.g. 2011-01-01T01:00Z
            course_section[restrict_enrollments_to_section_dates] | |boolean  |Set to true to restrict user enrollments to the start and end dates of the section.
            override_sis_stickiness                               | |boolean  |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
        """
        method = "PUT"
        api = f'/api/v1/sections/{id}'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: SectionsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/sections/:id
            url:GET|/api/v1/sections/:id

        
        Module: Sections
        Function Description: Get section information

        Parameter Desc:
            include[] | |string |`students`: Associations to include with the group. Note: this is only available if you have permission to view users or grades in the course                                 `avatar_url`: Include the avatar URLs for students returned.                                 `enrollments`: If ‘students’ is also included, return the section enrollment for each student                                 `total_students`: Returns the total amount of active and invited students for the course section                                 `passback_status`: Include the grade passback status.                                 `permissions`: Include whether section grants :manage_calendar permission to the caller                                 Allowed values: students, avatar_url, enrollments, total_students, passback_status, permissions
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/sections/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: SectionsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sections_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sections.destroy
        
        Scope:
            url:DELETE|/api/v1/sections/:id

        
        Module: Sections
        Function Description: Delete a section

        """
        method = "DELETE"
        api = f'/api/v1/sections/{id}'
        return self.request(method, api, params)
        