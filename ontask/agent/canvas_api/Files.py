from .etc.conf import *
from .res import *

class Files(Res):
    def api_quota(self, course_id, params={}):
        """
        Source Code:
            Code: FilesController#api_quota,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.api_quota
        
        Scope:
            url:GET|/api/v1/courses/:course_id/files/quota
            url:GET|/api/v1/groups/:group_id/files/quota
            url:GET|/api/v1/users/:user_id/files/quota

        
        Module: Files
        Function Description: Get quota information


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/1/files/quota' \
                  -H 'Authorization: Bearer <token>'

        Response Example: 
            { "quota": 524288000, "quota_used": 402653184 }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/files/quota'
        return self.request(method, api, params)
        
    def api_index(self, course_id, params={}):
        """
        Source Code:
            Code: FilesController#api_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.api_index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/files
            url:GET|/api/v1/users/:user_id/files
            url:GET|/api/v1/groups/:group_id/files
            url:GET|/api/v1/folders/:id/files

        
        Module: Files
        Function Description: List files

        Parameter Desc:
            content_types[]         | |string |Filter results by content-type. You can specify type/subtype pairs (e.g., ‘image/jpeg’), or simply types (e.g., ‘image’, which will match ‘image/gif’, ‘image/jpeg’, etc.).
            exclude_content_types[] | |string |Exclude given content-types from your results. You can specify type/subtype pairs (e.g., ‘image/jpeg’), or simply types (e.g., ‘image’, which will match ‘image/gif’, ‘image/jpeg’, etc.).
            search_term             | |string |The partial name of the files to match and return.
            include[]               | |string |Array of additional information to include.                                               `user`                                               the user who uploaded the file or last edited its content                                               `usage_rights`                                               copyright and license information for the file (see UsageRights)                                               Allowed values: user
            only[]                  | |Array  |Array of information to restrict to. Overrides include[]                                               `names`                                               only returns file name information
            sort                    | |string |Sort results by this field. Defaults to ‘name’. Note that ‘sort=user` implies `include[]=user`.                                               Allowed values: name, size, created_at, updated_at, content_type, user
            order                   | |string |The sorting order. Defaults to ‘asc’.                                               Allowed values: asc, desc
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/files'
        return self.request(method, api, params)
        
    def public_url(self, id, params={}):
        """
        Source Code:
            Code: FilesController#public_url,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.public_url
        
        Scope:
            url:GET|/api/v1/files/:id/public_url

        
        Module: Files
        Function Description: Get public inline preview url

        Parameter Desc:
            submission_id | |integer |The id of the submission the file is associated with.  Provide this argument to gain access to a file that has been submitted to an assignment (Canvas will verify that the file belongs to the submission and the calling user has rights to view the submission).

        Request Example: 
            curl 'https://<canvas>/api/v1/files/1/public_url' \
                  -H 'Authorization: Bearer <token>'

        Response Example: 
            { "public_url": "https://example-bucket.s3.amazonaws.com/example-namespace/attachments/1/example-filename?AWSAccessKeyId=example-key&Expires=1400000000&Signature=example-signature" }
        """
        method = "GET"
        api = f'/api/v1/files/{id}/public_url'
        return self.request(method, api, params)
        
    def api_show(self, id, params={}):
        """
        Source Code:
            Code: FilesController#api_show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.api_show
        
        Scope:
            url:GET|/api/v1/files/:id
            url:POST|/api/v1/files/:id
            url:GET|/api/v1/courses/:course_id/files/:id
            url:GET|/api/v1/groups/:group_id/files/:id
            url:GET|/api/v1/users/:user_id/files/:id

        
        Module: Files
        Function Description: Get file

        Parameter Desc:
            include[]                      | |string  |Array of additional information to include.                                                       `user`                                                       the user who uploaded the file or last edited its content                                                       `usage_rights`                                                       copyright and license information for the file (see UsageRights)                                                       Allowed values: user
            replacement_chain_context_type | |string  |When a user replaces a file during upload, Canvas keeps track of the `replacement chain.`                                                       Include this parameter if you wish Canvas to follow the replacement chain if the requested file was deleted and replaced by another.                                                       Must be set to ‘course’ or ‘account’. The `replacement_chain_context_id` parameter must also be included.
            replacement_chain_context_id   | |integer |When a user replaces a file during upload, Canvas keeps track of the `replacement chain.`                                                       Include this parameter if you wish Canvas to follow the replacement chain if the requested file was deleted and replaced by another.                                                       Indicates the context ID Canvas should use when following the `replacement chain.` The `replacement_chain_context_type` parameter must also be included.
        """
        method = "GET"
        api = f'/api/v1/files/{id}'
        return self.request(method, api, params)
        
    def file_ref(self, course_id, migration_id, params={}):
        """
        Source Code:
            Code: FilesController#file_ref,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.file_ref
        
        Scope:
            url:GET|/api/v1/courses/:course_id/files/file_ref/:migration_id

        
        Module: Files
        Function Description: Translate file reference

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/files/file_ref/{migration_id}'
        return self.request(method, api, params)
        
    def api_update(self, id, params={}):
        """
        Source Code:
            Code: FilesController#api_update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.api_update
        
        Scope:
            url:PUT|/api/v1/files/:id

        
        Module: Files
        Function Description: Update file

        Parameter Desc:
            name             | |string   |The new display name of the file, with a limit of 255 characters.
            parent_folder_id | |string   |The id of the folder to move this file into. The new folder must be in the same context as the original parent folder. If the file is in a context without folders this does not apply.
            on_duplicate     | |string   |If the file is moved to a folder containing a file with the same name, or renamed to a name matching an existing file, the API call will fail unless this parameter is supplied.                                          `overwrite`                                          Replace the existing file with the same name                                          `rename`                                          Add a qualifier to make the new filename unique                                          Allowed values: overwrite, rename
            lock_at          | |DateTime |The datetime to lock the file at
            unlock_at        | |DateTime |The datetime to unlock the file at
            locked           | |boolean  |Flag the file as locked
            hidden           | |boolean  |Flag the file as hidden
            visibility_level | |string   |Configure which roles can access this file
        """
        method = "PUT"
        api = f'/api/v1/files/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: FilesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.destroy
        
        Scope:
            url:DELETE|/api/v1/files/:id

        
        Module: Files
        Function Description: Delete file

        Parameter Desc:
            replace | |boolean |This action is irreversible. If replace is set to true the file contents will be replaced with a generic `file has been removed` file. This also destroys any previews that have been generated for the file. Must have manage files and become other users permissions
        """
        method = "DELETE"
        api = f'/api/v1/files/{id}'
        return self.request(method, api, params)
        
    def icon_metadata(self, id, params={}):
        """
        Source Code:
            Code: FilesController#icon_metadata,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.icon_metadata
        
        Scope:
            url:GET|/api/v1/files/:id/icon_metadata

        
        Module: Files
        Function Description: Get icon metadata


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/1/files/1/metadata' \
                  -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "type":"image/svg+xml-icon-maker-icons",
              "alt":"",
              "shape":"square",
              "size":"small",
              "color":"#FFFFFF",
              "outlineColor":"#65499D",
              "outlineSize":"large",
              "text":"Hello",
              "textSize":"x-large",
              "textColor":"#65499D",
              "textBackgroundColor":"#FFFFFF",
              "textPosition":"bottom-third",
              "encodedImage":"data:image/svg+xml;base64,PH==",
              "encodedImageType":"SingleColor",
              "encodedImageName":"Health Icon",
              "x":"50%",
              "y":"50%",
              "translateX":-54,
              "translateY":-54,
              "width":108,
              "height":108,
              "transform":"translate(-54,-54)"
            }
        """
        method = "GET"
        api = f'/api/v1/files/{id}/icon_metadata'
        return self.request(method, api, params)
        
    def reset_verifier(self, id, params={}):
        """
        Source Code:
            Code: FilesController#reset_verifier,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/files_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.files.reset_verifier
        
        Scope:
            url:POST|/api/v1/files/:id/reset_verifier

        
        Module: Files
        Function Description: Reset link verifier

        """
        method = "POST"
        api = f'/api/v1/files/{id}/reset_verifier'
        return self.request(method, api, params)
        