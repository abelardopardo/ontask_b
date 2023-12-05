from .etc.conf import *
from .res import *

class DiscussionTopics(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics
            url:GET|/api/v1/groups/:group_id/discussion_topics

        
        Module: Discussion Topics
        Function Description: List discussion topics

        Parameter Desc:
            include[]                            | |string  |If `all_dates` is passed, all dates associated with graded discussions’ assignments will be included. if `sections` is passed, includes the course sections that are associated with the topic, if the topic is specific to certain sections of the course. If `sections_user_count` is passed, then:                                                             (a) If sections were asked for *and* the topic is specific to certain                                                                 course sections, includes the number of users in each                                                                 section. (as part of the section json asked for above)                                                             (b) Else, includes at the root level the total number of users in the                                                                 topic's context (group or course) that the topic applies to.                                                             If `overrides` is passed, the overrides for the assignment will be included                                                             Allowed values: all_dates, sections, sections_user_count, overrides
            order_by                             | |string  |Determines the order of the discussion topic list. Defaults to `position`.                                                             Allowed values: position, recent_activity, title
            scope                                | |string  |Only return discussion topics in the given state(s). Defaults to including all topics. Filtering is done after pagination, so pages may be smaller than requested if topics are filtered. Can pass multiple states as comma separated string.                                                             Allowed values: locked, unlocked, pinned, unpinned
            only_announcements                   | |boolean |Return announcements instead of discussion topics. Defaults to false
            filter_by                            | |string  |The state of the discussion topic to return. Currently only supports unread state.                                                             Allowed values: all, unread
            search_term                          | |string  |The partial title of the discussion topics to match and return.
            exclude_context_module_locked_topics | |boolean |For students, exclude topics that are locked by module progression. Defaults to false.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics
            url:POST|/api/v1/groups/:group_id/discussion_topics

        
        Module: Discussion Topics
        Function Description: Create a new discussion topic

        Parameter Desc:
            title                     | |string     |no description
            message                   | |string     |no description
            discussion_type           | |string     |The type of discussion. Defaults to side_comment if not value is given. Accepted values are ‘side_comment’, for discussions that only allow one level of nested comments, and ‘threaded’ for fully threaded discussions.                                                     Allowed values: side_comment, threaded
            published                 | |boolean    |Whether this topic is published (true) or draft state (false). Only teachers and TAs have the ability to create draft state topics.
            delayed_post_at           | |DateTime   |If a timestamp is given, the topic will not be published until that time.
            allow_rating              | |boolean    |Whether or not users can rate entries in this topic.
            lock_at                   | |DateTime   |If a timestamp is given, the topic will be scheduled to lock at the provided timestamp. If the timestamp is in the past, the topic will be locked.
            podcast_enabled           | |boolean    |If true, the topic will have an associated podcast feed.
            podcast_has_student_posts | |boolean    |If true, the podcast will include posts from students as well. Implies podcast_enabled.
            require_initial_post      | |boolean    |If true then a user may not respond to other replies until that user has made an initial reply. Defaults to false.
            assignment                | |Assignment |To create an assignment discussion, pass the assignment parameters as a sub-object. See the Create an Assignment API for the available parameters. The name parameter will be ignored, as it’s taken from the discussion title. If you want to make a discussion that was an assignment NOT an assignment, pass set_assignment = false as part of the assignment object
            is_announcement           | |boolean    |If true, this topic is an announcement. It will appear in the announcement’s section rather than the discussions section. This requires announcment-posting permissions.
            pinned                    | |boolean    |If true, this topic will be listed in the `Pinned Discussion` section
            position_after            | |string     |By default, discussions are sorted chronologically by creation date, you can pass the id of another topic to have this one show up after the other when they are listed.
            group_category_id         | |integer    |If present, the topic will become a group discussion assigned to the group.
            only_graders_can_rate     | |boolean    |If true, only graders will be allowed to rate entries.
            sort_by_rating            | |boolean    |If true, entries will be sorted by rating.
            attachment                | |File       |A multipart/form-data form-field-style attachment. Attachments larger than 1 kilobyte are subject to quota restrictions.
            specific_sections         | |string     |A comma-separated list of sections ids to which the discussion topic should be made specific to.  If it is not desired to make the discussion topic specific to sections, then this parameter may be omitted or set to `all`.  Can only be present only on announcements and only those that are for a course (as opposed to a group).
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics'
        return self.request(method, api, params)
        
    def update(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id

        
        Module: Discussion Topics
        Function Description: Update a topic

        Parameter Desc:
            title                     | |string     |no description
            message                   | |string     |no description
            discussion_type           | |string     |The type of discussion. Defaults to side_comment if not value is given. Accepted values are ‘side_comment’, for discussions that only allow one level of nested comments, and ‘threaded’ for fully threaded discussions.                                                     Allowed values: side_comment, threaded
            published                 | |boolean    |Whether this topic is published (true) or draft state (false). Only teachers and TAs have the ability to create draft state topics.
            delayed_post_at           | |DateTime   |If a timestamp is given, the topic will not be published until that time.
            lock_at                   | |DateTime   |If a timestamp is given, the topic will be scheduled to lock at the provided timestamp. If the timestamp is in the past, the topic will be locked.
            podcast_enabled           | |boolean    |If true, the topic will have an associated podcast feed.
            podcast_has_student_posts | |boolean    |If true, the podcast will include posts from students as well. Implies podcast_enabled.
            require_initial_post      | |boolean    |If true then a user may not respond to other replies until that user has made an initial reply. Defaults to false.
            assignment                | |Assignment |To create an assignment discussion, pass the assignment parameters as a sub-object. See the Create an Assignment API for the available parameters. The name parameter will be ignored, as it’s taken from the discussion title. If you want to make a discussion that was an assignment NOT an assignment, pass set_assignment = false as part of the assignment object
            is_announcement           | |boolean    |If true, this topic is an announcement. It will appear in the announcement’s section rather than the discussions section. This requires announcment-posting permissions.
            pinned                    | |boolean    |If true, this topic will be listed in the `Pinned Discussion` section
            position_after            | |string     |By default, discussions are sorted chronologically by creation date, you can pass the id of another topic to have this one show up after the other when they are listed.
            group_category_id         | |integer    |If present, the topic will become a group discussion assigned to the group.
            allow_rating              | |boolean    |If true, users will be allowed to rate entries.
            only_graders_can_rate     | |boolean    |If true, only graders will be allowed to rate entries.
            sort_by_rating            | |boolean    |If true, entries will be sorted by rating.
            specific_sections         | |string     |A comma-separated list of sections ids to which the discussion topic should be made specific too.  If it is not desired to make the discussion topic specific to sections, then this parameter may be omitted or set to `all`.  Can only be present only on announcements and only those that are for a course (as opposed to a group).
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id

        
        Module: Discussion Topics
        Function Description: Delete a topic

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}'
        return self.request(method, api, params)
        
    def reorder(self, course_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsController#reorder,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics.reorder
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics/reorder
            url:POST|/api/v1/groups/:group_id/discussion_topics/reorder

        
        Module: Discussion Topics
        Function Description: Reorder pinned topics

        Parameter Desc:
            order[] |Required |integer |The ids of the pinned discussion topics in the desired order. (For example, `order=104,102,103`.)
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics/reorder'
        return self.request(method, api, params)
        
    def update(self, course_id, topic_id, id, params={}):
        """
        Source Code:
            Code: DiscussionEntriesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_entries_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_entries.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:id
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:id

        
        Module: Discussion Topics
        Function Description: Update an entry

        Parameter Desc:
            message | |string |The updated body of the entry.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, topic_id, id, params={}):
        """
        Source Code:
            Code: DiscussionEntriesController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_entries_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_entries.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:id
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:id

        
        Module: Discussion Topics
        Function Description: Delete an entry

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{id}'
        return self.request(method, api, params)
        
    def show(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics/:topic_id
            url:GET|/api/v1/groups/:group_id/discussion_topics/:topic_id

        
        Module: Discussion Topics
        Function Description: Get a single topic

        Parameter Desc:
            include[] | |string |If `all_dates` is passed, all dates associated with graded discussions’ assignments will be included. if `sections` is passed, includes the course sections that are associated with the topic, if the topic is specific to certain sections of the course. If `sections_user_count` is passed, then:                                 (a) If sections were asked for *and* the topic is specific to certain                                     course sections, includes the number of users in each                                     section. (as part of the section json asked for above)                                 (b) Else, includes at the root level the total number of users in the                                     topic's context (group or course) that the topic applies to.                                 If `overrides` is passed, the overrides for the assignment will be included                                 Allowed values: all_dates, sections, sections_user_count, overrides
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}'
        return self.request(method, api, params)
        
    def view(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#view,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.view
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics/:topic_id/view
            url:GET|/api/v1/groups/:group_id/discussion_topics/:topic_id/view

        
        Module: Discussion Topics
        Function Description: Get the full topic


        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/discussion_topics/<topic_id>/view' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            {
              "unread_entries": [1,3,4],
              "entry_ratings": {3: 1},
              "forced_entries": [1],
              "participants": [
                { "id": 10, "display_name": "user 1", "avatar_image_url": "https://...", "html_url": "https://..." },
                { "id": 11, "display_name": "user 2", "avatar_image_url": "https://...", "html_url": "https://..." }
              ],
              "view": [
                { "id": 1, "user_id": 10, "parent_id": null, "message": "...html text...", "replies": [
                  { "id": 3, "user_id": 11, "parent_id": 1, "message": "...html....", "replies": [...] }
                ]},
                { "id": 2, "user_id": 11, "parent_id": null, "message": "...html..." },
                { "id": 4, "user_id": 10, "parent_id": null, "message": "...html..." }
              ]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/view'
        return self.request(method, api, params)
        
    def add_entry(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#add_entry,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.add_entry
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries
            url:POST|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries

        
        Module: Discussion Topics
        Function Description: Post an entry

        Parameter Desc:
            message    | |string |The body of the entry.
            attachment | |string |a multipart/form-data form-field-style attachment. Attachments larger than 1 kilobyte are subject to quota restrictions.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries'
        return self.request(method, api, params)
        
    def duplicate(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#duplicate,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.duplicate
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics/:topic_id/duplicate
            url:POST|/api/v1/groups/:group_id/discussion_topics/:topic_id/duplicate

        
        Module: Discussion Topics
        Function Description: Duplicate discussion topic

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/duplicate'
        return self.request(method, api, params)
        
    def entries(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#entries,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.entries
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries
            url:GET|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries

        
        Module: Discussion Topics
        Function Description: List topic entries


        Response Example: 
            [ {
                "id": 1019,
                "user_id": 7086,
                "user_name": "nobody@example.com",
                "message": "Newer entry",
                "read_state": "read",
                "forced_read_state": false,
                "created_at": "2011-11-03T21:33:29Z",
                "attachment": {
                  "content-type": "unknown/unknown",
                  "url": "http://www.example.com/files/681/download?verifier=JDG10Ruitv8o6LjGXWlxgOb5Sl3ElzVYm9cBKUT3",
                  "filename": "content.txt",
                  "display_name": "content.txt" } },
              {
                "id": 1016,
                "user_id": 7086,
                "user_name": "nobody@example.com",
                "message": "first top-level entry",
                "read_state": "unread",
                "forced_read_state": false,
                "created_at": "2011-11-03T21:32:29Z",
                "recent_replies": [
                  {
                    "id": 1017,
                    "user_id": 7086,
                    "user_name": "nobody@example.com",
                    "message": "Reply message",
                    "created_at": "2011-11-03T21:32:29Z"
                  } ],
                "has_more_replies": false } ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries'
        return self.request(method, api, params)
        
    def add_reply(self, course_id, topic_id, entry_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#add_reply,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.add_reply
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:entry_id/replies
            url:POST|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:entry_id/replies

        
        Module: Discussion Topics
        Function Description: Post a reply

        Parameter Desc:
            message    | |string |The body of the entry.
            attachment | |string |a multipart/form-data form-field-style attachment. Attachments larger than 1 kilobyte are subject to quota restrictions.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/replies'
        return self.request(method, api, params)
        
    def replies(self, course_id, topic_id, entry_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#replies,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.replies
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:entry_id/replies
            url:GET|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:entry_id/replies

        
        Module: Discussion Topics
        Function Description: List entry replies


        Response Example: 
            [ {
                "id": 1015,
                "user_id": 7084,
                "user_name": "nobody@example.com",
                "message": "Newer message",
                "read_state": "read",
                "forced_read_state": false,
                "created_at": "2011-11-03T21:27:44Z" },
              {
                "id": 1014,
                "user_id": 7084,
                "user_name": "nobody@example.com",
                "message": "Older message",
                "read_state": "unread",
                "forced_read_state": false,
                "created_at": "2011-11-03T21:26:44Z" } ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/replies'
        return self.request(method, api, params)
        
    def entry_list(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#entry_list,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.entry_list
        
        Scope:
            url:GET|/api/v1/courses/:course_id/discussion_topics/:topic_id/entry_list
            url:GET|/api/v1/groups/:group_id/discussion_topics/:topic_id/entry_list

        
        Module: Discussion Topics
        Function Description: List entries

        Parameter Desc:
            ids[] | |string |A list of entry ids to retrieve. Entries will be returned in id order, smallest id first.

        Request Example: 
            curl 'https://<canvas>/api/v1/courses/<course_id>/discussion_topics/<topic_id>/entry_list?ids[]=1&ids[]=2&ids[]=3' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            [
              { ... entry 1 ... },
              { ... entry 2 ... },
              { ... entry 3 ... },
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entry_list'
        return self.request(method, api, params)
        
    def mark_topic_read(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_topic_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_topic_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id/read
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id/read

        
        Module: Discussion Topics
        Function Description: Mark topic as read

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/read'
        return self.request(method, api, params)
        
    def mark_topic_unread(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_topic_unread,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_topic_unread
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id/read
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id/read

        
        Module: Discussion Topics
        Function Description: Mark topic as unread

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/read'
        return self.request(method, api, params)
        
    def mark_all_read(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_all_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_all_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id/read_all
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id/read_all

        
        Module: Discussion Topics
        Function Description: Mark all entries as read

        Parameter Desc:
            forced_read_state | |boolean |A boolean value to set all of the entries’ forced_read_state. No change is made if this argument is not specified.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/read_all'
        return self.request(method, api, params)
        
    def mark_all_unread(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_all_unread,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_all_unread
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id/read_all
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id/read_all

        
        Module: Discussion Topics
        Function Description: Mark all entries as unread

        Parameter Desc:
            forced_read_state | |boolean |A boolean value to set all of the entries’ forced_read_state. No change is made if this argument is not specified.
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/read_all'
        return self.request(method, api, params)
        
    def mark_entry_read(self, course_id, topic_id, entry_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_entry_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_entry_read
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:entry_id/read
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:entry_id/read

        
        Module: Discussion Topics
        Function Description: Mark entry as read

        Parameter Desc:
            forced_read_state | |boolean |A boolean value to set the entry’s forced_read_state. No change is made if this argument is not specified.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/read'
        return self.request(method, api, params)
        
    def mark_entry_unread(self, course_id, topic_id, entry_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#mark_entry_unread,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.mark_entry_unread
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:entry_id/read
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:entry_id/read

        
        Module: Discussion Topics
        Function Description: Mark entry as unread

        Parameter Desc:
            forced_read_state | |boolean |A boolean value to set the entry’s forced_read_state. No change is made if this argument is not specified.
        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/read'
        return self.request(method, api, params)
        
    def rate_entry(self, course_id, topic_id, entry_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#rate_entry,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.rate_entry
        
        Scope:
            url:POST|/api/v1/courses/:course_id/discussion_topics/:topic_id/entries/:entry_id/rating
            url:POST|/api/v1/groups/:group_id/discussion_topics/:topic_id/entries/:entry_id/rating

        
        Module: Discussion Topics
        Function Description: Rate entry

        Parameter Desc:
            rating | |integer |A rating to set on this entry. Only 0 and 1 are accepted.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/rating'
        return self.request(method, api, params)
        
    def subscribe_topic(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#subscribe_topic,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.subscribe_topic
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/discussion_topics/:topic_id/subscribed
            url:PUT|/api/v1/groups/:group_id/discussion_topics/:topic_id/subscribed

        
        Module: Discussion Topics
        Function Description: Subscribe to a topic

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/subscribed'
        return self.request(method, api, params)
        
    def unsubscribe_topic(self, course_id, topic_id, params={}):
        """
        Source Code:
            Code: DiscussionTopicsApiController#unsubscribe_topic,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/discussion_topics_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.discussion_topics_api.unsubscribe_topic
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/discussion_topics/:topic_id/subscribed
            url:DELETE|/api/v1/groups/:group_id/discussion_topics/:topic_id/subscribed

        
        Module: Discussion Topics
        Function Description: Unsubscribe from a topic

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/discussion_topics/{topic_id}/subscribed'
        return self.request(method, api, params)
        