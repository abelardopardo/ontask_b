from .etc.conf import *
from .res import *

class ExternalTools(Res):
    def index(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.index
        
        Scope:
            url:GET|/api/v1/courses/:course_id/external_tools
            url:GET|/api/v1/accounts/:account_id/external_tools
            url:GET|/api/v1/groups/:group_id/external_tools

        
        Module: External Tools
        Function Description: List external tools

        Parameter Desc:
            search_term     | |string  |The partial name of the tools to match and return.
            selectable      | |boolean |If true, then only tools that are meant to be selectable are returned.
            include_parents | |boolean |If true, then include tools installed in all accounts above the current context
            placement       | |string  |The placement type to filter by.

        Request Example: 
            Return all tools at the current context as well as all tools from the parent, and filter the tools list to only those with a placement of 'editor_button'
            curl 'https://<canvas>/api/v1/courses/<course_id>/external_tools?include_parents=true&placement=editor_button' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            [
             {
               "id": 1,
               "domain": "domain.example.com",
               "url": "http://www.example.com/ims/lti",
               "consumer_key": "key",
               "name": "LTI Tool",
               "description": "This is for cool things",
               "created_at": "2037-07-21T13:29:31Z",
               "updated_at": "2037-07-28T19:38:31Z",
               "privacy_level": "anonymous",
               "custom_fields": {"key": "value"},
               "is_rce_favorite": false
               "account_navigation": {
                    "canvas_icon_class": "icon-lti",
                    "icon_url": "...",
                    "text": "...",
                    "url": "...",
                    "label": "...",
                    "selection_width": 50,
                    "selection_height":50
               },
               "assignment_selection": null,
               "course_home_sub_navigation": null,
               "course_navigation": {
                    "canvas_icon_class": "icon-lti",
                    "icon_url": "...",
                    "text": "...",
                    "url": "...",
                    "default": "disabled",
                    "enabled": "true",
                    "visibility": "public",
                    "windowTarget": "_blank"
               },
               "editor_button": {
                    "canvas_icon_class": "icon-lti",
                    "icon_url": "...",
                    "message_type": "ContentItemSelectionRequest",
                    "text": "...",
                    "url": "...",
                    "label": "...",
                    "selection_width": 50,
                    "selection_height": 50
               },
               "homework_submission": null,
               "link_selection": null,
               "migration_selection": null,
               "resource_selection": null,
               "tool_configuration": null,
               "user_navigation": null,
               "selection_width": 500,
               "selection_height": 500,
               "icon_url": "...",
               "not_selectable": false,
               "deployment_id": null
             },
             { ...  }
            ]
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/external_tools'
        return self.request(method, api, params)
        
    def generate_sessionless_launch(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#generate_sessionless_launch,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.generate_sessionless_launch
        
        Scope:
            url:GET|/api/v1/courses/:course_id/external_tools/sessionless_launch
            url:GET|/api/v1/accounts/:account_id/external_tools/sessionless_launch

        
        Module: External Tools
        Function Description: Get a sessionless launch url for an external tool.

        Parameter Desc:
            id                        | |string |The external id of the tool to launch.
            url                       | |string |The LTI launch url for the external tool.
            assignment_id             | |string |The assignment id for an assignment launch. Required if launch_type is set to `assessment`.
            module_item_id            | |string |The assignment id for a module item launch. Required if launch_type is set to `module_item`.
            launch_type               | |string |The type of launch to perform on the external tool. Placement names (eg. `course_navigation`) can also be specified to use the custom launch url for that placement; if done, the tool id must be provided.                                                 Allowed values: assessment, module_item
            resource_link_lookup_uuid | |string |The identifier to lookup a resource link.
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/external_tools/sessionless_launch'
        return self.request(method, api, params)
        
    def show(self, course_id, external_tool_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.show
        
        Scope:
            url:GET|/api/v1/courses/:course_id/external_tools/:external_tool_id
            url:GET|/api/v1/accounts/:account_id/external_tools/:external_tool_id

        
        Module: External Tools
        Function Description: Get a single external tool


        Response Example: 
            {
              "id": 1,
              "domain": "domain.example.com",
              "url": "http://www.example.com/ims/lti",
              "consumer_key": "key",
              "name": "LTI Tool",
              "description": "This is for cool things",
              "created_at": "2037-07-21T13:29:31Z",
              "updated_at": "2037-07-28T19:38:31Z",
              "privacy_level": "anonymous",
              "custom_fields": {"key": "value"},
              "account_navigation": {
                   "canvas_icon_class": "icon-lti",
                   "icon_url": "...",
                   "text": "...",
                   "url": "...",
                   "label": "...",
                   "selection_width": 50,
                   "selection_height":50
              },
              "assignment_selection": null,
              "course_home_sub_navigation": null,
              "course_navigation": {
                   "canvas_icon_class": "icon-lti",
                   "icon_url": "...",
                   "text": "...",
                   "url": "...",
                   "default": "disabled",
                   "enabled": "true",
                   "visibility": "public",
                   "windowTarget": "_blank"
              },
              "editor_button": {
                   "canvas_icon_class": "icon-lti",
                   "icon_url": "...",
                   "message_type": "ContentItemSelectionRequest",
                   "text": "...",
                   "url": "...",
                   "label": "...",
                   "selection_width": 50,
                   "selection_height": 50
              },
              "homework_submission": null,
              "link_selection": null,
              "migration_selection": null,
              "resource_selection": null,
              "tool_configuration": null,
              "user_navigation": {
                   "canvas_icon_class": "icon-lti",
                   "icon_url": "...",
                   "text": "...",
                   "url": "...",
                   "default": "disabled",
                   "enabled": "true",
                   "visibility": "public",
                   "windowTarget": "_blank"
              },
              "selection_width": 500,
              "selection_height": 500,
              "icon_url": "...",
              "not_selectable": false
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/external_tools/{external_tool_id}'
        return self.request(method, api, params)
        
    def create(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.create
        
        Scope:
            url:POST|/api/v1/courses/:course_id/external_tools
            url:POST|/api/v1/accounts/:account_id/external_tools

        
        Module: External Tools
        Function Description: Create an external tool

        Parameter Desc:
            client_id                            |Required |string  |The client id is attached to the developer key. If supplied all other parameters are unnecessary and will be ignored
            name                                 |Required |string  |The name of the tool
            privacy_level                        |Required |string  |What information to send to the external tool.                                                                     Allowed values: anonymous, name_only, public
            consumer_key                         |Required |string  |The consumer key for the external tool
            shared_secret                        |Required |string  |The shared secret with the external tool
            description                          |         |string  |A description of the tool
            url                                  |         |string  |The url to match links against. Either `url` or `domain` should be set, not both.
            domain                               |         |string  |The domain to match links against. Either `url` or `domain` should be set, not both.
            icon_url                             |         |string  |The url of the icon to show for this tool
            text                                 |         |string  |The default text to show for this tool
            custom_fields[field_name]            |         |string  |Custom fields that will be sent to the tool consumer; can be used multiple times
            is_rce_favorite                      |         |boolean |(Deprecated in favor of Add tool to RCE Favorites and Remove tool from RCE Favorites) Whether this tool should appear in a preferred location in the RCE. This only applies to tools in root account contexts that have an editor button placement.
            account_navigation[url]              |         |string  |The url of the external tool for account navigation
            account_navigation[enabled]          |         |boolean |Set this to enable this feature
            account_navigation[text]             |         |string  |The text that will show on the left-tab in the account navigation
            account_navigation[selection_width]  |         |string  |The width of the dialog the tool is launched in
            account_navigation[selection_height] |         |string  |The height of the dialog the tool is launched in
            account_navigation[display_type]     |         |string  |The layout type to use when launching the tool. Must be `full_width`, `full_width_in_context`, `in_nav_context`, `borderless`, or `default`
            user_navigation[url]                 |         |string  |The url of the external tool for user navigation
            user_navigation[enabled]             |         |boolean |Set this to enable this feature
            user_navigation[text]                |         |string  |The text that will show on the left-tab in the user navigation
            user_navigation[visibility]          |         |string  |Who will see the navigation tab. `admins` for admins, `public` or `members` for everyone. Setting this to ‘null` will remove this configuration and use the default behavior, which is `public`.                                                                     Allowed values: admins, members, public
            course_home_sub_navigation[url]      |         |string  |The url of the external tool for right-side course home navigation menu
            course_home_sub_navigation[enabled]  |         |boolean |Set this to enable this feature
            course_home_sub_navigation[text]     |         |string  |The text that will show on the right-side course home navigation menu
            course_home_sub_navigation[icon_url] |         |string  |The url of the icon to show in the right-side course home navigation menu
            course_navigation[enabled]           |         |boolean |Set this to enable this feature
            course_navigation[text]              |         |string  |The text that will show on the left-tab in the course navigation
            course_navigation[visibility]        |         |string  |Who will see the navigation tab. `admins` for course admins, `members` for students, `public` for everyone. Setting this to ‘null` will remove this configuration and use the default behavior, which is `public`.                                                                     Allowed values: admins, members, public
            course_navigation[windowTarget]      |         |string  |Determines how the navigation tab will be opened. `_blank`	Launches the external tool in a new window or tab. `_self`	(Default) Launches the external tool in an iframe inside of Canvas.                                                                     Allowed values: _blank, _self
            course_navigation[default]           |         |string  |If set to `disabled` the tool will not appear in the course navigation until a teacher explicitly enables it.                                                                     If set to `enabled` the tool will appear in the course navigation without requiring a teacher to explicitly enable it.                                                                     defaults to `enabled`                                                                     Allowed values: disabled, enabled
            course_navigation[display_type]      |         |string  |The layout type to use when launching the tool. Must be `full_width`, `full_width_in_context`, `in_nav_context`, `borderless`, or `default`
            editor_button[url]                   |         |string  |The url of the external tool
            editor_button[enabled]               |         |boolean |Set this to enable this feature
            editor_button[icon_url]              |         |string  |The url of the icon to show in the WYSIWYG editor
            editor_button[selection_width]       |         |string  |The width of the dialog the tool is launched in
            editor_button[selection_height]      |         |string  |The height of the dialog the tool is launched in
            editor_button[message_type]          |         |string  |Set this to ContentItemSelectionRequest to tell the tool to use content-item; otherwise, omit
            homework_submission[url]             |         |string  |The url of the external tool
            homework_submission[enabled]         |         |boolean |Set this to enable this feature
            homework_submission[text]            |         |string  |The text that will show on the homework submission tab
            homework_submission[message_type]    |         |string  |Set this to ContentItemSelectionRequest to tell the tool to use content-item; otherwise, omit
            link_selection[url]                  |         |string  |The url of the external tool
            link_selection[enabled]              |         |boolean |Set this to enable this feature
            link_selection[text]                 |         |string  |The text that will show for the link selection text
            link_selection[message_type]         |         |string  |Set this to ContentItemSelectionRequest to tell the tool to use content-item; otherwise, omit
            migration_selection[url]             |         |string  |The url of the external tool
            migration_selection[enabled]         |         |boolean |Set this to enable this feature
            migration_selection[message_type]    |         |string  |Set this to ContentItemSelectionRequest to tell the tool to use content-item; otherwise, omit
            tool_configuration[url]              |         |string  |The url of the external tool
            tool_configuration[enabled]          |         |boolean |Set this to enable this feature
            tool_configuration[message_type]     |         |string  |Set this to ContentItemSelectionRequest to tell the tool to use content-item; otherwise, omit
            tool_configuration[prefer_sis_email] |         |boolean |Set this to default the lis_person_contact_email_primary to prefer provisioned sis_email; otherwise, omit
            resource_selection[url]              |         |string  |The url of the external tool
            resource_selection[enabled]          |         |boolean |Set this to enable this feature. If set to false, not_selectable must also be set to true in order to hide this tool from the selection UI in modules and assignments.
            resource_selection[icon_url]         |         |string  |The url of the icon to show in the module external tool list
            resource_selection[selection_width]  |         |string  |The width of the dialog the tool is launched in
            resource_selection[selection_height] |         |string  |The height of the dialog the tool is launched in
            config_type                          |         |string  |Configuration can be passed in as CC xml instead of using query parameters. If this value is `by_url` or `by_xml` then an xml configuration will be expected in either the `config_xml` or `config_url` parameter. Note that the name parameter overrides the tool name provided in the xml
            config_xml                           |         |string  |XML tool configuration, as specified in the CC xml specification. This is required if `config_type` is set to `by_xml`
            config_url                           |         |string  |URL where the server can retrieve an XML tool configuration, as specified in the CC xml specification. This is required if `config_type` is set to `by_url`
            not_selectable                       |         |boolean |Default: false. If set to true, and if resource_selection is set to false, the tool won’t show up in the external tool selection UI in modules and assignments
            oauth_compliant                      |         |boolean |Default: false, if set to true LTI query params will not be copied to the post body.
        """
        method = "POST"
        api = f'/api/v1/courses/{course_id}/external_tools'
        return self.request(method, api, params)
        
    def update(self, course_id, external_tool_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.update
        
        Scope:
            url:PUT|/api/v1/courses/:course_id/external_tools/:external_tool_id
            url:PUT|/api/v1/accounts/:account_id/external_tools/:external_tool_id

        
        Module: External Tools
        Function Description: Edit an external tool

        """
        method = "PUT"
        api = f'/api/v1/courses/{course_id}/external_tools/{external_tool_id}'
        return self.request(method, api, params)
        
    def destroy(self, course_id, external_tool_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.destroy
        
        Scope:
            url:DELETE|/api/v1/courses/:course_id/external_tools/:external_tool_id
            url:DELETE|/api/v1/accounts/:account_id/external_tools/:external_tool_id

        
        Module: External Tools
        Function Description: Delete an external tool

        """
        method = "DELETE"
        api = f'/api/v1/courses/{course_id}/external_tools/{external_tool_id}'
        return self.request(method, api, params)
        
    def add_rce_favorite(self, account_id, id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#add_rce_favorite,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.add_rce_favorite
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/external_tools/rce_favorites/:id

        
        Module: External Tools
        Function Description: Add tool to RCE Favorites

        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/external_tools/rce_favorites/{id}'
        return self.request(method, api, params)
        
    def remove_rce_favorite(self, account_id, id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#remove_rce_favorite,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.remove_rce_favorite
        
        Scope:
            url:DELETE|/api/v1/accounts/:account_id/external_tools/rce_favorites/:id

        
        Module: External Tools
        Function Description: Remove tool from RCE Favorites

        """
        method = "DELETE"
        api = f'/api/v1/accounts/{account_id}/external_tools/rce_favorites/{id}'
        return self.request(method, api, params)
        
    def all_visible_nav_tools(self, params={}):
        """
        Source Code:
            Code: ExternalToolsController#all_visible_nav_tools,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.all_visible_nav_tools
        
        Scope:
            url:GET|/api/v1/external_tools/visible_course_nav_tools

        
        Module: External Tools
        Function Description: Get visible course navigation tools

        Parameter Desc:
            context_codes[] |Required |string |List of context_codes to retrieve visible course nav tools for (for example, course_123). Only courses are presently supported.

        Request Example: 
            curl 'https://<canvas>/api/v1/external_tools/visible_course_nav_tools?context_codes[]=course_5' \
                 -H "Authorization: Bearer <token>"

        Response Example: 
            [{
              "id": 1,
              "domain": "domain.example.com",
              "url": "http://www.example.com/ims/lti",
              "context_id": 5,
              "context_name": "Example Course",
              ...
            },
            { ...  }]
        """
        method = "GET"
        api = f'/api/v1/external_tools/visible_course_nav_tools'
        return self.request(method, api, params)
        
    def visible_course_nav_tools(self, course_id, params={}):
        """
        Source Code:
            Code: ExternalToolsController#visible_course_nav_tools,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/external_tools_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.external_tools.visible_course_nav_tools
        
        Scope:
            url:GET|/api/v1/courses/:course_id/external_tools/visible_course_nav_tools

        
        Module: External Tools
        Function Description: Get visible course navigation tools for a single course

        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/external_tools/visible_course_nav_tools'
        return self.request(method, api, params)
        