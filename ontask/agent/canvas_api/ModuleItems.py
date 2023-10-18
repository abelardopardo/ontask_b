from .etc.conf import *
from .res import *

class ModuleItems(Res):
    def index(self, course_id, module_id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/modules/:module_id/items

        
        Module: Module Items
        Function Description: List module items

        Parameter Desc:
            include[]   | |string |If included, will return additional details specific to the content associated with each item. Refer to the Module Item specification for more details. Includes standard lock information for each item.                                   Allowed values: content_details
            search_term | |string |The partial title of the items to match and return.
            student_id  | |string |Returns module completion information for the student with this id.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items'
        return self.request(method, api, params)
        
    def show(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/modules/:module_id/items/:id

        
        Module: Module Items
        Function Description: Show module item

        Parameter Desc:
            include[]  | |string |If included, will return additional details specific to the content associated with this item. Refer to the Module Item specification for more details. Includes standard lock information for each item.                                  Allowed values: content_details
            student_id | |string |Returns module completion information for the student with this id.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}'
        return self.request(method, api, params)
        
    def create(self, course_id, module_id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/modules/:module_id/items

        
        Module: Module Items
        Function Description: Create a module item

        Parameter Desc:
            module_item[title]                             |         |string  |The name of the module item and associated content
            module_item[type]                              |Required |string  |The type of content linked to the item                                                                               Allowed values: File, Page, Discussion, Assignment, Quiz, SubHeader, ExternalUrl, ExternalTool
            module_item[content_id]                        |Required |string  |The id of the content to link to the module item. Required, except for ‘ExternalUrl’, ‘Page’, and ‘SubHeader’ types.
            module_item[position]                          |         |integer |The position of this item in the module (1-based).
            module_item[indent]                            |         |integer |0-based indent level; module items may be indented to show a hierarchy
            module_item[page_url]                          |         |string  |Suffix for the linked wiki page (e.g. ‘front-page’). Required for ‘Page’ type.
            module_item[external_url]                      |         |string  |External url that the item points to. [Required for ‘ExternalUrl’ and ‘ExternalTool’ types.
            module_item[new_tab]                           |         |boolean |Whether the external tool opens in a new tab. Only applies to ‘ExternalTool’ type.
            module_item[completion_requirement][type]      |         |string  |Completion requirement for this module item. `must_view`: Applies to all item types `must_contribute`: Only applies to `Assignment`, `Discussion`, and `Page` types `must_submit`, `min_score`: Only apply to `Assignment` and `Quiz` types `must_mark_done`: Only applies to `Assignment` and `Page` types Inapplicable types will be ignored                                                                               Allowed values: must_view, must_contribute, must_submit, must_mark_done
            module_item[completion_requirement][min_score] |         |integer |Minimum score required to complete. Required for completion_requirement type ‘min_score’.
            module_item[iframe][width]                     |         |integer |Width of the ExternalTool on launch
            module_item[iframe][height]                    |         |integer |Height of the ExternalTool on launch
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items'
        return self.request(method, api, params)
        
    def update(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/modules/:module_id/items/:id

        
        Module: Module Items
        Function Description: Update a module item

        Parameter Desc:
            module_item[title]                             | |string  |The name of the module item
            module_item[position]                          | |integer |The position of this item in the module (1-based)
            module_item[indent]                            | |integer |0-based indent level; module items may be indented to show a hierarchy
            module_item[external_url]                      | |string  |External url that the item points to. Only applies to ‘ExternalUrl’ type.
            module_item[new_tab]                           | |boolean |Whether the external tool opens in a new tab. Only applies to ‘ExternalTool’ type.
            module_item[completion_requirement][type]      | |string  |Completion requirement for this module item. `must_view`: Applies to all item types `must_contribute`: Only applies to `Assignment`, `Discussion`, and `Page` types `must_submit`, `min_score`: Only apply to `Assignment` and `Quiz` types `must_mark_done`: Only applies to `Assignment` and `Page` types Inapplicable types will be ignored                                                                       Allowed values: must_view, must_contribute, must_submit, must_mark_done
            module_item[completion_requirement][min_score] | |integer |Minimum score required to complete, Required for completion_requirement type ‘min_score’.
            module_item[published]                         | |boolean |Whether the module item is published and visible to students.
            module_item[module_id]                         | |string  |Move this item to another module by specifying the target module id here. The target module must be in the same course.
        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}'
        return self.request(method, api, params)
        
    def select_mastery_path(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#select_mastery_path,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.select_mastery_path
        
        Scope:
            url:POST|/api/v1/courses/:course_id/modules/:module_id/items/:id/select_mastery_path

        
        Module: Module Items
        Function Description: Select a mastery path

        Parameter Desc:
            assignment_set_id | |string |Assignment set chosen, as specified in the mastery_paths portion of the context module item response
            student_id        | |string |Which student the selection applies to.  If not specified, current user is implied.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}/select_mastery_path'
        return self.request(method, api, params)
        
    def destroy(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/modules/:module_id/items/:id

        
        Module: Module Items
        Function Description: Delete module item

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}'
        return self.request(method, api, params)
        
    def mark_as_done(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#mark_as_done,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.mark_as_done
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/modules/:module_id/items/:id/done

        
        Module: Module Items
        Function Description: Mark module item as done/not done

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}/done'
        return self.request(method, api, params)
        
    def item_sequence(self, course_id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#item_sequence,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.item_sequence
        
        Scope:
            url:GET|/api/v1/courses/:course_id/module_item_sequence

        
        Module: Module Items
        Function Description: Get module item sequence

        Parameter Desc:
            asset_type | |string  |The type of asset to find module sequence information for. Use the ModuleItem if it is known (e.g., the user navigated from a module item), since this will avoid ambiguity if the asset appears more than once in the module sequence.                                   Allowed values: ModuleItem, File, Page, Discussion, Assignment, Quiz, ExternalTool
            asset_id   | |integer |The id of the asset (or the url in the case of a Page)
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/module_item_sequence'
        return self.request(method, api, params)
        
    def mark_item_read(self, course_id, module_id, id, params={}):
        """
        Source Code:
            Code: ContextModuleItemsApiController#mark_item_read,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/context_module_items_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.context_module_items_api.mark_item_read
        
        Scope:
            url:POST|/api/v1/courses/:course_id/modules/:module_id/items/:id/mark_read

        
        Module: Module Items
        Function Description: Mark module item read

        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/modules/{module_id}/items/{id}/mark_read'
        return self.request(method, api, params)
        