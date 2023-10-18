from .etc.conf import *
from .res import *

class LineItems(Res):
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::LineItemsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/line_items_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/line_items.create
        
        Scope:
            url:POST|/api/lti/courses/:course_id/line_items

        
        Module: Line Items
        Function Description: Create a Line Item

        Parameter Desc:
            scoreMaximum                                       |Required |number |The maximum score for the line item. Scores created for the Line Item may exceed this value.
            label                                              |Required |string |The label for the Line Item. If no resourceLinkId is specified this value will also be used as the name of the placeholder assignment.
            resourceId                                         |         |string |A Tool Provider specified id for the Line Item. Multiple line items may share the same resourceId within a given context.
            tag                                                |         |string |A value used to qualify a line Item beyond its ids. Line Items may be queried by this value in the List endpoint. Multiple line items can share the same tag within a given context.
            resourceLinkId                                     |         |string |The resource link id the Line Item should be attached to. This value should match the LTI id of the Canvas assignment associated with the tool.
            endDateTime                                        |         |string |The ISO8601 date and time when the line item stops receiving submissions. Corresponds to the assignment’s due_at date.
            https://canvas.instructure.com/lti/submission_type |         |object |(EXTENSION) - Optional block to set Assignment Submission Type when creating a new assignment is created.                                                                                  type - ‘none’ or ‘external_tool’                                                                                  external_tool_url - Submission URL only used when type: ‘external_tool’
        """
        method = "POST"
        api = f'/api/lti/courses/{course_id}/line_items'
        return self.request(method, api, params)
        
    def update(self, course_id, id, params={}):
        """
        Source Code:
            Code: Lti::Ims::LineItemsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/line_items_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/line_items.update
        
        Scope:
            url:PUT|/api/lti/courses/:course_id/line_items/:id

        
        Module: Line Items
        Function Description: Update a Line Item

        Parameter Desc:
            scoreMaximum | |number |The maximum score for the line item. Scores created for the Line Item may exceed this value.
            label        | |string |The label for the Line Item. If no resourceLinkId is specified this value will also be used as the name of the placeholder assignment.
            resourceId   | |string |A Tool Provider specified id for the Line Item. Multiple line items may share the same resourceId within a given context.
            tag          | |string |A value used to qualify a line Item beyond its ids. Line Items may be queried by this value in the List endpoint. Multiple line items can share the same tag within a given context.
            endDateTime  | |string |The ISO8601 date and time when the line item stops receiving submissions. Corresponds to the assignment’s due_at date.
        """
        method = "PUT"
        api = f'/api/lti/courses/{course_id}/line_items/{id}'
        return self.request(method, api, params)
        
    def show(self, course_id, id, params={}):
        """
        Source Code:
            Code: Lti::Ims::LineItemsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/line_items_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/line_items.show
        
        Scope:
            url:GET|/api/lti/courses/:course_id/line_items/:id

        
        Module: Line Items
        Function Description: Show a Line Item

        Parameter Desc:
            include[] | |string |Array of additional information to include.                                 `launch_url`                                 includes the launch URL for this line item using the `https://canvas.instructure.com/lti/launch_url` extension                                 Allowed values: launch_url
        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/line_items/{id}'
        return self.request(method, api, params)
        
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::LineItemsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/line_items_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/line_items.index
        
        Scope:
            url:GET|/api/lti/courses/:course_id/line_items

        
        Module: Line Items
        Function Description: List line Items

        Parameter Desc:
            tag              | |string |If specified only Line Items with this tag will be included.
            resource_id      | |string |If specified only Line Items with this resource_id will be included.
            resource_link_id | |string |If specified only Line Items attached to the specified resource_link_id will be included.
            limit            | |string |May be used to limit the number of Line Items returned in a page
            include[]        | |string |Array of additional information to include.                                        `launch_url`                                        includes the launch URL for each line item using the `https://canvas.instructure.com/lti/launch_url` extension                                        Allowed values: launch_url
        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/line_items'
        return self.request(method, api, params)
        
    def destroy(self, course_id, id, params={}):
        """
        Source Code:
            Code: Lti::Ims::LineItemsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/line_items_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/line_items.destroy
        
        Scope:
            url:DELETE|/api/lti/courses/:course_id/line_items/:id

        
        Module: Line Items
        Function Description: Delete a Line Item

        """
        method = "DELETE"
        api = f'/api/lti/courses/{course_id}/line_items/{id}'
        return self.request(method, api, params)
        