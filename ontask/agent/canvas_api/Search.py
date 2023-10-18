from .etc.conf import *
from .res import *

class Search(Res):
    def recipients(self, params={}):
        """
        Source Code:
            Code: SearchController#recipients,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/search_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.search.recipients
        
        Scope:
            url:GET|/api/v1/conversations/find_recipients
            url:GET|/api/v1/search/recipients

        
        Module: Search
        Function Description: Find recipients

        Parameter Desc:
            search               | |string  |Search terms used for matching users/courses/groups (e.g. `bob smith`). If multiple terms are given (separated via whitespace), only results matching all terms will be returned.
            context              | |string  |Limit the search to a particular course/group (e.g. `course_3` or `group_4`).
            exclude[]            | |string  |Array of ids to exclude from the search. These may be user ids or course/group ids prefixed with `course_` or `group_` respectively, e.g. exclude[]=1&exclude=2&exclude[]=course_3
            type                 | |string  |Limit the search just to users or contexts (groups/courses).                                             Allowed values: user, context
            user_id              | |integer |Search for a specific user id. This ignores the other above parameters, and will never return more than one result.
            from_conversation_id | |integer |When searching by user_id, only users that could be normally messaged by this user will be returned. This parameter allows you to specify a conversation that will be referenced for a shared context – if both the current user and the searched user are in the conversation, the user will be returned. This is used to start new side conversations.
            permissions[]        | |string  |Array of permission strings to be checked for each matched context (e.g. `send_messages`). This argument determines which permissions may be returned in the response; it won’t prevent contexts from being returned if they don’t grant the permission(s).

        Response Example: 
            [
              {"id": "group_1", "name": "the group", "type": "context", "user_count": 3},
              {"id": 2, "name": "greg", "full_name": "greg jones", "common_courses": {}, "common_groups": {"1": ["Member"]}}
            ]
        """
        method = "GET"
        api = f'/api/v1/conversations/find_recipients'
        return self.request(method, api, params)
        
    def all_courses(self, params={}):
        """
        Source Code:
            Code: SearchController#all_courses,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/search_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.search.all_courses
        
        Scope:
            url:GET|/api/v1/search/all_courses

        
        Module: Search
        Function Description: List all courses

        Parameter Desc:
            search               | |string  |Search terms used for matching users/courses/groups (e.g. `bob smith`). If multiple terms are given (separated via whitespace), only results matching all terms will be returned.
            public_only          | |boolean |Only return courses with public content. Defaults to false.
            open_enrollment_only | |boolean |Only return courses that allow self enrollment. Defaults to false.
        """
        method = "GET"
        api = f'/api/v1/search/all_courses'
        return self.request(method, api, params)
        