from .etc.conf import *
from .res import *

class Announcements(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: AnnouncementsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/announcements_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.announcements_api.index
        
        Scope:
            url:GET|/api/v1/announcements

        
        Module: Announcements
        Function Description: List announcements

        Parameter Desc:
            context_codes[] |Required |string  |List of context_codes to retrieve announcements for (for example, course_123). Only courses are presently supported. The call will fail unless the caller has View Announcements permission in all listed courses.
            start_date      |         |Date    |Only return announcements posted since the start_date (inclusive). Defaults to 14 days ago. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            end_date        |         |Date    |Only return announcements posted before the end_date (inclusive). Defaults to 28 days from start_date. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ. Announcements scheduled for future posting will only be returned to course administrators.
            active_only     |         |boolean |Only return active announcements that have been published. Applies only to requesting users that have permission to view unpublished items. Defaults to false for users with access to view unpublished items, otherwise true and unmodifiable.
            latest_only     |         |boolean |Only return the latest announcement for each associated context. The response will include at most one announcement for each specified context in the context_codes[] parameter. Defaults to false.
            include         |         |array   |Optional list of resources to include with the response. May include a string of the name of the resource. Possible values are: `sections`, `sections_user_count` if `sections` is passed, includes the course sections that are associated with the topic, if the topic is specific to certain sections of the course. If `sections_user_count` is passed, then:                                                (a) If sections were asked for *and* the topic is specific to certain                                                    course sections sections, includes the number of users in each                                                    section. (as part of the section json asked for above)                                                (b) Else, includes at the root level the total number of users in the                                                    topic's context (group or course) that the topic applies to.

        Request Example: 
            curl https://<canvas>/api/v1/announcements?context_codes[]=course_1&context_codes[]=course_2 \
                 -H 'Authorization: Bearer <token>'

        Response Example: 
            [{
              "id": 1,
              "title": "Hear ye",
              "message": "Henceforth, all assignments must be...",
              "posted_at": "2017-01-31T22:00:00Z",
              "delayed_post_at": null,
              "context_code": "course_2",
              ...
            }]
        """
        method = "GET"
        api = f'/api/v1/announcements'
        return self.request(method, api, params)
        