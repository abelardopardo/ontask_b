from .etc.conf import *
from .res import *

class Favorites(Res):
    def list_favorite_courses(self, params={}):
        """
        Source Code:
            Code: FavoritesController#list_favorite_courses,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.list_favorite_courses
        
        Scope:
            url:GET|/api/v1/users/self/favorites/courses

        
        Module: Favorites
        Function Description: List favorite courses

        Parameter Desc:
            exclude_blueprint_courses | |boolean |When set, only return courses that are not configured as blueprint courses.
        """
        method = "GET"
        api = f'/api/v1/users/self/favorites/courses'
        return self.request(method, api, params)
        
    def list_favorite_groups(self, params={}):
        """
        Source Code:
            Code: FavoritesController#list_favorite_groups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.list_favorite_groups
        
        Scope:
            url:GET|/api/v1/users/self/favorites/groups

        
        Module: Favorites
        Function Description: List favorite groups

        """
        method = "GET"
        api = f'/api/v1/users/self/favorites/groups'
        return self.request(method, api, params)
        
    def add_favorite_course(self, id, params={}):
        """
        Source Code:
            Code: FavoritesController#add_favorite_course,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.add_favorite_course
        
        Scope:
            url:POST|/api/v1/users/self/favorites/courses/:id

        
        Module: Favorites
        Function Description: Add course to favorites

        Parameter Desc:
            id |Required |string |The ID or SIS ID of the course to add.  The current user must be registered in the course.
        """
        method = "POST"
        api = f'/api/v1/users/self/favorites/courses/{id}'
        return self.request(method, api, params)
        
    def add_favorite_groups(self, id, params={}):
        """
        Source Code:
            Code: FavoritesController#add_favorite_groups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.add_favorite_groups
        
        Scope:
            url:POST|/api/v1/users/self/favorites/groups/:id

        
        Module: Favorites
        Function Description: Add group to favorites

        Parameter Desc:
            id |Required |string |The ID or SIS ID of the group to add.  The current user must be a member of the group.
        """
        method = "POST"
        api = f'/api/v1/users/self/favorites/groups/{id}'
        return self.request(method, api, params)
        
    def remove_favorite_course(self, id, params={}):
        """
        Source Code:
            Code: FavoritesController#remove_favorite_course,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.remove_favorite_course
        
        Scope:
            url:DELETE|/api/v1/users/self/favorites/courses/:id

        
        Module: Favorites
        Function Description: Remove course from favorites

        Parameter Desc:
            id |Required |string |the ID or SIS ID of the course to remove
        """
        method = "DELETE"
        api = f'/api/v1/users/self/favorites/courses/{id}'
        return self.request(method, api, params)
        
    def remove_favorite_groups(self, id, params={}):
        """
        Source Code:
            Code: FavoritesController#remove_favorite_groups,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.remove_favorite_groups
        
        Scope:
            url:DELETE|/api/v1/users/self/favorites/groups/:id

        
        Module: Favorites
        Function Description: Remove group from favorites

        Parameter Desc:
            id |Required |string |the ID or SIS ID of the group to remove
        """
        method = "DELETE"
        api = f'/api/v1/users/self/favorites/groups/{id}'
        return self.request(method, api, params)
        
    def reset_course_favorites(self, params={}):
        """
        Source Code:
            Code: FavoritesController#reset_course_favorites,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.reset_course_favorites
        
        Scope:
            url:DELETE|/api/v1/users/self/favorites/courses

        
        Module: Favorites
        Function Description: Reset course favorites

        """
        method = "DELETE"
        api = f'/api/v1/users/self/favorites/courses'
        return self.request(method, api, params)
        
    def reset_groups_favorites(self, params={}):
        """
        Source Code:
            Code: FavoritesController#reset_groups_favorites,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/favorites_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.favorites.reset_groups_favorites
        
        Scope:
            url:DELETE|/api/v1/users/self/favorites/groups

        
        Module: Favorites
        Function Description: Reset group favorites

        """
        method = "DELETE"
        api = f'/api/v1/users/self/favorites/groups'
        return self.request(method, api, params)
        