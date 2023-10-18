from .etc.conf import *
from .res import *

class SharedBrandConfigs(Res):
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: SharedBrandConfigsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/shared_brand_configs_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.shared_brand_configs.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/shared_brand_configs

        
        Module: Shared Brand Configs
        Function Description: Share a BrandConfig (Theme)

        Parameter Desc:
            shared_brand_config[name]             |Required |string |Name to share this BrandConfig (theme) as.
            shared_brand_config[brand_config_md5] |Required |string |MD5 of brand_config to share
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/shared_brand_configs'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: SharedBrandConfigsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/shared_brand_configs_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.shared_brand_configs.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/shared_brand_configs/:id

        
        Module: Shared Brand Configs
        Function Description: Update a shared theme

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/shared_brand_configs/{id}'
        return self.request(method, api, params)
        
    def destroy(self, id, params={}):
        """
        Source Code:
            Code: SharedBrandConfigsController#destroy,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/shared_brand_configs_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.shared_brand_configs.destroy
        
        Scope:
            url:DELETE|/api/v1/shared_brand_configs/:id

        
        Module: Shared Brand Configs
        Function Description: Un-share a BrandConfig (Theme)

        """
        method = "DELETE"
        api = f'/api/v1/shared_brand_configs/{id}'
        return self.request(method, api, params)
        