from .etc.conf import *
from .res import *

class Pages(Res):
    def show_front_page(self, course_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#show_front_page,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.show_front_page
        
        Scope:
            url:GET|/api/v1/courses/:course_id/front_page
            url:GET|/api/v1/groups/:group_id/front_page

        
        Module: Pages
        Function Description: Show front page

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/front_page'
        return self.request(method, api, params)
        
    def duplicate(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#duplicate,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.duplicate
        
        Scope:
            url:POST|/api/v1/courses/:course_id/pages/:url_or_id/duplicate

        
        Module: Pages
        Function Description: Duplicate page

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}/duplicate'
        return self.request(method, api, params)
        
    def update_front_page(self, course_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#update_front_page,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.update_front_page
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/front_page
            url:PUT|/api/v1/groups/:group_id/front_page

        
        Module: Pages
        Function Description: Update/create front page

        Parameter Desc:
            wiki_page[title]            | |string  |The title for the new page. NOTE: changing a page’s title will change its url. The updated url will be returned in the result.
            wiki_page[body]             | |string  |The content for the new page.
            wiki_page[editing_roles]    | |string  |Which user roles are allowed to edit this page. Any combination of these roles is allowed (separated by commas).                                                    `teachers`                                                    Allows editing by teachers in the course.                                                    `students`                                                    Allows editing by students in the course.                                                    `members`                                                    For group wikis, allows editing by members of the group.                                                    `public`                                                    Allows editing by any user.                                                    Allowed values: teachers, students, members, public
            wiki_page[notify_of_update] | |boolean |Whether participants should be notified when this page changes.
            wiki_page[published]        | |boolean |Whether the page is published (true) or draft state (false).
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/front_page'
        return self.request(method, api, params)
        
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/pages
            url:GET|/api/v1/groups/:group_id/pages

        
        Module: Pages
        Function Description: List pages

        Parameter Desc:
            sort        | |string  |Sort results by this field.                                    Allowed values: title, created_at, updated_at
            order       | |string  |The sorting order. Defaults to ‘asc’.                                    Allowed values: asc, desc
            search_term | |string  |The partial title of the pages to match and return.
            published   | |boolean |If true, include only published paqes. If false, exclude published pages. If not present, do not filter on published status.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/pages'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/pages
            url:POST|/api/v1/groups/:group_id/pages

        
        Module: Pages
        Function Description: Create page

        Parameter Desc:
            wiki_page[title]            |Required |string   |The title for the new page.
            wiki_page[body]             |         |string   |The content for the new page.
            wiki_page[editing_roles]    |         |string   |Which user roles are allowed to edit this page. Any combination of these roles is allowed (separated by commas).                                                             `teachers`                                                             Allows editing by teachers in the course.                                                             `students`                                                             Allows editing by students in the course.                                                             `members`                                                             For group wikis, allows editing by members of the group.                                                             `public`                                                             Allows editing by any user.                                                             Allowed values: teachers, students, members, public
            wiki_page[notify_of_update] |         |boolean  |Whether participants should be notified when this page changes.
            wiki_page[published]        |         |boolean  |Whether the page is published (true) or draft state (false).
            wiki_page[front_page]       |         |boolean  |Set an unhidden page as the front page (if true)
            wiki_page[publish_at]       |         |DateTime |Schedule a future date/time to publish the page. This will have no effect unless the `Scheduled Page Publication` feature is enabled in the account. If a future date is supplied, the page will be unpublished and wiki_page will be ignored.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/pages'
        return self.request(method, api, params)
        
    def show(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/pages/:url_or_id
            url:GET|/api/v1/groups/:group_id/pages/:url_or_id

        
        Module: Pages
        Function Description: Show page

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}'
        return self.request(method, api, params)
        
    def update(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/pages/:url_or_id
            url:PUT|/api/v1/groups/:group_id/pages/:url_or_id

        
        Module: Pages
        Function Description: Update/create page

        Parameter Desc:
            wiki_page[title]            | |string   |The title for the new page. NOTE: changing a page’s title will change its url. The updated url will be returned in the result.
            wiki_page[body]             | |string   |The content for the new page.
            wiki_page[editing_roles]    | |string   |Which user roles are allowed to edit this page. Any combination of these roles is allowed (separated by commas).                                                     `teachers`                                                     Allows editing by teachers in the course.                                                     `students`                                                     Allows editing by students in the course.                                                     `members`                                                     For group wikis, allows editing by members of the group.                                                     `public`                                                     Allows editing by any user.                                                     Allowed values: teachers, students, members, public
            wiki_page[notify_of_update] | |boolean  |Whether participants should be notified when this page changes.
            wiki_page[published]        | |boolean  |Whether the page is published (true) or draft state (false).
            wiki_page[publish_at]       | |DateTime |Schedule a future date/time to publish the page. This will have no effect unless the `Scheduled Page Publication` feature is enabled in the account. If a future date is set and the page is already published, it will be unpublished.
            wiki_page[front_page]       | |boolean  |Set an unhidden page as the front page (if true)
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/pages/:url_or_id
            url:DELETE|/api/v1/groups/:group_id/pages/:url_or_id

        
        Module: Pages
        Function Description: Delete page

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}'
        return self.request(method, api, params)
        
    def revisions(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#revisions,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.revisions
        
        Scope:
            url:GET|/api/v1/courses/:course_id/pages/:url_or_id/revisions
            url:GET|/api/v1/groups/:group_id/pages/:url_or_id/revisions

        
        Module: Pages
        Function Description: List revisions

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}/revisions'
        return self.request(method, api, params)
        
    def show_revision(self, course_id, url_or_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#show_revision,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.show_revision
        
        Scope:
            url:GET|/api/v1/courses/:course_id/pages/:url_or_id/revisions/latest
            url:GET|/api/v1/groups/:group_id/pages/:url_or_id/revisions/latest
            url:GET|/api/v1/courses/:course_id/pages/:url_or_id/revisions/:revision_id
            url:GET|/api/v1/groups/:group_id/pages/:url_or_id/revisions/:revision_id

        
        Module: Pages
        Function Description: Show revision

        Parameter Desc:
            summary | |boolean |If set, exclude page content from results
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}/revisions/latest'
        return self.request(method, api, params)
        
    def revert(self, course_id, url_or_id, revision_id, params={}):
        """
        Source Code:
            Code: WikiPagesApiController#revert,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/wiki_pages_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.wiki_pages_api.revert
        
        Scope:
            url:POST|/api/v1/courses/:course_id/pages/:url_or_id/revisions/:revision_id
            url:POST|/api/v1/groups/:group_id/pages/:url_or_id/revisions/:revision_id

        
        Module: Pages
        Function Description: Revert to revision

        Parameter Desc:
            revision_id |Required |integer |The revision to revert to (use the List Revisions API to see available revisions)
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/pages/{url_or_id}/revisions/{revision_id}'
        return self.request(method, api, params)
        