from .etc.conf import *
from .res import *

class NotificationPreferences(Res):
    def index(self, user_id, communication_channel_id, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.index
        
        Scope:
            url:GET|/api/v1/users/:user_id/communication_channels/:communication_channel_id/notification_preferences
            url:GET|/api/v1/users/:user_id/communication_channels/:type/:address/notification_preferences

        
        Module: Notification Preferences
        Function Description: List preferences

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/communication_channels/{communication_channel_id}/notification_preferences'
        return self.request(method, api, params)
        
    def category_index(self, user_id, communication_channel_id, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#category_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.category_index
        
        Scope:
            url:GET|/api/v1/users/:user_id/communication_channels/:communication_channel_id/notification_preference_categories

        
        Module: Notification Preferences
        Function Description: List of preference categories

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/communication_channels/{communication_channel_id}/notification_preference_categories'
        return self.request(method, api, params)
        
    def show(self, user_id, communication_channel_id, notification, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.show
        
        Scope:
            url:GET|/api/v1/users/:user_id/communication_channels/:communication_channel_id/notification_preferences/:notification
            url:GET|/api/v1/users/:user_id/communication_channels/:type/:address/notification_preferences/:notification

        
        Module: Notification Preferences
        Function Description: Get a preference

        """
        method = "GET"
        api = f'/api/v1/users/{user_id}/communication_channels/{communication_channel_id}/notification_preferences/{notification}'
        return self.request(method, api, params)
        
    def update(self, communication_channel_id, notification, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.update
        
        Scope:
            url:PUT|/api/v1/users/self/communication_channels/:communication_channel_id/notification_preferences/:notification
            url:PUT|/api/v1/users/self/communication_channels/:type/:address/notification_preferences/:notification

        
        Module: Notification Preferences
        Function Description: Update a preference

        Parameter Desc:
            notification_preferences[frequency] |Required |string |The desired frequency for this notification
        """
        method = "PUT"
        api = f'/api/v1/users/self/communication_channels/{communication_channel_id}/notification_preferences/{notification}'
        return self.request(method, api, params)
        
    def update_preferences_by_category(self, communication_channel_id, category, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#update_preferences_by_category,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.update_preferences_by_category
        
        Scope:
            url:PUT|/api/v1/users/self/communication_channels/:communication_channel_id/notification_preference_categories/:category

        
        Module: Notification Preferences
        Function Description: Update preferences by category

        Parameter Desc:
            category                            |         |string |The name of the category. Must be parameterized (e.g. The category `Course Content` should be `course_content`)
            notification_preferences[frequency] |Required |string |The desired frequency for each notification in the category
        """
        method = "PUT"
        api = f'/api/v1/users/self/communication_channels/{communication_channel_id}/notification_preference_categories/{category}'
        return self.request(method, api, params)
        
    def update_all(self, communication_channel_id, params={}):
        """
        Source Code:
            Code: NotificationPreferencesController#update_all,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/notification_preferences_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.notification_preferences.update_all
        
        Scope:
            url:PUT|/api/v1/users/self/communication_channels/:communication_channel_id/notification_preferences
            url:PUT|/api/v1/users/self/communication_channels/:type/:address/notification_preferences

        
        Module: Notification Preferences
        Function Description: Update multiple preferences

        Parameter Desc:
            notification_preferences[<X>][frequency] |Required |string |The desired frequency for <X> notification
        """
        method = "PUT"
        api = f'/api/v1/users/self/communication_channels/{communication_channel_id}/notification_preferences'
        return self.request(method, api, params)
        