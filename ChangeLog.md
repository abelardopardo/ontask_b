## 6.1 ()

### Added

- New functionality to execute actions incrementally over a time window (Issue #160)

- Link to the table views in the top menu

### Fixed

- Scheduled action editing now remembers those items selected for exclusion

- Scheduled executions are now properly reflected in the last_executed (Issue #157)

## 6.0 (2019-09-06)

### Added

- Two new action types to send emails or JSON objects containing the content of a selected column  (Issue #158)

- Major architectural rewrite to consolidate the tool into a single app instead of handling several apps. Tables are now under a single application.

- Additional test suites for the new actions.

### Changed

- Updated localization files

- Re-enabled URL to access surveys through LTI

- Email lists are now space separated instead of comma separated.

- Scheduling forms so that they can robustly go back and forth from item selection page

- Rewriting of the run action forms to make them more robust when canceling operations.

- Caching the formula in text mode in conditions to improve response time

- Booleans are now manipulated as text with (True, False) as values to allow for null detection

- Use console for messages under development

### Fixed

- Error when using extra parameters with the loggers

- Added scrollable dropdown menus (Issue #159)

- Attribute "shared" can no be manipulated through the Admin menu (Issue #17)

- Error when selecting the first column to sort the data in a table

## 5.2.2 (2019-08-10)

### Fixed

- Error when invoking scheduled actions (Issue #153)

### Changed

- Upgraded requirements (Django and other libraries)

## 5.2.1 (2019-08-02)

### Changed

- Decoupled documentation building from platform configuration

## 5.2.0 (2019-08-01)

### Added

- Role handling configuration for LTI (deciding which role is Instructor)

### Changed

- Moved admin URL

- Improved HTML rendering for visualizations.

### Fixed

- Mistake when cloning conditions from another action

- Error in function to search value in table

- Error when cacheing page chunks without the language_code

- Fixed incorrect error reporting when uploading an incorrect file

- Fixed error when using empty/not-empty operator in conditions

- Fixed error in decorator in the case of a locked workflow

- Fixed count of all false rows

- Fixed error when invoking scheduled tasks (Issue #153)

- Fixed error when handling payload management in Oauth2 (Issue #152)

- Fixed inconsistencies in the documentation regarding paths in the tooltips

## 5.1.4 (2019-07-05)

### Changed

- Upgrade django version to avoid vulnerability

### Fixed

- Mistake when cloning conditions from another action

- Error in function to search value in table

- Error when cacheing page chunks without the language_code

- Fixed incorrect error reporting when uploading an incorrect file

- Fixed error when using empty/not-empty operator in conditions

- Fixed error in decorator in the case of a locked workflow

- Fixed count of all false rows

## 5.1.3 (2019-06-16)

### Fixed

- Error when using conditions in the personalised text editor

- Removed dependency from Jupyter, ipython and parso (due to vulnerability)

## 5.1.2 (2019-06-14)

### Fixed

- Error when exporting a workflow with no actions.

## 5.1.1 (2019-06-13)

### Fixed

- Error when serving surveys to users not owning the workflow

## 5.1.0 (2019-06-11)

### Added

- Option to export workflow after JSON action run

- New page for system administratio to handle plugins

- Admin page to manage plugins (enable them for execution)

- Mark workflows as favourite and show in separate area

### Changed

- Model name for PluginRegistry

- Survey editor now allows the key column to be unset.

### Fixed

- Error when handling the workflow row to user translation

- Error when exporting workflow after action run

## 5.0.1 (2019-06-08)

### Changed

- Requires Django 2.2.2

### Fixed

- Error preventing import of duplicate workflow name for different users.

## 5 (2019-06-07)

### Added 

- The presence of a question in a survey can be controlled by a condition. Surveys now have conditions that can be assigned to questions.

- Support to deploy a development server using docker (Issue #81)

- Timeline visualization of action executions. In a single page the timeline of the execution of either all the actions, or a single one.

- Support for CORS Headers (using library django-cors-headers)

### Changed

- Batch command for workflow import can now process multiple files (bulk upload of multiple workflows)

- New UI to differentiate between the execution of transformations and of statistical models.

- Refactoring of plugin infrastructure to execute arbitrary transformations and
  models
  
- Import operation now allows to either provide a workflow name for the import or use the original workflow name (stored in the file).

- Major refactoring of the code to use type hints and an more adequate division into packages. 

- Major rewriting of data frame manipulation to use direct database operations and reduce 
  the number of load/store operations from DB to Pandas.
  
### Fixed

- Error when taking the conjunction between two queryset and not using distinct

## 4.3.5 (2019-05-06)

### Fixed

- Incorrect column filter when editing (Issue #150)

## 4.3.4 (2019-04-25)

### Fixed

- Internal error while creating/editing shared users

- Error when viewing the scheduled actions

- Error in column operation button to insert formula and random row

## 4.3.3 (2019-04-24)

### Fixed

- Error when evaluating conditions

## 4.3.2 (2019-04-23)

### Fixed

- Error when exporting/importing workflows with luser field

## 4.3.1 (2019-04-22)

### Added

- Preliminary backend functionality to deploy a learner page (still under construction)

- Increase the use of cache for portions of the pages

### Changed

- Import/export operations to improve performance

- Backend management of DB queries to prefetch related relations and improve performance

### Fixed

- Error when creating an empty column of type integer 

- Legacy errors in migrations when handling some models

## 4.3 (2019-04-16)

### Added

- Read S3 buckets with possibility of providing Key/Secret

- Possibility to clone conditions from other actions

- Workflow delete now requires typing workflow name for security reasons

- Steps requiring multiple steps now have numbers at the top of the screen (suggested by University of Auckland's group a while ago)

- Functionality to reset the password (needs email configured) and to remain connected (1 month)

- Color coding to distinguish the type of columns and the type of actions

- Button to preview emails when scheduling an action for future execution

### Changed

- Editor pages to use tabs in more intuitive ways

- Added shadow to a few elements to improve UI 

- Updated dependencies to include supervisor and celery now supporting Python3

- UI using large modals to take advantage of larger screens

- Significant revamp of how the configuration file is structured

- Library dependencies are now aligned and the new version does not require Python 2.7 and 3 at the same time. Only Python 3.

### Fixed

- Incorrect number of entries shown at bottom of column page

- Error when evaluating numeric conditions in the presence of null values

- Focus now goes to the tag with invalid params in plugin execution

- Allowed the configuration of HTML email or text + html email (Issue #140)

- Error allowing a key column to loose this property through a merge (Issue #142)

- Error in serialization handling the new Condition/Column pairs

## 4.2.1 (2019-03-29)

### Changed

- Production configuration file needs USE_SSL=True to use HTTPS

- Updated localization files

## 4.2 (2019-03-27)

### Added

- Export now allows to export a workflow without a data frame

- Detection of personalized texts or JSON objects in which all conditions are false

- Function to show column statistics when creating conditions in personalized
  actions

- New plugin to round numeric column to a number of decimal places

### Fixed

- Bug when handling URL creation for row edition

- Legacy problem with Python3 numpy and pickled data

### Changed

- Upgraded requirements and propagated changes to adapt to Pandas 0.24

- Underlying models to handle conditions and columns in actions (new many to many relation)

- Switched to email_validator to validate email addresses

- Cleaner UI to insert attributes, columns, conditions in actions

## 4.1 (2019-02-27)

### Added

- Possibility of disabling the type of actions available in config file (Issue #112)
  
### Fixed

- Conditions break when renaming them (Issue #128)

- Fixed incorrect highlighting of Workflows link (Issue #127)

- Fixed localization in dataTables using only the URL field

### Changed

- Footer is now sticky to the bottom of the viewport if body is shorter (Issue #121)

- Redesigned the top bar menu to include icons and text (Issue #127)

- Moved contacts and about links only to the Login page (Issue #127)

- Moved the SQL icon in the admin profile to the right of the menu (Issue #127)

## 4.0.1 (2019-02-19)

### Fixed

- Incorrect download of table data into CSV format

- API table upload did not check for presence of key column

### Changed

- Update the chinese i18n

## 4.0 (2019-02-14)

### Fixed

- Various bugs due to the incompatibility with Python3/Django2

### Added

- Support for Python3/Django2

- New type of personalized email actions that send messages using the Canvas API

### Changed

- Datetimepicker widget changed due to incompatibilities with Django 2

- Reviewed the Chinese localization

- Major UI redesign to use more intuitive constructs and better use of screen space

- Migration to Bootstrap 4

## 3.2.1 (2018-11-21)

### Added

- Survey columns now can be queried about their null and not null status.

### Changed

- Significant changes in the documentation (more to come) to provide more activities and details in the tutorial

- Various minor cosmetic changes in the HTML structure of the pages

- Updated the version of QueryBuilder and added localization files

### Fixed

- Randomly populated columns now are guaranteed to have equal numer of elements in each partition (Issue #104)

- Bug when using the Check all box in CSV upload. It was selecting all checkboxes in the page, now only those related to column upload

- Bug allowing a workflow to loose its key column through outer merge operation. 

- Bug preventing the conditions to be clone in the actions

## 3.2.0 (2018-11-12)

### Added

- Personalized actions can now be downloaded in a ZIP with one file per message. Suitable to be used in combination with *Upload multiple feedback files in a ZIP* in [Moodle Assignments](https://docs.moodle.org/35/en/Assignment_settings#Feedback_types) (Issue #96)

### Fixed

- Error when merging data frames with key columns with different name (Issue #103)

- Error preventing the renaming of actions (Issue #101)

### Changed

- Reviewed the Chinese localization

## 3.1.0 (2018-10-31)

### Added

- Initial support for localization to Chinese

## 3.0.4 (2018-10-20)

### Changed

- Cosmetic changes in menu bar to visualise properly in mobile devices.

### Fixed

- Fixed bug that showed the spinner when an invalid field is present in a form

## 3.0.3 (2018-10-16)

### Fixed

- Misleading information shown when flushing a workflow (Iussue #97)

- Fixed bug when merging data frames using the "right" option (Issue #98)

- Fixed bug when loading/dumping dataframes with UTF-8 characters (Issue #99)

## 3.0.2 (2018-10-13)

### Fixed

- Bug preventing questions to be added to the workflow (Issue #95)

- Fixed bug in localization preventing the use of translations

## 3.0.1 (2018-09-25)

### Fixed

- Bug preventing action creation (divergence between debug/production instance)

## 3.0.0 (2018-09-24)

### Added

- Added screen to exclude emails before sending messages (Issue #66)

- Added API entry point to schedule action execution (Issue #53)

- Added operators to filter data if the cell is empty/non empty (Issue #60)

- Added additional code to remove Word markup when copy/pasting (Issue #63)

- Added functionality to create a column with either a random integer 
  (between 1 and a given number) or with a random category value.
  
- Column in action index showing when was the last time an action has been 
  executed (Issue #71) 
  
- EMAIL configuration can now be done through environment variables (Issue #84)

### Changed

- Log objects have been re-encoded to use enumeration types.

- Steps to create the actions have changed. Whe an action is created a set of
  action types are presented (Issue #72)
  
- Significant changes to the UI as suggested by University of Auckland's 
  group (Issue #74, #77):

  - Merged the home page into the login, and the workflow index is now the home
    page
    
  - Simplified the top menu removing the dataops item. It is now part of 
    every main level screen.
    
  - Actions are created now by choosing the type
  
  - New action type to send a JSON object. It will eventually evolve into one
    going through the Oauth2 cycle first.
    
  - Restructuring of the action edit pages.
  
  - Restructuring of the operations shown in the workflow index. 

### Fixed

- Bug preventing the visualisation of the API documentation.

- Fixed bug opening preview in personalized text when number of learners is 
  equal to zero (Issue #70)
  
- Fixed bug that provoked some of the scheduled actions not to be picked 
  (Issue #79)
  
- Replaced all http by https in URLs for libraries (Issue #85)

- Unable to delete filters by users sharing workflows (Issue #86 #87)

- Fixed two errors while evaluating some of the operands in the conditions 
  (Issue #88)
  
- Removed duplicate Middleware (Issue #89)

## 2.8.3 (2018-08-21)

### Changed

- Several UI changes after the review provided by University of Auckland
  
- About and Contacts link in the main page now open in separated windows (2B)
  
### Fixed

- Fixed bug accidentally introduced when committing code.

## 2.8.2 (2018-08-14)

### Fixed

- Fixed celery configuration and bug in email send function

## 2.8.1 (2018-08-11)

### Added

- Surveys can be run directly from the editor (added Run button there)

### Fixed

- Fixed a few bugs related to localisation

## 2.8.0 (2018-08-07)

### Added

- Localization and internationalization support. First language supported, 
  es-ES. There are still a few areas that need polishing, but the bulk of the
  translation is done.
   
- Boolean field in the action-in to request the questions to be shuffled when
  shown to the learners as some surveys suggest (Issue #48)
  
- Function to restrict the values in a column based on the current values. 
  Useful to manage future updates
  
- New folder containing a catalogue of surveys and its corresponding plugins 
  (if applicable)

- Added capacity to retain/forget key columns in the upload/merge steps 
  (Issue #55)
 
- Dashboard now available from the table views (and subviews)

- Script to create users in bulk with a CSV file.

- Functionality to send email now includes CC and BCC fields (Issue #57)

- Possibility to "unmark" a column as key when uploading in CSV (Issue #55)

- Preview screen now shows the value of those variables used when computing 
the personalised message (Issue #47)

### Changed

- Changed configuration scripts to take the environment file name from the 
  environment variable ENV_FILENAME (if it exists). 
  
- Additional parameters in the configuration that are taken from the ENV_FILE
  
- Show questions in Action In editor in the same order in which they are in the 
  workflow 
  
- Configuration of Summernote now precludes the use of drag and drop (Issue #63)

- Preview screen for emails now includes the total number of emails (Issue #64)

### Fixed

- Row dashboard now takes into account the subset of data considered in a view.

- Emails are now sent asynchronously through a queue (Issue #45)
  
- Subject line for emails is now properly processed in the preview it if 
  contains variables like a template (Issue #54)
  
- Fixed incorrect number comparison when providing a range (Issue #49)

- Text in the personalised messages is now processed to remove newlines that 
  break the processing (Issue #44) 
  
- Action out editor no longer allows drag & drop (Issue #25)
  
- Bug when evaluating a condition with the operand "doesn't begin with" (Issue
  #68)
  
- Bug when receiving a large volume of tracking requests (Issue #67)

## 2.7.3 (2018-06-24)

### Fixed

- Bug when checking the lock status of workflows through the API

### Added

- New functionality to check the lock status, lock and unlock workflows 
  through the API
  
### Changed

- Policy to handle workflow locks. If a session tries to access a workflow 
  locked by another session, but with the same user, access is granted. This 
  case occurs when the same account is used from two browsers (or API 
  clients). This policy is adopted because the API authentication is done 
  through Tokens (not sessions), and is needed to maintain workflow locks 
  through consecutive API calls due to the lack of a proper session object.
  
## 2.7.2 (2018-06-19)

### Fixed

- Bug preventing learner data input (Issue #46)

## 2.7.1 (2018-06-15)

### Fixed

- Bug preventing installation from scratch

## 2.7.0 (2018-06-04)

### Added

- Functionality to export and import actions alone. This is very useful to 
  simply transfer a single set of conditions or columns from one workflow to 
  another.
  
- Definition and usage of SQL connections. The definition is only available 
  for the superuser and instructors are allowed to use them in the upload/merge
  page.
 
- Use of plugins. Arbitrary transformations of a subset of the dataframe are 
  now allowed by installing python modules in a specific folder. 

### Changed

- Revamped the structure of the page to edit the action ins.

- Extended and polished documentation

## 2.6.1 (2018-05-23)

### Added

- Platform now notifies with a pop-up one minute before the session user session
  expires (Issue #31)
  
- Arrows in the table view to move columns left and right (issue #33)

### Changed

- Changed the way a merge is reported before the last step. The key columns
  now appear separately if they have different names as they will both 
  survive the merge operation (issue #39)
  
- File name when exporting a workflow now includes a date/time suffix (issue 
  #36)

- Changed HTTP headers to allow Safari to save the workflow with the right 
  extension.
   
- Conditions and filters now show the number of rows that satisfy the 
  specified condition (issue #26)

- Removed the back buttom from the page for learner data submission (issue 
  #27)  

- All columns are selected by default when uploading a new CSV (issue #28)

- Merged the options of tracking an email and adding a column in the table. 
  They are now the same option (issue #35)
  
- Active column label only appears if the column is "Disabled" by date/time 
  (issue #22)
  
- Changed wording in tooltips in the Action Out edit page to offer better 
  guidance to the new user (issue #23)
  
- Changed wording in the buttons to move columns in the workflow (issue #29)

- Excel upload does not have a sheet name by default any more (issue #38)

- Datetimes shown now without the T in between (issue #42)
  
### Fixed

- Merge procedure improved to consider the case where src and dst keys are
  different, but still src key is equal to a column in dst (issue #41)

- CSV download button in table view now correctly narrows the table to the right
  data when using a view (previously, it would download the whole table 
  regardless, issue #34)

- Column picker widget was rendered in an incorrect location (issue #21)   

- Modal windows now opening for all the operations are not closed when clicking
  outside of the area (issue #20)
  
- Fixed glitch when inserting an image in action out after using the modal
  page to edit a condition (issue #32)
  
- Fixed merge procedure to account for the corner case in which the upcoming 
  key column is matched against another existing column with a different name, 
  but the existing data frame does have a column with such name. Example: 
  Existing data frame with columns C1, C2 and C3 (C1 and C2 are keys). New 
  data frame with columns C2 and C4. The merge is done matching C1 in the 
  existing DF and C2 in the new DF. The merge now goes through and C2 is 
  updated accordingly (issue #40)
  
- Fixed how merge operation fails in the presence of NaN appearing in Key 
  columns. The merge operation now has a security check to prevent this from 
  hapenning (issue #41) 
  
## 2.6.0 (2018-05-13) 

### Added

- Possibility to change the order in which columns are shown.

- Download the table as CSV

### Changed

- Major overhaul of the documentation available when merging dataframes. When
  choosing now the merging uption, a figure and corresponding text explains the
  result of the operation.
  
- Preventing the modal window to close when clicking outside of it.

- Simplified the layout for the Action-Out screen

- Changed the name of the Workflow "Rename" button to "Edit"

- Search in tables is now case insensitive.

- End of CSV upload operation now is followed by workflow details screen

- Re-writing of the action-in screen to make it consistent with the rest of
  the application.
  
- Various navigation sequences to reduce the number of clicks

### Fixed

- AND/OR button in condition builder is now easier to differentiate.

- Misalignment of the NOT button in condition builder.

- Bug that leaked Views when table is flushed in the workflow

- Error in URL included in emails

## 2.5.1 (2018-04-21)

### Added

- Documentation on how to open the URL in OnTask to track email reading when using SAML authentication (Apache configuration)

- Tables now remember their state (number of items shown, search item)

- Documentation now has the initial set of *scenarios* to showcase the differet functionality available in the platform. This section is unfinished.

### Changed

- Column delete now returns to previous screen (table or workflow detail)

- Email preview now uses the subject text provided in the form.

- Platform now prevents concurrent sessions from the same user. If a user tries
  to access a workflow that is being used by another session in another 
  browser, the platform rejects the access until the previous session is 
  terminated by logout, or (if the browser has been closed) it expires.
  
- Removed bootstrapped Admin interface and restored the original one.

### Fixed

- Changed the update of the action out text to use a POST request and prevent
  the System Error due to the length of the text (Issues 13 and 15)
  
- Bug preventing columns to be deleted from the table view.

- Bug limiting the length of the action text when using preview (Issue 18)

- Bug limiting the search in tables to only pure string columns (unable to
  search columns with booleans that are promoted to strings)
  
- Bug when merging/updating data sets with overlapping columns. The code
  was not considering them as existing columns. Major rewriting of the
  update/merge functionality.

- Bug detecting condition names with spaces in action out text

- Bug when enforcing new data types after merge/update operation

- Bug when flushing a workflow that did not restored the selected number of 
  rows in the action filters.
  
- Bug when evaluating the condition and filter expressions in the presence of 
  None or NULL values  (Issue 14)
  
- Bug when sending emails when preview fails (Issue 16)

- Bug failing to detect a non gzip file when given to Import (Issue 11)
  
## 2.5.0 (2018-02-18)

### Added

- Visualisations

  1) For each column in the table
  
  2) For each row in the table 
  
  3) For subsets of the matrix and certain types of visualisations (tentative)
  
  These visualizations are implemented using the open-source javascript 
  library plot.ly/javascript
  
### Changed

- Folded some of the operations into a pull/down menu to simplify interface

- Rebranded the import button in the workflows page to make sure it says 
  "Workflow" and users do not think it is the link to upload data (which is 
  the first step)
   
### Fixed 

- Bug when filtering columns and obtaining a row in the table

## 2.4.0 (2017-12-18)

### Added

- Take a set of already existing columns and combine them to create a new 
  one using the following operations:
  - sum (addition)
  - prod (product)
  - max (maximum value)
  - min (minimum value)
  - mean
  - median
  - mode
  - std (standard deviation)
  - all (boolean conjunction)
  - any (boolean disjunction)

- The table now can be viewed selecting a "View" which is a set of colums and 
  a formula to filter rows. A workflow can have an arbitrary number of views.
  They are available in the Table section and can be created, edited, deleted
  and cloned.  
  
- Documentation now available in [OnTask documentation in Github.io]
(https://abelardopardo.github.io/ontask_b)

### Changed

- Removed django-auth-ldap from requirements. Instructions mention the need to
  install it if needed.
  
- Simplified operation menus. Less options visible and more tucked under 
  dropdown buttons. 
 
- Improved rendering of the action in form for data input from the learners.

- Reimplemented attribute manipulation screen to make it similar in 
  functionality to the rest
  
## 2.3.0 (2017-12-30)

### Added

- Support for LDAP integration through django-auth-ldap

- Read CSV now allows to specify number of lines at the top and
  bottom of the file to skip.
  
- Read Excel files into Table

- Read SQL queries into Table giving the parameters to connect to a DB.

### Changed

- Fixed various glicthes when sending confirmation emails and HTML email
  formatting 
  
## 2.2.0 (2017-12-23)

### Changed

- Removed the restriction of using only column, attribute and condition names
  starting with a letter followed by a letter, digit or '_'. The only 
  restriction is that the names cannot contain the characters " and '.
   
## 2.1.1 (2017-12-19)

### Changed

- Fixed bug when creating API token and session expired.

- Fixed bug preventing excel CSV files to be uploaded.

## 2.1.0 (2017-12-13)

### Added

- Edit columns from the table display

- Columns now have an active from-to window with a datetime. If they are 
  inactive, they are ignored when running Actions In
  
- URL for actions in/out now have an additional date/time window.

- Columns in the workflow can now be cloned (duplicating values)

- New app to schedule execution of actions (not fully implemented yet)

### Changed

- Fixed bug showing wrong number of (filtered) entries in AJAX generated 
  tables.

- Refined the process to clone workflows, columns, actions, conditions.

- Fixed but on import/export of actions

- Workflows can no longer be exported without the data. It does not make 
  sense because the presence of the data frame defines the columns and those 
  columns are used in all the actions. A workflow without the data would be 
  reduced only to the text in the action out. 

## 2.0.0

### Added

- Included new functionality to allow easy data entry. Data entry can be done
  as "Action In" (as opposed to Action Out for sending information). With 
  this functionality, instructors can easily enter information by hand, or 
  even collect the information from the students.
  
- Clone functionality for workflows, actions and conditions. 

- Write the documentation for the new actions.

## 1.4.0

### Changed

- Removed the use of query strings in URLs. All parameters are now path of the
  path

### Added

- Support for LTI authentication (using the django-auth-lti package). More 
information in the installation instructions.

## 1.3.0

### Changed

- Matrix is out. Table is in. Thanks Marion

- Fixed bug when importing a workflow without data frame and requesting to
  upload it.

- Fixed bug when editing actions in a workflow without data. Conditions and 
  filters were incorrectly allowed to edit.

- Polished how columns in CSV file upload are managed (internally)  

### Added

- New export functionality lets you choose which elements to include (table and
  actions)
  
- Home text next to the icon (confussing otherwise)

- Test for import/export functionality

## 1.2.2

### Added

- Additional material in the tutorial (still unfinished)

### Changed

- Fixed bug preventing the edition of columns

- Fixed bug when rendering the export done page.

## 1.2.1

### Added

- Email tracking available. Creates an extra column in the table.

### Changed

- Cosmetic changes in the import screen and the email notification

- Changed the mass email send to occur only if the host has been specified

- Documentation now includes how to install static resources

- Logs now show the payload (the whole db access)

- API to manipulate matrices now offers two versions: JSON and Pandas Pickle.
  The first one is sensitive to NaN, whereas the second maintains the data 
  frame intact (encodes NaN and NaT). The latter is recommended whenever 
  possible.

### Fixed

- Bug not showing the status of the action URL.

## 1.2.0

### Changed

- User search for sharing is now case insensitive.

- Conditions in actions appear now in the order in which they have been 
  modified

- Action raw text is now shown with line wrapping

- Revamped serializers for API and import/export to preserve NaN in data frames.

- Locked workflow now shows the user (email) locking it.

- Column table in workflow detail is now redered with DataTables (paging,
  search capacity)
  
- Fixed search functionality in table view to search all fields (despite data
  type)
  
- First version implementing row views (manual data entry). Just CRUD. No
  more functionality (still outside import/export)
  
- Added testing rig

- Added skeleton for documentation!

### Fixed

- A few bugs in import/export to guarantee isomorphism of the two

## 1.1.2

### Changed

- Handling the data frames in the import/export process using pickle to
  make sure the structure survives the process. Going to JSON nukes data
  types and NaNs are not properly handled.
  
- Added some additional events in the logs

## 1.1.1

### Added

- Workflows are now shared among users (with some operations reserverd only
  for the owner)
  
### Changed

- Fixed bug to remember step 1 in csv upload. 

- Fixed bug to require authenticated access to the API only to instructors

## 1.1.0 

### Removed

- Support for SQLite3. Now using only postgresql

- Major overhaul of code to polish bugs in all packages.

## 1.0.2 2017-10-22

### Added

- Shared workflows now have restricted operations. Delete, flush, rename are
  only allowed to owners.
  
- Columns can now also be added from the table screen.

- Send email now checks for correctness of email addresses (basic check)
  
### Changed

- Fixed a bug in a redirect when finishing the attributes screen with a Save
  and close.

- Workflow model now stores all the information about columns in a single 
  JSON object rather than three of them individually. This is to include in 
  the future things like "category names" for the values in the column (and 
  simplify data entry for rows). This is a transparent change in the 
  underlying model.
  
- Major revamp of the column representation. It now has its own data model 
  (instead of being folded as JSON fields in the Workflow model). Major 
  rewrite of the column-handling functions/views to account for this change.
  
- Fixed several bugs in the merge procedure (column reordering, column 
  renaming in the data_frame, and combining renaming and selection of key 
  columns).
  
- Fixed the import/export in the presence of the new column model + tested 
  cases of full/partial export with full/partial import. Serializers are now 
  properly invoked in a recursive way.
  
- Code reorg to curb down on large files.

- Wrote the templates and views for the pages for 404, 403, 400 and 500.
   
## 1.0.1 2017-10-18

### Added

- The possibility to turn the URL for serving an action on/off
- The possibility to share workflows. The functionality relies on the sessions
   being stored in the database. It assigns a session key to each workflow that
   is remove once the user goes back to the main page or the session expires.
   Any access to a workflow is checked against the owner, the users that can
   access it (ManyToMany relation in workflow) and if the workflow has the 
   sesison_key of an active session.
    
- Filter name does not need to be restricted to have a "variable" name style.

## 1.0.0 2017-10-17

### Added

- This CHANGELOG file will include the developments included in OnTask
- Deployed the production instance with the basic functionality:
    - Workflow, action, condition and filter creation
    - HTML preview based on condition
    - Bulk email with notification email, tracking, and message preview
    - Import/export of workflows with/without data.
    - Update/Merge of CSV with automatic detection of data types and unique
      keys. Merge procedure allows user to select key, rename columns and
      choose the modality of merging.
    - API offering functionality to list, create, update and delete workflows,
      as well as updating and merging data frames.
    - Workflow operations to manage attributes, column names, key columns
    - Search and Data entry for individual rows
    - Column deletion
    - Fully operational admin subsite with permission control of all the
      objects, user and group manipulation, handling Token authentiation for 
      the API, and user profile.
