from .etc.conf import *
from .res import *

class Bookmarks(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: Bookmarks::BookmarksController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/bookmarks/bookmarks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.bookmarks/bookmarks.index
        
        Scope:
            url:GET|/api/v1/users/self/bookmarks

        
        Module: Bookmarks
        Function Description: List bookmarks

        """
        method = "GET"
        api = f'/api/v1/users/self/bookmarks'
        return self.request(method, api, params)
        
    def create(self, params={}):
        """
        Source Code:
            Code: Bookmarks::BookmarksController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/bookmarks/bookmarks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.bookmarks/bookmarks.create
        
        Scope:
            url:POST|/api/v1/users/self/bookmarks

        
        Module: Bookmarks
        Function Description: Create bookmark

        Parameter Desc:
            name     | |string  |The name of the bookmark
            url      | |string  |The url of the bookmark
            position | |integer |The position of the bookmark. Defaults to the bottom.
            data     | |string  |The data associated with the bookmark
        """
        method = "POST"
        api = f'/api/v1/users/self/bookmarks'
        return self.request(method, api, params)
        
    def show(self, id, params={}):
        """
        Source Code:
            Code: Bookmarks::BookmarksController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/bookmarks/bookmarks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.bookmarks/bookmarks.show
        
        Scope:
            url:GET|/api/v1/users/self/bookmarks/:id

        
        Module: Bookmarks
        Function Description: Get bookmark

        """
        method = "GET"
        api = f'/api/v1/users/self/bookmarks/{id}'
        return self.request(method, api, params)
        
    def update(self, id, params={}):
        """
        Source Code:
            Code: Bookmarks::BookmarksController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/bookmarks/bookmarks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.bookmarks/bookmarks.update
        
        Scope:
            url:PUT|/api/v1/users/self/bookmarks/:id

        
        Module: Bookmarks
        Function Description: Update bookmark

        Parameter Desc:
            name     | |string  |The name of the bookmark
            url      | |string  |The url of the bookmark
            position | |integer |The position of the bookmark. Defaults to the bottom.
            data     | |string  |The data associated with the bookmark
        """
        method = "PUT"
        api = f'/api/v1/users/self/bookmarks/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: Bookmarks::BookmarksController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/bookmarks/bookmarks_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.bookmarks/bookmarks.destroy
        
        Scope:
            url:DELETE|/api/v1/users/self/bookmarks/:id

        
        Module: Bookmarks
        Function Description: Delete bookmark

        """
        method = "DELETE"
        api = f'/api/v1/users/self/bookmarks/{id}'
        return self.request(method, api, params)
        