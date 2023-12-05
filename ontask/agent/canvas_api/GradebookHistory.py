from .etc.conf import *
from .res import *

class GradebookHistory(Res):
    def days(self, course_id, params={}):
        """
        Source Code:
            Code: GradebookHistoryApiController#days,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/gradebook_history_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.gradebook_history_api.days
        
        Scope:
            url:GET|/api/v1/courses/:course_id/gradebook_history/days

        
        Module: Gradebook History
        Function Description: Days in gradebook history for this course

        Parameter Desc:
            course_id |Required |integer |The id of the contextual course for this API call
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/gradebook_history/days'
        return self.request(method, api, params)
        
    def day_details(self, course_id, date, params={}):
        """
        Source Code:
            Code: GradebookHistoryApiController#day_details,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/gradebook_history_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.gradebook_history_api.day_details
        
        Scope:
            url:GET|/api/v1/courses/:course_id/gradebook_history/:date

        
        Module: Gradebook History
        Function Description: Details for a given date in gradebook history for this course

        Parameter Desc:
            course_id |Required |integer |The id of the contextual course for this API call
            date      |Required |string  |The date for which you would like to see detailed information
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/gradebook_history/{date}'
        return self.request(method, api, params)
        
    def submissions(self, course_id, date, grader_id, assignment_id, params={}):
        """
        Source Code:
            Code: GradebookHistoryApiController#submissions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/gradebook_history_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.gradebook_history_api.submissions
        
        Scope:
            url:GET|/api/v1/courses/:course_id/gradebook_history/:date/graders/:grader_id/assignments/:assignment_id/submissions

        
        Module: Gradebook History
        Function Description: Lists submissions

        Parameter Desc:
            course_id     |Required |integer |The id of the contextual course for this API call
            date          |Required |string  |The date for which you would like to see submissions
            grader_id     |Required |integer |The ID of the grader for which you want to see submissions
            assignment_id |Required |integer |The ID of the assignment for which you want to see submissions
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/gradebook_history/{date}/graders/{grader_id}/assignments/{assignment_id}/submissions'
        return self.request(method, api, params)
        
    def feed(self, course_id, params={}):
        """
        Source Code:
            Code: GradebookHistoryApiController#feed,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/gradebook_history_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.gradebook_history_api.feed
        
        Scope:
            url:GET|/api/v1/courses/:course_id/gradebook_history/feed

        
        Module: Gradebook History
        Function Description: List uncollated submission versions

        Parameter Desc:
            course_id     |Required |integer |The id of the contextual course for this API call
            assignment_id |         |integer |The ID of the assignment for which you want to see submissions. If absent, versions of submissions from any assignment in the course are included.
            user_id       |         |integer |The ID of the user for which you want to see submissions. If absent, versions of submissions from any user in the course are included.
            ascending     |         |boolean |Returns submission versions in ascending date order (oldest first). If absent, returns submission versions in descending date order (newest first).
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/gradebook_history/feed'
        return self.request(method, api, params)
        