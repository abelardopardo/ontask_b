from .etc.conf import *
from .res import *

class ContentMigrations(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations
            url:GET|/api/v1/courses/:course_id/content_migrations
            url:GET|/api/v1/groups/:group_id/content_migrations
            url:GET|/api/v1/users/:user_id/content_migrations

        
        Module: Content Migrations
        Function Description: List content migrations

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations/:id
            url:GET|/api/v1/courses/:course_id/content_migrations/:id
            url:GET|/api/v1/groups/:group_id/content_migrations/:id
            url:GET|/api/v1/users/:user_id/content_migrations/:id

        
        Module: Content Migrations
        Function Description: Get a content migration

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{id}'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/content_migrations
            url:POST|/api/v1/courses/:course_id/content_migrations
            url:POST|/api/v1/groups/:group_id/content_migrations
            url:POST|/api/v1/users/:user_id/content_migrations

        
        Module: Content Migrations
        Function Description: Create a content migration

        Parameter Desc:
            migration_type                           |Required |string  |The type of the migration. Use the Migrator endpoint to see all available migrators. Default allowed values: canvas_cartridge_importer, common_cartridge_importer, course_copy_importer, zip_file_importer, qti_converter, moodle_converter
            pre_attachment[name]                     |         |string  |Required if uploading a file. This is the first step in uploading a file to the content migration. See the File Upload Documentation for details on the file upload workflow.
            pre_attachment[*]                        |         |string  |Other file upload properties, See File Upload Documentation
            settings[file_url]                       |         |string  |A URL to download the file from. Must not require authentication.
            settings[content_export_id]              |         |string  |The id of a ContentExport to import. This allows you to import content previously exported from Canvas without needing to download and re-upload it.
            settings[source_course_id]               |         |string  |The course to copy from for a course copy migration. (required if doing course copy)
            settings[folder_id]                      |         |string  |The folder to unzip the .zip file into for a zip_file_import.
            settings[overwrite_quizzes]              |         |boolean |Whether to overwrite quizzes with the same identifiers between content packages.
            settings[question_bank_id]               |         |integer |The existing question bank ID to import questions into if not specified in the content package.
            settings[question_bank_name]             |         |string  |The question bank to import questions into if not specified in the content package, if both bank id and name are set, id will take precedence.
            settings[insert_into_module_id]          |         |integer |The id of a module in the target course. This will add all imported items (that can be added to a module) to the given module.
            settings[insert_into_module_type]        |         |string  |If provided (and insert_into_module_id is supplied), only add objects of the specified type to the module.                                                                         Allowed values: assignment, discussion_topic, file, page, quiz
            settings[insert_into_module_position]    |         |integer |The (1-based) position to insert the imported items into the course (if insert_into_module_id is supplied). If this parameter is omitted, items will be added to the end of the module.
            settings[move_to_assignment_group_id]    |         |integer |The id of an assignment group in the target course. If provided, all imported assignments will be moved to the given assignment group.
            settings[importer_skips]                 |         |Array   |Set of importers to skip, even if otherwise selected by migration settings.                                                                         Allowed values: all_course_settings, visibility_settings
            settings[import_blueprint_settings]      |         |boolean |Import the `use as blueprint course` setting as well as the list of locked items from the source course or package. The destination course must not be associated with an existing blueprint course and cannot have any student or observer enrollments.
            date_shift_options[shift_dates]          |         |boolean |Whether to shift dates in the copied course
            date_shift_options[old_start_date]       |         |Date    |The original start date of the source content/course
            date_shift_options[old_end_date]         |         |Date    |The original end date of the source content/course
            date_shift_options[new_start_date]       |         |Date    |The new start date for the content/course
            date_shift_options[new_end_date]         |         |Date    |The new end date for the source content/course
            date_shift_options[day_substitutions][X] |         |integer |Move anything scheduled for day ‘X’ to the specified day. (0-Sunday, 1-Monday, 2-Tuesday, 3-Wednesday, 4-Thursday, 5-Friday, 6-Saturday)
            date_shift_options[remove_dates]         |         |boolean |Whether to remove dates in the copied course. Cannot be used in conjunction with shift_dates.
            selective_import                         |         |boolean |If set, perform a selective import instead of importing all content. The migration will identify the contents of the package and then stop in the waiting_for_select workflow state. At this point, use the List items endpoint to enumerate the contents of the package, identifying the copy parameters for the desired content. Then call the Update endpoint and provide these copy parameters to start the import.
            select                                   |         |Hash    |For course_copy_importer migrations, this parameter allows you to select the objects to copy without using the selective_import argument and waiting_for_select state as is required for uploaded imports (though that workflow is also supported for course copy migrations). The keys are object types like ‘files’, ‘folders’, ‘pages’, etc. The value for each key is a list of object ids. An id can be an integer or a string. Multiple object types can be selected in the same call.                                                                         Allowed values: folders, files, attachments, quizzes, assignments, announcements, calendar_events, discussion_topics, modules, module_items, pages, rubrics
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/content_migrations'
        return self.request(method, api, params)
        
    def update(self, account_id, id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#update,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.update
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/content_migrations/:id
            url:PUT|/api/v1/courses/:course_id/content_migrations/:id
            url:PUT|/api/v1/groups/:group_id/content_migrations/:id
            url:PUT|/api/v1/users/:user_id/content_migrations/:id

        
        Module: Content Migrations
        Function Description: Update a content migration

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{id}'
        return self.request(method, api, params)
        
    def available_migrators(self, account_id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#available_migrators,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.available_migrators
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations/migrators
            url:GET|/api/v1/courses/:course_id/content_migrations/migrators
            url:GET|/api/v1/groups/:group_id/content_migrations/migrators
            url:GET|/api/v1/users/:user_id/content_migrations/migrators

        
        Module: Content Migrations
        Function Description: List Migration Systems

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations/migrators'
        return self.request(method, api, params)
        
    def content_list(self, account_id, id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#content_list,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.content_list
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/content_migrations/:id/selective_data
            url:GET|/api/v1/courses/:course_id/content_migrations/:id/selective_data
            url:GET|/api/v1/groups/:group_id/content_migrations/:id/selective_data
            url:GET|/api/v1/users/:user_id/content_migrations/:id/selective_data

        
        Module: Content Migrations
        Function Description: List items for selective import

        Parameter Desc:
            type | |string |The type of content to enumerate.                            Allowed values: context_modules, assignments, quizzes, assessment_question_banks, discussion_topics, wiki_pages, context_external_tools, tool_profiles, announcements, calendar_events, rubrics, groups, learning_outcomes, attachments
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/content_migrations/{id}/selective_data'
        return self.request(method, api, params)
        
    def asset_id_mapping(self, course_id, id, params={}):
        """
        Source Code:
            Code: ContentMigrationsController#asset_id_mapping,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/content_migrations_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.content_migrations.asset_id_mapping
        
        Scope:
            url:GET|/api/v1/courses/:course_id/content_migrations/:id/asset_id_mapping

        
        Module: Content Migrations
        Function Description: Get asset id mapping


        Request Example: 
            curl https://<canvas>/api/v1/courses/<course_id>/content_migrations/<id>/asset_id_mapping \
                -H 'Authorization: Bearer <token>'

        Response Example: 
            {
              "assignments": {"13": "740", "14": "741"},
              "discussion_topics": {"15": "743", "16": "744"}
            }
        """
        method = "GET"
        api = f'/api/v1/courses/{course_id}/content_migrations/{id}/asset_id_mapping'
        return self.request(method, api, params)
        