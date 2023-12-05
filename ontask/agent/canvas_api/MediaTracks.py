from .etc.conf import *
from .res import *

class MediaTracks(Res):
    def index(self, media_object_id, params={}):
        """
        Source Code:
            Code: MediaTracksController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/media_tracks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.media_tracks.index
        
        Scope:
            url:GET|/api/v1/media_objects/:media_object_id/media_tracks
            url:GET|/api/v1/media_attachments/:attachment_id/media_tracks

        
        Module: Media Tracks
        Function Description: List media tracks for a Media Object or Attachment

        Parameter Desc:
            include[] | |string |By default, index returns id, locale, kind, media_object_id, and user_id for each of the result MediaTracks. Use include[] to add additional fields. For example include[]=content                                 Allowed values: content, webvtt_content, updated_at, created_at
        """
        method = "GET"
        api = f'/api/v1/media_objects/{media_object_id}/media_tracks'
        return self.request(method, api, params)
        
    def update(self, media_object_id, params={}):
        """
        Source Code:
            Code: MediaTracksController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/media_tracks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.media_tracks.update
        
        Scope:
            url:PUT|/api/v1/media_objects/:media_object_id/media_tracks
            url:PUT|/api/v1/media_attachments/:attachment_id/media_tracks

        
        Module: Media Tracks
        Function Description: Update Media Tracks

        Parameter Desc:
            include[] | |string |By default, an update returns id, locale, kind, media_object_id, and user_id for each of the result MediaTracks. Use include[] to add additional fields. For example include[]=content                                 Allowed values: content, webvtt_content, updated_at, created_at
        """
        method = "PUT"
        api = f'/api/v1/media_objects/{media_object_id}/media_tracks'
        return self.request(method, api, params)
        