from .etc.conf import *
from .res import *

class NamesandRole(Res):
    def course_index(self, course_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::NamesAndRolesController#course_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/names_and_roles_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/names_and_roles.course_index
        
        Scope:
            url:GET|/api/lti/courses/:course_id/names_and_roles

        
        Module: Names and Role
        Function Description: List Course Memberships

        Parameter Desc:
            rlid  | |string |If specified only NamesAndRoleMemberships with access to the LTI link references by this ‘rlid` will be included. Also causes the member array to be included for each returned NamesAndRoleMembership. If the `role` parameter is also present, it will be ’and-ed’ together with this parameter
            role  | |string |If specified only NamesAndRoleMemberships having this role in the given Course will be included. Value must be a fully-qualified LTI/LIS role URN. If the ‘rlid` parameter is also present, it will be ’and-ed’ together with this parameter
            limit | |string |May be used to limit the number of NamesAndRoleMemberships returned in a page. Defaults to 50.
        """
        method = "GET"
        api = f'/api/lti/courses/{course_id}/names_and_roles'
        return self.request(method, api, params)
        
    def group_index(self, group_id, params={}):
        """
        Source Code:
            Code: Lti::Ims::NamesAndRolesController#group_index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/lti/ims/names_and_roles_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.lti/ims/names_and_roles.group_index
        
        Scope:
            url:GET|/api/lti/groups/:group_id/names_and_roles

        
        Module: Names and Role
        Function Description: List Group Memberships

        Parameter Desc:
            `rlid` | |string |If specified only NamesAndRoleMemberships with access to the LTI link references by this ‘rlid` will be included. Also causes the member array to be included for each returned NamesAndRoleMembership. If the role parameter is also present, it will be ’and-ed’ together with this parameter
            role   | |string |If specified only NamesAndRoleMemberships having this role in the given Group will be included. Value must be a fully-qualified LTI/LIS role URN. Further, only purl.imsglobal.org/vocab/lis/v2/membership#Member and purl.imsglobal.org/vocab/lis/v2/membership#Manager are supported. If the ‘rlid` parameter is also present, it will be ’and-ed’ together with this parameter
            limit  | |string |May be used to limit the number of NamesAndRoleMemberships returned in a page. Defaults to 50.
        """
        method = "GET"
        api = f'/api/lti/groups/{group_id}/names_and_roles'
        return self.request(method, api, params)
        