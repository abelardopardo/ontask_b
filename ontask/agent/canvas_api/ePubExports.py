from .etc.conf import *
from .res import *

class ePubExports(Res):
    def index(self, params={}):
        """
        Source Code:
            Code: EpubExportsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/epub_exports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.epub_exports.index
        
        Scope:
            url:GET|/api/v1/epub_exports

        
        Module: ePub Exports
        Function Description: List courses with their latest ePub export

        """
        method = "GET"
        api = f'/api/v1/epub_exports'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: EpubExportsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/epub_exports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.epub_exports.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/epub_exports

        
        Module: ePub Exports
        Function Description: Create ePub Export

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/epub_exports'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: EpubExportsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/epub_exports_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.epub_exports.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/epub_exports/:id

        
        Module: ePub Exports
        Function Description: Show ePub export

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/epub_exports/{id}'
        return self.request(method, api, params)
        