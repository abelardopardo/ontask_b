from .etc.conf import *
from .res import *

class Analytics(Res):
    def department_participation(self, account_id, term_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.department_participation
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/analytics/terms/:term_id/activity
            url:GET|/api/v1/accounts/:account_id/analytics/current/activity
            url:GET|/api/v1/accounts/:account_id/analytics/completed/activity

        
        Module: Analytics
        Function Description: Get department-level participation data


        Request Example: 
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/current/activity \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/completed/activity \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/terms/<term_id>/activity \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "by_date": {
                "2012-01-24": 1240,
                "2012-01-27": 912,
              },
              "by_category": {
                "announcements": 54,
                "assignments": 256,
                "collaborations": 18,
                "conferences": 26,
                "discussions": 354,
                "files": 132,
                "general": 59,
                "grades": 177,
                "groups": 132,
                "modules": 71,
                "other": 412,
                "pages": 105,
                "quizzes": 356
              },
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/analytics/terms/{term_id}/activity'
        return self.request(method, api, params)
        
    def department_grades(self, account_id, term_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.department_grades
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/analytics/terms/:term_id/grades
            url:GET|/api/v1/accounts/:account_id/analytics/current/grades
            url:GET|/api/v1/accounts/:account_id/analytics/completed/grades

        
        Module: Analytics
        Function Description: Get department-level grade data


        Request Example: 
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/current/grades \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/completed/grades \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/terms/<term_id>/grades \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "0": 95,
              "1": 1,
              "2": 0,
              "3": 0,
              ...
              "93": 125,
              "94": 110,
              "95": 142,
              "96": 157,
              "97": 116,
              "98": 85,
              "99": 63,
              "100": 190
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/analytics/terms/{term_id}/grades'
        return self.request(method, api, params)
        
    def department_statistics(self, account_id, term_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.department_statistics
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/analytics/terms/:term_id/statistics
            url:GET|/api/v1/accounts/:account_id/analytics/current/statistics
            url:GET|/api/v1/accounts/:account_id/analytics/completed/statistics

        
        Module: Analytics
        Function Description: Get department-level statistics


        Request Example: 
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/current/statistics \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/completed/statistics \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/terms/<term_id>/statistics \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "courses": 27,
              "subaccounts": 3,
              "teachers": 36,
              "students": 418,
              "discussion_topics": 77,
              "media_objects": 219,
              "attachments": 1268,
              "assignments": 290,
            }
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/analytics/terms/{term_id}/statistics'
        return self.request(method, api, params)
        
    def department_statistics_by_subaccount(self, account_id, term_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.department_statistics_by_subaccount
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/analytics/terms/:term_id/statistics_by_subaccount
            url:GET|/api/v1/accounts/:account_id/analytics/current/statistics_by_subaccount
            url:GET|/api/v1/accounts/:account_id/analytics/completed/statistics_by_subaccount

        
        Module: Analytics
        Function Description: Get department-level statistics, broken down by subaccount


        Request Example: 
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/current/statistics_by_subaccount \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/completed/statistics_by_subaccount \
                -H 'Authorization: Bearer <token>'
            
            curl https://<canvas>/api/v1/accounts/<account_id>/analytics/terms/<term_id>/statistics_by_subaccount \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {"accounts": [
              {
                "name": "some string",
                "id": 188,
                "courses": 27,
                "teachers": 36,
                "students": 418,
                "discussion_topics": 77,
                "media_objects": 219,
                "attachments": 1268,
                "assignments": 290,
              }
            ]}
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/analytics/terms/{term_id}/statistics_by_subaccount'
        return self.request(method, api, params)
        
    def course_participation(self, course_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.course_participation
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/activity

        
        Module: Analytics
        Function Description: Get course-level participation data


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/activity \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            [
              {
                "date": "2012-01-24",
                "participations": 3,
                "views": 10
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/activity'
        return self.request(method, api, params)
        
    def course_assignments(self, course_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.course_assignments
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/assignments

        
        Module: Analytics
        Function Description: Get course-level assignment data

        Parameter Desc:
            async | |boolean |If async is true, then the course_assignments call can happen asynch- ronously and MAY return a response containing a progress_url key instead of an assignments array. If it does, then it is the caller’s responsibility to poll the API again to see if the progress is complete. If the data is ready (possibly even on the first async call) then it will be passed back normally, as documented in the example response.

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/assignments \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            [
              {
                "assignment_id": 1234,
                "title": "Assignment 1",
                "points_possible": 10,
                "due_at": "2012-01-25T22:00:00-07:00",
                "unlock_at": "2012-01-20T22:00:00-07:00",
                "muted": false,
                "min_score": 2,
                "max_score": 10,
                "median": 7,
                "first_quartile": 4,
                "third_quartile": 8,
                "tardiness_breakdown": {
                  "on_time": 0.75,
                  "missing": 0.1,
                  "late": 0.15
                }
              },
              {
                "assignment_id": 1235,
                "title": "Assignment 2",
                "points_possible": 15,
                "due_at": "2012-01-26T22:00:00-07:00",
                "unlock_at": null,
                "muted": true,
                "min_score": 8,
                "max_score": 8,
                "median": 8,
                "first_quartile": 8,
                "third_quartile": 8,
                "tardiness_breakdown": {
                  "on_time": 0.65,
                  "missing": 0.12,
                  "late": 0.23
                  "total": 275
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/assignments'
        return self.request(method, api, params)
        
    def course_student_summaries(self, course_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.course_student_summaries
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/student_summaries

        
        Module: Analytics
        Function Description: Get course-level student summary data

        Parameter Desc:
            sort_column | |string |The order results in which results are returned.  Defaults to `name`.                                   Allowed values: name, name_descending, score, score_descending, participations, participations_descending, page_views, page_views_descending
            student_id  | |string |If set, returns only the specified student.

        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/student_summaries \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            [
              {
                "id": 2346,
                "page_views": 351,
                "page_views_level": "1"
                "max_page_view": 415,
                "participations": 1,
                "participations_level": "3",
                "max_participations": 10,
                "tardiness_breakdown": {
                  "total": 5,
                  "on_time": 3,
                  "late": 0,
                  "missing": 2,
                  "floating": 0
                }
              },
              {
                "id": 2345,
                "page_views": 124,
                "participations": 15,
                "tardiness_breakdown": {
                  "total": 5,
                  "on_time": 1,
                  "late": 2,
                  "missing": 3,
                  "floating": 0
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/student_summaries'
        return self.request(method, api, params)
        
    def student_in_course_participation(self, course_id, student_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.student_in_course_participation
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/users/:student_id/activity

        
        Module: Analytics
        Function Description: Get user-in-a-course-level participation data


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/users/<user_id>/activity \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "page_views": {
                "2012-01-24T13:00:00-00:00": 19,
                "2012-01-24T14:00:00-00:00": 13,
                "2012-01-27T09:00:00-00:00": 23
              },
              "participations": [
                {
                  "created_at": "2012-01-21T22:00:00-06:00",
                  "url": "https://canvas.example.com/path/to/canvas",
                },
                {
                  "created_at": "2012-01-27T22:00:00-06:00",
                  "url": "https://canvas.example.com/path/to/canvas",
                }
              ]
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/users/{student_id}/activity'
        return self.request(method, api, params)
        
    def student_in_course_assignments(self, course_id, student_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.student_in_course_assignments
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/users/:student_id/assignments

        
        Module: Analytics
        Function Description: Get user-in-a-course-level assignment data


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/users/<user_id>/assignments \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            [
              {
                "assignment_id": 1234,
                "title": "Assignment 1",
                "points_possible": 10,
                "due_at": "2012-01-25T22:00:00-07:00",
                "unlock_at": "2012-01-20T22:00:00-07:00",
                "muted": false,
                "min_score": 2,
                "max_score": 10,
                "median": 7,
                "first_quartile": 4,
                "third_quartile": 8,
                "module_ids": [
                    1,
                    2
                ],
                "submission": {
                  "posted_at": "2012-01-23T20:00:00-07:00",
                  "submitted_at": "2012-01-22T22:00:00-07:00",
                  "score": 10
                }
              },
              {
                "assignment_id": 1235,
                "title": "Assignment 2",
                "points_possible": 15,
                "due_at": "2012-01-26T22:00:00-07:00",
                "unlock_at": null,
                "muted": true,
                "min_score": 8,
                "max_score": 8,
                "median": 8,
                "first_quartile": 8,
                "third_quartile": 8,
                "module_ids": [
                    1
                ],
                "submission": {
                  "posted_at": null,
                  "submitted_at": "2012-01-22T22:00:00-07:00"
                }
              }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/users/{student_id}/assignments'
        return self.request(method, api, params)
        
    def student_in_course_messaging(self, course_id, student_id, params={}):
        """
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.analytics_api.student_in_course_messaging
        
        Scope:
            url:GET|/api/v1/courses/:course_id/analytics/users/:student_id/communication

        
        Module: Analytics
        Function Description: Get user-in-a-course-level messaging data


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/analytics/users/<user_id>/communication \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "2012-01-24":{
                "instructorMessages":1,
                "studentMessages":2
              },
              "2012-01-27":{
                "studentMessages":1
              }
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/analytics/users/{student_id}/communication'
        return self.request(method, api, params)
        