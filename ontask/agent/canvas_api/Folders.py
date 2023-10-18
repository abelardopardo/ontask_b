from .etc.conf import *
from .res import *

class Folders(Res):
    def api_index(self, id, params={}):
        """
        Source Code:
            Code: FoldersController#api_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.api_index
        
        Scope:
            url:GET|/api/v1/folders/:id/folders

        
        Module: Folders
        Function Description: List folders

        """
        method = "GET"
        api = f'/api/v1/folders/{id}/folders'
        return self.request(method, api, params)
        
    def list_all_folders(self, course_id, params={}):
        """
        Source Code:
            Code: FoldersController#list_all_folders,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.list_all_folders
        
        Scope:
            url:GET|/api/v1/courses/:course_id/folders
            url:GET|/api/v1/users/:user_id/folders
            url:GET|/api/v1/groups/:group_id/folders

        
        Module: Folders
        Function Description: List all folders

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/folders'
        return self.request(method, api, params)
        
    def resolve_path(self, course_id, params={}):
        """
        Source Code:
            Code: FoldersController#resolve_path,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.resolve_path
        
        Scope:
            url:GET|/api/v1/courses/:course_id/folders/by_path/*full_path
            url:GET|/api/v1/courses/:course_id/folders/by_path
            url:GET|/api/v1/users/:user_id/folders/by_path/*full_path
            url:GET|/api/v1/users/:user_id/folders/by_path
            url:GET|/api/v1/groups/:group_id/folders/by_path/*full_path
            url:GET|/api/v1/groups/:group_id/folders/by_path

        
        Module: Folders
        Function Description: Resolve path

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/folders/by_path/*full_path'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: FoldersController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/folders/:id
            url:GET|/api/v1/users/:user_id/folders/:id
            url:GET|/api/v1/groups/:group_id/folders/:id
            url:GET|/api/v1/folders/:id

        
        Module: Folders
        Function Description: Get folder

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/folders/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: FoldersController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.update
        
        Scope:
            url:PUT|/api/v1/folders/:id

        
        Module: Folders
        Function Description: Update folder

        Parameter Desc:
            name             | |string   |The new name of the folder
            parent_folder_id | |string   |The id of the folder to move this folder into. The new folder must be in the same context as the original parent folder.
            lock_at          | |DateTime |The datetime to lock the folder at
            unlock_at        | |DateTime |The datetime to unlock the folder at
            locked           | |boolean  |Flag the folder as locked
            hidden           | |boolean  |Flag the folder as hidden
            position         | |integer  |Set an explicit sort position for the folder
        """
        method = "PUT"
        api = f'/api/v1/folders/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: FoldersController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/folders
            url:POST|/api/v1/users/:user_id/folders
            url:POST|/api/v1/groups/:group_id/folders
            url:POST|/api/v1/folders/:folder_id/folders

        
        Module: Folders
        Function Description: Create folder

        Parameter Desc:
            name               |Required |string   |The name of the folder
            parent_folder_id   |         |string   |The id of the folder to store the new folder in. An error will be returned if this does not correspond to an existing folder. If this and parent_folder_path are sent an error will be returned. If neither is given, a default folder will be used.
            parent_folder_path |         |string   |The path of the folder to store the new folder in. The path separator is the forward slash ‘/`, never a back slash. The parent folder will be created if it does not already exist. This parameter only applies to new folders in a context that has folders, such as a user, a course, or a group. If this and parent_folder_id are sent an error will be returned. If neither is given, a default folder will be used.
            lock_at            |         |DateTime |The datetime to lock the folder at
            unlock_at          |         |DateTime |The datetime to unlock the folder at
            locked             |         |boolean  |Flag the folder as locked
            hidden             |         |boolean  |Flag the folder as hidden
            position           |         |integer  |Set an explicit sort position for the folder
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/folders'
        return self.request(method, api, params)
        
    def api_destroy(self, id, params={}):
        """
        Source Code:
            Code: FoldersController#api_destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.api_destroy
        
        Scope:
            url:DELETE|/api/v1/folders/:id

        
        Module: Folders
        Function Description: Delete folder

        Parameter Desc:
            force | |boolean |Set to ‘true’ to allow deleting a non-empty folder
        """
        method = "DELETE"
        api = f'/api/v1/folders/{id}'
        return self.request(method, api, params)
        
    def create_file(self, folder_id, params={}):
        """
        Source Code:
            Code: FoldersController#create_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.create_file
        
        Scope:
            url:POST|/api/v1/folders/:folder_id/files

        
        Module: Folders
        Function Description: Upload a file

        """
        method = "POST"
        api = f'/api/v1/folders/{folder_id}/files'
        return self.request(method, api, params)
        
    def copy_file(self, dest_folder_id, params={}):
        """
        Source Code:
            Code: FoldersController#copy_file,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.copy_file
        
        Scope:
            url:POST|/api/v1/folders/:dest_folder_id/copy_file

        
        Module: Folders
        Function Description: Copy a file

        Parameter Desc:
            source_file_id |Required |string |The id of the source file
            on_duplicate   |         |string |What to do if a file with the same name already exists at the destination. If such a file exists and this parameter is not given, the call will fail.                                              `overwrite`                                              Replace an existing file with the same name                                              `rename`                                              Add a qualifier to make the new filename unique                                              Allowed values: overwrite, rename
        """
        method = "POST"
        api = f'/api/v1/folders/{dest_folder_id}/copy_file'
        return self.request(method, api, params)
        
    def copy_folder(self, dest_folder_id, params={}):
        """
        Source Code:
            Code: FoldersController#copy_folder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.copy_folder
        
        Scope:
            url:POST|/api/v1/folders/:dest_folder_id/copy_folder

        
        Module: Folders
        Function Description: Copy a folder

        Parameter Desc:
            source_folder_id |Required |string |The id of the source folder
        """
        method = "POST"
        api = f'/api/v1/folders/{dest_folder_id}/copy_folder'
        return self.request(method, api, params)
        
    def media_folder(self, course_id, params={}):
        """
        Source Code:
            Code: FoldersController#media_folder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/folders_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.folders.media_folder
        
        Scope:
            url:GET|/api/v1/courses/:course_id/folders/media
            url:GET|/api/v1/groups/:group_id/folders/media

        
        Module: Folders
        Function Description: Get uploaded media folder for user

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/folders/media'
        return self.request(method, api, params)
        