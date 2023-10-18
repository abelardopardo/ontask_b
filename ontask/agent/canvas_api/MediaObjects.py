from .etc.conf import *
from .res import *

class MediaObjects(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: MediaObjectsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/media_objects_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.media_objects.index
        
        Scope:
            url:GET|/api/v1/media_objects
            url:GET|/api/v1/courses/:course_id/media_objects
            url:GET|/api/v1/groups/:group_id/media_objects
            url:GET|/api/v1/media_attachments
            url:GET|/api/v1/courses/:course_id/media_attachments
            url:GET|/api/v1/groups/:group_id/media_attachments

        
        Module: Media Objects
        Function Description: List Media Objects

        Parameter Desc:
            sort      | |string |Field to sort on. Default is `title`                                 title                                 sorts on user_entered_title if available, title if not.                                 created_at                                 sorts on the object’s creation time.                                 Allowed values: title, created_at
            order     | |string |Sort direction. Default is `asc`                                 Allowed values: asc, desc
            exclude[] | |string |Array of data to exclude. By excluding `sources` and `tracks`, the api will not need to query kaltura, which greatly speeds up its response.                                 sources                                 Do not query kaltura for media_sources                                 tracks                                 Do not query kaltura for media_tracks                                 Allowed values: sources, tracks
        """
        method = "GET"
        api = f'/api/v1/media_objects'
        return self.request(method, api, params)
        
    def update_media_object(self, media_object_id, params={}):
        """
        Source Code:
            Code: MediaObjectsController#update_media_object,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/media_objects_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.media_objects.update_media_object
        
        Scope:
            url:PUT|/api/v1/media_objects/:media_object_id
            url:PUT|/api/v1/media_attachments/:attachment_id

        
        Module: Media Objects
        Function Description: Update Media Object

        """
        method = "PUT"
        api = f'/api/v1/media_objects/{media_object_id}'
        return self.request(method, api, params)
        