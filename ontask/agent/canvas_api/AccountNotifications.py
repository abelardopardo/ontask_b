from .etc.conf import *
from .res import *

class AccountNotifications(Res):
    def user_index(self, account_id, params={}):
        """
        Source Code:
            Code: AccountNotificationsController#user_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_notifications_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_notifications.user_index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/account_notifications

        
        Module: Account Notifications
        Function Description: Index of active global notification for the user

        Parameter Desc:
            include_past | |boolean |Include past and dismissed global announcements.
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/account_notifications'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: AccountNotificationsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_notifications_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_notifications.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/account_notifications/:id

        
        Module: Account Notifications
        Function Description: Show a global notification

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/account_notifications/{id}'
        return self.request(method, api, params)
        
    def user_close_notification(self, account_id, id, params={}):
        """
        Source Code:
            Code: AccountNotificationsController#user_close_notification,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_notifications_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_notifications.user_close_notification
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/account_notifications/:id

        
        Module: Account Notifications
        Function Description: Close notification for user

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/account_notifications/{id}'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: AccountNotificationsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_notifications_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_notifications.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/account_notifications

        
        Module: Account Notifications
        Function Description: Create a global notification

        Parameter Desc:
            account_notification[subject]  |Required |string   |The subject of the notification.
            account_notification[message]  |Required |string   |The message body of the notification.
            account_notification[start_at] |Required |DateTime |The start date and time of the notification in ISO8601 format. e.g. 2014-01-01T01:00Z
            account_notification[end_at]   |Required |DateTime |The end date and time of the notification in ISO8601 format. e.g. 2014-01-01T01:00Z
            account_notification[icon]     |         |string   |The icon to display with the notification. Note: Defaults to warning.                                                                Allowed values: warning, information, question, error, calendar
            account_notification_roles[]   |         |string   |The role(s) to send global notification to.  Note:  ommitting this field will send to everyone Example:                                                                account_notification_roles: ["StudentEnrollment", "TeacherEnrollment"]

        Request Example: 
            curl -X POST -H 'Authorization: Bearer <token>' \
            https://<canvas>/api/v1/accounts/2/account_notifications \
            -d 'account_notification[subject]=New notification' \
            -d 'account_notification[start_at]=2014-01-01T00:00:00Z' \
            -d 'account_notification[end_at]=2014-02-01T00:00:00Z' \
            -d 'account_notification[message]=This is a global notification'

        Response Example: 
            {
              "subject": "New notification",
              "start_at": "2014-01-01T00:00:00Z",
              "end_at": "2014-02-01T00:00:00Z",
              "message": "This is a global notification"
            }
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/account_notifications'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: AccountNotificationsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/account_notifications_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.account_notifications.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/account_notifications/:id

        
        Module: Account Notifications
        Function Description: Update a global notification

        Parameter Desc:
            account_notification[subject]  | |string   |The subject of the notification.
            account_notification[message]  | |string   |The message body of the notification.
            account_notification[start_at] | |DateTime |The start date and time of the notification in ISO8601 format. e.g. 2014-01-01T01:00Z
            account_notification[end_at]   | |DateTime |The end date and time of the notification in ISO8601 format. e.g. 2014-01-01T01:00Z
            account_notification[icon]     | |string   |The icon to display with the notification.                                                        Allowed values: warning, information, question, error, calendar
            account_notification_roles[]   | |string   |The role(s) to send global notification to.  Note:  ommitting this field will send to everyone Example:                                                        account_notification_roles: ["StudentEnrollment", "TeacherEnrollment"]

        Request Example: 
            curl -X PUT -H 'Authorization: Bearer <token>' \
            https://<canvas>/api/v1/accounts/2/account_notifications/1 \
            -d 'account_notification[subject]=New notification' \
            -d 'account_notification[start_at]=2014-01-01T00:00:00Z' \
            -d 'account_notification[end_at]=2014-02-01T00:00:00Z' \
            -d 'account_notification[message]=This is a global notification'

        Response Example: 
            {
              "subject": "New notification",
              "start_at": "2014-01-01T00:00:00Z",
              "end_at": "2014-02-01T00:00:00Z",
              "message": "This is a global notification"
            }
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/account_notifications/{id}'
        return self.request(method, api, params)
        