from .etc.conf import *
from .res import *

class Planner(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: PlannerController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/planner_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.planner.index
        
        Scope:
            url:GET|/api/v1/planner/items
            url:GET|/api/v1/users/:user_id/planner/items

        
        Module: Planner
        Function Description: List planner items

        Parameter Desc:
            start_date       | |Date   |Only return items starting from the given date. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            end_date         | |Date   |Only return items up to the given date. The value should be formatted as: yyyy-mm-dd or ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            context_codes[]  | |string |List of context codes of courses and/or groups whose items you want to see. If not specified, defaults to all contexts associated to the current user. Note that concluded courses will be ignored unless specified in the includes[] parameter. The format of this field is the context type, followed by an underscore, followed by the context id. For example: course_42, group_123
            observed_user_id | |string |Return planner items for the given observed user. Must be accompanied by context_codes[]. The user making the request must be observing the observed user in all the courses specified by context_codes[].
            filter           | |string |Only return items that have new or unread activity                                        Allowed values: new_activity

        Response Example: 
            [
             {
               "context_type": "Course",
               "course_id": 1,
               "planner_override": { ... planner override object ... }, // Associated PlannerOverride object if user has toggled visibility for the object on the planner
               "submissions": false, // The statuses of the user's submissions for this object
               "plannable_id": "123",
               "plannable_type": "discussion_topic",
               "plannable": { ... discussion topic object },
               "html_url": "/courses/1/discussion_topics/8"
             },
             {
               "context_type": "Course",
               "course_id": 1,
               "planner_override": {
                   "id": 3,
                   "plannable_type": "Assignment",
                   "plannable_id": 1,
                   "user_id": 2,
                   "workflow_state": "active",
                   "marked_complete": true, // A user-defined setting for marking items complete in the planner
                   "dismissed": false, // A user-defined setting for hiding items from the opportunities list
                   "deleted_at": null,
                   "created_at": "2017-05-18T18:35:55Z",
                   "updated_at": "2017-05-18T18:35:55Z"
               },
               "submissions": { // The status as it pertains to the current user
                 "excused": false,
                 "graded": false,
                 "late": false,
                 "missing": true,
                 "needs_grading": false,
                 "with_feedback": false
               },
               "plannable_id": "456",
               "plannable_type": "assignment",
               "plannable": { ... assignment object ...  },
               "html_url": "http://canvas.instructure.com/courses/1/assignments/1#submit"
             },
             {
               "planner_override": null,
               "submissions": false, // false if no associated assignment exists for the plannable item
               "plannable_id": "789",
               "plannable_type": "planner_note",
               "plannable": {
                 "id": 1,
                 "todo_date": "2017-05-30T06:00:00Z",
                 "title": "hello",
                 "details": "world",
                 "user_id": 2,
                 "course_id": null,
                 "workflow_state": "active",
                 "created_at": "2017-05-30T16:29:04Z",
                 "updated_at": "2017-05-30T16:29:15Z"
               },
               "html_url": "http://canvas.instructure.com/api/v1/planner_notes.1"
             }
            ]
        """
        method = "GET"
        api = f'/api/v1/planner/items'
        return self.request(method, api, params)
        