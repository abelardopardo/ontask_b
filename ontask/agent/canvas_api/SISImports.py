from .etc.conf import *
from .res import *

class SISImports(Res):
    def index(self, account_id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#index,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.index
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sis_imports

        
        Module: SIS Imports
        Function Description: Get SIS import list

        Parameter Desc:
            created_since    | |DateTime |If set, only shows imports created after the specified date (use ISO8601 format)
            created_before   | |DateTime |If set, only shows imports created before the specified date (use ISO8601 format)
            workflow_state[] | |string   |If set, only returns imports that are in the given state.                                          Allowed values: initializing, created, importing, cleanup_batch, imported, imported_with_messages, aborted, failed, failed_with_messages, restoring, partially_restored, restored
        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sis_imports'
        return self.request(method, api, params)
        
    def importing(self, account_id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#importing,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.importing
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sis_imports/importing

        
        Module: SIS Imports
        Function Description: Get the current importing SIS import

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sis_imports/importing'
        return self.request(method, api, params)
        
    def create(self, account_id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#create,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.create
        
        Scope:
            url:POST|/api/v1/accounts/:account_id/sis_imports

        
        Module: SIS Imports
        Function Description: Import SIS data

        Parameter Desc:
            import_type                       | |string  |Choose the data format for reading SIS data. With a standard Canvas install, this option can only be ‘instructure_csv’, and if unprovided, will be assumed to be so. Can be part of the query string.
            attachment                        | |string  |There are two ways to post SIS import data - either via a multipart/form-data form-field-style attachment, or via a non-multipart raw post request.                                                          ‘attachment’ is required for multipart/form-data style posts. Assumed to be SIS data from a file upload form field named ‘attachment’.                                                          Examples:                                                          curl -F attachment=@<filename> -H "Authorization: Bearer <token>" \                                                              https://<canvas>/api/v1/accounts/<account_id>/sis_imports.json?import_type=instructure_csv                                                          If you decide to do a raw post, you can skip the ‘attachment’ argument, but you will then be required to provide a suitable Content-Type header. You are encouraged to also provide the ‘extension’ argument.                                                          Examples:                                                          curl -H 'Content-Type: application/octet-stream' --data-binary @<filename>.zip \                                                              -H "Authorization: Bearer <token>" \                                                              https://<canvas>/api/v1/accounts/<account_id>/sis_imports.json?import_type=instructure_csv&extension=zip                                                          curl -H 'Content-Type: application/zip' --data-binary @<filename>.zip \                                                              -H "Authorization: Bearer <token>" \                                                              https://<canvas>/api/v1/accounts/<account_id>/sis_imports.json?import_type=instructure_csv                                                          curl -H 'Content-Type: text/csv' --data-binary @<filename>.csv \                                                              -H "Authorization: Bearer <token>" \                                                              https://<canvas>/api/v1/accounts/<account_id>/sis_imports.json?import_type=instructure_csv                                                          curl -H 'Content-Type: text/csv' --data-binary @<filename>.csv \                                                              -H "Authorization: Bearer <token>" \                                                              https://<canvas>/api/v1/accounts/<account_id>/sis_imports.json?import_type=instructure_csv&batch_mode=1&batch_mode_term_id=15                                                          If the attachment is a zip file, the uncompressed file(s) cannot be 100x larger than the zip, or the import will fail. For example, if the zip file is 1KB but the total size of the uncompressed file(s) is 100KB or greater the import will fail. There is a hard cap of 50 GB.
            extension                         | |string  |Recommended for raw post request style imports. This field will be used to distinguish between zip, xml, csv, and other file format extensions that would usually be provided with the filename in the multipart post request scenario. If not provided, this value will be inferred from the Content-Type, falling back to zip-file format if all else fails.
            batch_mode                        | |boolean |If set, this SIS import will be run in batch mode, deleting any data previously imported via SIS that is not present in this latest import. See the SIS CSV Format page for details. Batch mode cannot be used with diffing.
            batch_mode_term_id                | |string  |Limit deletions to only this term. Required if batch mode is enabled.
            multi_term_batch_mode             | |boolean |Runs batch mode against all terms in terms file. Requires change_threshold.
            skip_deletes                      | |boolean |When set the import will skip any deletes. This does not account for objects that are deleted during the batch mode cleanup process.
            override_sis_stickiness           | |boolean |Default is true. If false, any fields containing `sticky` changes will not be updated. See SIS CSV Format documentation for information on which fields can have SIS stickiness
            add_sis_stickiness                | |boolean |This option, if present, will process all changes as if they were UI changes. This means that `stickiness` will be added to changed fields. This option is only processed if ‘override_sis_stickiness’ is also provided.
            clear_sis_stickiness              | |boolean |This option, if present, will clear `stickiness` from all fields touched by this import. Requires that ‘override_sis_stickiness’ is also provided. If ‘add_sis_stickiness’ is also provided, ‘clear_sis_stickiness’ will overrule the behavior of ‘add_sis_stickiness’
            update_sis_id_if_login_claimed    | |boolean |This option, if present, will override the old (or non-existent) non-matching SIS ID with the new SIS ID in the upload, if a pseudonym is found from the login field and the SIS ID doesn’t match.
            diffing_data_set_identifier       | |string  |If set on a CSV import, Canvas will attempt to optimize the SIS import by comparing this set of CSVs to the previous set that has the same data set identifier, and only applying the difference between the two. See the SIS CSV Format documentation for more details. Diffing cannot be used with batch_mode
            diffing_remaster_data_set         | |boolean |If true, and diffing_data_set_identifier is sent, this SIS import will be part of the data set, but diffing will not be performed. See the SIS CSV Format documentation for details.
            diffing_drop_status               | |string  |If diffing_drop_status is passed, this SIS import will use this status for enrollments that are not included in the sis_batch. Defaults to ‘deleted’                                                          Allowed values: deleted, completed, inactive
            batch_mode_enrollment_drop_status | |string  |If batch_mode_enrollment_drop_status is passed, this SIS import will use this status for enrollments that are not included in the sis_batch. This will have an effect if multi_term_batch_mode is set. Defaults to ‘deleted’ This will still mark courses and sections that are not included in the sis_batch as deleted, and subsequently enrollments in the deleted courses and sections as deleted.                                                          Allowed values: deleted, completed, inactive
            change_threshold                  | |integer |If set with batch_mode, the batch cleanup process will not run if the number of items deleted is higher than the percentage set. If set to 10 and a term has 200 enrollments, and batch would delete more than 20 of the enrollments the batch will abort before the enrollments are deleted. The change_threshold will be evaluated for course, sections, and enrollments independently. If set with diffing, diffing will not be performed if the files are greater than the threshold as a percent. If set to 5 and the file is more than 5% smaller or more than 5% larger than the file that is being compared to, diffing will not be performed. If the files are less than 5%, diffing will be performed. The way the percent is calculated is by taking the size of the current import and dividing it by the size of the previous import. The formula used is: |(1 - current_file_size / previous_file_size)| * 100 See the SIS CSV Format documentation for more details. Required for multi_term_batch_mode.
            diff_row_count_threshold          | |integer |If set with diffing, diffing will not be performed if the number of rows to be run in the fully calculated diff import exceeds the threshold.
        """
        method = "POST"
        api = f'/api/v1/accounts/{account_id}/sis_imports'
        return self.request(method, api, params)
        
    def show(self, account_id, id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#show,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.show
        
        Scope:
            url:GET|/api/v1/accounts/:account_id/sis_imports/:id

        
        Module: SIS Imports
        Function Description: Get SIS import status

        """
        method = "GET"
        api = f'/api/v1/accounts/{account_id}/sis_imports/{id}'
        return self.request(method, api, params)
        
    def restore_states(self, account_id, id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#restore_states,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.restore_states
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/sis_imports/:id/restore_states

        
        Module: SIS Imports
        Function Description: Restore workflow_states of SIS imported items

        Parameter Desc:
            batch_mode      | |boolean |If set, will only restore items that were deleted from batch_mode.
            undelete_only   | |boolean |If set, will only restore items that were deleted. This will ignore any items that were created or modified.
            unconclude_only | |boolean |If set, will only restore enrollments that were concluded. This will ignore any items that were created or deleted.
        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/sis_imports/{id}/restore_states'
        return self.request(method, api, params)
        
    def abort(self, account_id, id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#abort,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.abort
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/sis_imports/:id/abort

        
        Module: SIS Imports
        Function Description: Abort SIS import

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/sis_imports/{id}/abort'
        return self.request(method, api, params)
        
    def abort_all_pending(self, account_id, params={}):
        """
        Source Code:
            Code: SisImportsApiController#abort_all_pending,
            Link: https://github.com/instructure/canvas-lms/blob/master/app/controllers/sis_imports_api_controller.rb
        
        API Documentation:
            https://canvas.instructure.com/doc/api/all_resources.html#method.sis_imports_api.abort_all_pending
        
        Scope:
            url:PUT|/api/v1/accounts/:account_id/sis_imports/abort_all_pending

        
        Module: SIS Imports
        Function Description: Abort all pending SIS imports

        """
        method = "PUT"
        api = f'/api/v1/accounts/{account_id}/sis_imports/abort_all_pending'
        return self.request(method, api, params)
        