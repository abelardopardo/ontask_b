from .etc.conf import *
from .res import *

class ContentExports(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: ContentExportsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_exports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_exports_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/content_exports
            url:GET|/api/v1/groups/:group_id/content_exports
            url:GET|/api/v1/users/:user_id/content_exports

        
        Module: Content Exports
        Function Description: List content exports

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/content_exports'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContentExportsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_exports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_exports_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/content_exports/:id
            url:GET|/api/v1/groups/:group_id/content_exports/:id
            url:GET|/api/v1/users/:user_id/content_exports/:id

        
        Module: Content Exports
        Function Description: Show content export

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/content_exports/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: ContentExportsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_exports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_exports_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/content_exports
            url:POST|/api/v1/groups/:group_id/content_exports
            url:POST|/api/v1/users/:user_id/content_exports

        
        Module: Content Exports
        Function Description: Export content

        Parameter Desc:
            export_type        |Required |string  |`common_cartridge`                                                   Export the contents of the course in the Common Cartridge (.imscc) format                                                   `qti`                                                   Export quizzes from a course in the QTI format                                                   `zip`                                                   Export files from a course, group, or user in a zip file                                                   Allowed values: common_cartridge, qti, zip
            skip_notifications |         |boolean |Don’t send the notifications about the export to the user. Default: false
            select             |         |Hash    |The select parameter allows exporting specific data. The keys are object types like ‘files’, ‘folders’, ‘pages’, etc. The value for each key is a list of object ids. An id can be an integer or a string.                                                   Multiple object types can be selected in the same call. However, not all object types are valid for every export_type. Common Cartridge supports all object types. Zip and QTI only support the object types as described below.                                                   `folders`                                                   Also supported for zip export_type.                                                   `files`                                                   Also supported for zip export_type.                                                   `quizzes`                                                   Also supported for qti export_type.                                                   Allowed values: folders, files, attachments, quizzes, assignments, announcements, calendar_events, discussion_topics, modules, module_items, pages, rubrics
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/content_exports'
        return self.request(method, api, params)
        