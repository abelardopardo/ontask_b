from .etc.conf import *
from .res import *

class AnnouncementExternalFeeds(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalFeedsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_feeds_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_feeds.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/external_feeds
            url:GET|/api/v1/groups/:group_id/external_feeds

        
        Module: Announcement External Feeds
        Function Description: List external feeds

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/external_feeds'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalFeedsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_feeds_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_feeds.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/external_feeds
            url:POST|/api/v1/groups/:group_id/external_feeds

        
        Module: Announcement External Feeds
        Function Description: Create an external feed

        Parameter Desc:
            url          |Required |string  |The url to the external rss or atom feed
            header_match |         |boolean |If given, only feed entries that contain this string in their title will be imported
            verbosity    |         |string  |Defaults to `full`                                             Allowed values: full, truncate, link_only
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/external_feeds'
        return self.request(method, api, params)
        
    def destroy(self, course_id, external_feed_id, params={}):
        """
        Source Code:
            Code: ExternalFeedsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_feeds_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_feeds.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/external_feeds/:external_feed_id
            url:DELETE|/api/v1/groups/:group_id/external_feeds/:external_feed_id

        
        Module: Announcement External Feeds
        Function Description: Delete an external feed

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/external_feeds/{external_feed_id}'
        return self.request(method, api, params)
        