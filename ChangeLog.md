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
