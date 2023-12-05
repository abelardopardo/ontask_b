from .etc.conf import *
from .res import *

class MigrationIssues(Res):
    def index(self, account_id, content_migration_id, params={}):
        """
        Source Code:
            Code: MigrationIssuesController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/migration_issues_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.migration_issues.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues
            url:GET|/api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues
            url:GET|/api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues
            url:GET|/api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues

        
        Module: Migration Issues
        Function Description: List migration issues

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{content_migration_id}/migration_issues'
        return self.request(method, api, params)
        
    def show(self, account_id, content_migration_id, id, params={}):
        """
        Source Code:
            Code: MigrationIssuesController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/migration_issues_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.migration_issues.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues/:id
            url:GET|/api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues/:id
            url:GET|/api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues/:id
            url:GET|/api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues/:id

        
        Module: Migration Issues
        Function Description: Get a migration issue

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{content_migration_id}/migration_issues/{id}'
        return self.request(method, api, params)
        
    def update(self, account_id, content_migration_id, id, params={}):
        """
        Source Code:
            Code: MigrationIssuesController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/migration_issues_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.migration_issues.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/content_migrations/:content_migration_id/migration_issues/:id
            url:PUT|/api/v1/courses/:course_id/content_migrations/:content_migration_id/migration_issues/:id
            url:PUT|/api/v1/groups/:group_id/content_migrations/:content_migration_id/migration_issues/:id
            url:PUT|/api/v1/users/:user_id/content_migrations/:content_migration_id/migration_issues/:id

        
        Module: Migration Issues
        Function Description: Update a migration issue

        Parameter Desc:
            workflow_state |Required |string |Set the workflow_state of the issue.                                              Allowed values: active, resolved
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{content_migration_id}/migration_issues/{id}'
        return self.request(method, api, params)
        