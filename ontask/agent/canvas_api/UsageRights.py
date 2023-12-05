from .etc.conf import *
from .res import *

class UsageRights(Res):
    def set_usage_rights(self, course_id, params={}):
        """
        Source Code:
            Code: UsageRightsController#set_usage_rights,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/usage_rights_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.usage_rights.set_usage_rights
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/usage_rights
            url:PUT|/api/v1/groups/:group_id/usage_rights
            url:PUT|/api/v1/users/:user_id/usage_rights

        
        Module: Usage Rights
        Function Description: Set usage rights

        Parameter Desc:
            file_ids[]                      |Required |string  |List of ids of files to set usage rights for.
            folder_ids[]                    |         |string  |List of ids of folders to search for files to set usage rights for. Note that new files uploaded to these folders do not automatically inherit these rights.
            publish                         |         |boolean |Whether the file(s) or folder(s) should be published on save, provided that usage rights have been specified (set to ‘true` to publish on save).
            usage_rights[use_justification] |Required |string  |The intellectual property justification for using the files in Canvas                                                                Allowed values: own_copyright, used_by_permission, fair_use, public_domain, creative_commons
            usage_rights[legal_copyright]   |         |string  |The legal copyright line for the files
            usage_rights[license]           |         |string  |The license that applies to the files. See the List licenses endpoint for the supported license types.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/usage_rights'
        return self.request(method, api, params)
        
    def remove_usage_rights(self, course_id, params={}):
        """
        Source Code:
            Code: UsageRightsController#remove_usage_rights,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/usage_rights_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.usage_rights.remove_usage_rights
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/usage_rights
            url:DELETE|/api/v1/groups/:group_id/usage_rights
            url:DELETE|/api/v1/users/:user_id/usage_rights

        
        Module: Usage Rights
        Function Description: Remove usage rights

        Parameter Desc:
            file_ids[]   |Required |string |List of ids of files to remove associated usage rights from.
            folder_ids[] |         |string |List of ids of folders. Usage rights will be removed from all files in these folders.
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/usage_rights'
        return self.request(method, api, params)
        
    def licenses(self, course_id, params={}):
        """
        Source Code:
            Code: UsageRightsController#licenses,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/usage_rights_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.usage_rights.licenses
        
        Scope:
            url:GET|/api/v1/courses/:course_id/content_licenses
            url:GET|/api/v1/groups/:group_id/content_licenses
            url:GET|/api/v1/users/:user_id/content_licenses

        
        Module: Usage Rights
        Function Description: List licenses

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/content_licenses'
        return self.request(method, api, params)
        