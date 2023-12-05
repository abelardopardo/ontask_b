from .res import *

class Account(Res):
  
  # A paginated list of accounts that the current user can view or manage. 
  # Typically, students and even teachers will get an empty list in response, 
  # only account admins can view the accounts that they are in.
  # @param params 
  # {
  #   'include[]': ['lti_guid', 'registration_settings', 'services']
  # }
  # lti_guid: the ‘tool_consumer_instance_guid’ that will be sent for this account on LTI launches
  # registration_settings: returns info about the privacy policy and terms of use
  # services: returns services and whether they are enabled (requires account management permissions)
  def listaccounts(self, params = {}):
    method = 'get'
    api = '/api/v1/accounts'
    return self.request(method, api, params)
  
  # A paginated list of accounts where the current user has permission to 
  # create or manage courses. List will be empty for students and teachers 
  # as only admins can view which accounts they are in.
  # 
  # Returns a list of Account objects
  def get_manageable_accounts(self):
    method = 'get'
    api = '/api/v1/manageable_accounts'
    return self.request(method, api)

  # Retrieve information on an individual account, given by id or sis sis_account_id.
  # Returns an Account object
  def getasingleaccount(self, id):
    method = 'GET'
    api =f'/api/v1/accounts/{id}'
    return self.request(method, api)
  
  # Returns settings for the specified account as a JSON object. 
  # The caller must be an Account admin with the manage_account_settings permission.
  def get_settings(self, account_id):
    method = 'GET'
    api = f'/api/v1/accounts/{account_id}/settings'
    return self.request(method, api)

  # Returns permission information for the calling user and the given account. 
  # You may use ‘self` as the account id to check permissions against the domain 
  # root account. The caller must have an account role or admin (teacher/TA/designer) 
  # enrollment in a course in the account.
  # @param params
  # permissions[]		string	
  # {
  #   'permissions[]':['manage_account_memberships', 'become_user']
  # } 
  #List of permissions to check against the authenticated user. Permission names are documented in the Create a role endpoint.
  def get_permissions(self, account_id, params = {}):
    method = 'GET'
    api = f'/api/v1/accounts/{account_id}/permissions'
    return self.request(method, api, params)
  
  # List accounts that are sub-accounts of the given account.
  # @param params
  #   {recursive: boolean}
  #  true: the entire account tree underneath this account will be returned (though still paginated). 
  #  false, only direct sub-accounts of this account will be returned. Defaults to false.
  def get_sub_accounts(self, account_id, params = {}):
    method = 'get'
    api = f'/api/v1/accounts/{account_id}/sub_accounts'
    return self.request(method, api, params)
  
  # Returns the terms of service for that account
  # Returns a TermsOfService object
  def get_term_of_service(self, account_id):
    method = 'GET'
    api = f'/api/v1/accounts/{account_id}/terms_of_service'
    return self.request(method, api)
  
  #GET /api/v1/accounts/:account_id/help_links
  def get_help_links(self, account_id):
    method = 'GET'
    api = f'/api/v1/accounts/{account_id}/help_links'
    return self.request(method, api)
    
  # GET /api/v1/manually_created_courses_account
  def get_manually_created_courses_account(self):
    method = 'GET'
    api = '/api/v1/manually_created_courses_account'
    return self.request(method, api)
  
  # Retrieve a paginated list of courses in this account.
  # @param
  # more information refer to 
  # https://canvas.instructure.com/doc/api/accounts.html#method.accounts.courses_api
  # {
  #    'with_enrollments': True,
  #    'enrollment_type[]': ['teacher', 'student', 'ta', 'observer', 'designer'],
  #    'published': True,
  #    'completed': True,
  #    'blueprint': True,
  #    'blueprint_associated': True,
  #    'public': True,
  #    'by_teachers[]': [id of teachers],
  #    'by_subaccounts[]': [id of subaccount],
  #    'hide_enrollmentless_courses': True,
  #    'state[]': ['created', 'claimed', 'available', 'completed', 'deleted', 'all'],
  #    'enrollment_term_id': None,
  #    'search_term': None,
  #    'include[]': ['syllabus_body', 'term', 'course_progress', 'storage_quota_used_mb', 'total_students', 'teachers', 'account_name', 'concluded'],
  #    'sort': 'course_name'/'sis_course_id'/'teacher'/'account_name',
  #    'order': 'asc'/'desc',
  #    'search_by': 'course'/'teacher',
  #    'starts_before': 'YYYY-MM-DDTHH:MM:SSZ.',
  #    'ends_after': 'YYYY-MM-DDTHH:MM:SSZ.',
  #    'homeroom': True
  # }
  def get_active_courses(self, account_id, params = {}):
    method = 'GET'
    api = f'/api/v1/accounts/{account_id}/courses'
    return self.request(method, api, params)
  
  # @param
  # {
  #  'account[name]': '',
  #  'account[sis_account_id]':
  #  'account[default_time_zone]':
  #  'account[default_storage_quota_mb]':
  #  'account[default_user_storage_quota_mb]':
  #  'account[default_group_storage_quota_mb]':
  #  'account[course_template_id]':
  #  'account[settings][restrict_student_past_view][value]':
  #  'account[settings][restrict_student_past_view][locked]':
  #  'account[settings][restrict_student_future_view][value]':
  #  'account[settings][microsoft_sync_enabled]':
  #  'account[settings][microsoft_sync_tenant]':
  #  'account[settings][microsoft_sync_login_attribute]':
  #  'account[settings][microsoft_sync_login_attribute_suffix]':
  #  'account[settings][microsoft_sync_remote_attribute]':
  #  'account[settings][restrict_student_future_view][locked]':
  #  'account[settings][lock_all_announcements][value]':
  #  'account[settings][lock_all_announcements][locked]':
  #  'account[settings][usage_rights_required][value]':
  #  'account[settings][usage_rights_required][locked]':
  #  'account[settings][restrict_student_future_listing][value]':
  #  'account[settings][restrict_student_future_listing][locked]':
  #  'account[settings][conditional_release][value]':
  #  'account[settings][conditional_release][locked]':
  #  'override_sis_stickiness':
  #  'account[settings][lock_outcome_proficiency][value]':
  #  'account[lock_outcome_proficiency][locked]':
  #  'account[settings][lock_proficiency_calculation][value]':
  #  'account[lock_proficiency_calculation][locked]':
  #  'account[services]':
  # }
  def update_account(self, id, params):
    method = 'PUT'
    api = f'/api/v1/accounts/{id}'
    return self.request(method, api, params)

  # Delete a user record from a Canvas root account. If a user is 
  # associated with multiple root accounts (in a multi-tenant instance of Canvas), 
  # this action will NOT remove them from the other accounts.
  #
  # WARNING: This API will allow a user to remove themselves from the 
  # account. If they do this, they won’t be able to make API calls or 
  # log into Canvas at that account.
  def delete_user(self, account_id, user_id):
    method = 'DELETE'
    api = f'/api/v1/accounts/{account_id}/users/{user_id}'
    return self.request(method, api)

  # Add a new sub-account to a given account.
  # @param params
  # {
  #   'account[name]': 'test_sub_account',
  #   'account[sis_account_id]': 'test_sub_account_sis_id',
  #   'account[default_storage_quota_mb]': 500,
  #   'account[default_user_storage_quota_mb]': 20,
  #   'account[default_group_storage_quota_mb]':100
  # }
  def create_sub_account(self, account_id, params):
    method = 'POST'
    api = f'/api/v1/accounts/{account_id}/sub_accounts'
    return self.request(method, api, params)

  # DELETE /api/v1/accounts/:account_id/sub_accounts/:id
  # Cannot delete an account with active courses or active sub_accounts. Cannot delete a root_account
  def delete_account(self, account_id, sub_account_id):
    method = 'DELETE'
    api = f'/api/v1/accounts/{account_id}/sub_accounts/{sub_account_id}'
    return self.request(method, api)
