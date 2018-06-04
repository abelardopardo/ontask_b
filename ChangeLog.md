## 2.7.0 (2018-06-04)

### Added

- Functionality to export andi mport actions alone. This is very useful to 
  simply transfer a single set of conditions or columns from one workflow to 
  another.
  
- Definition and usage of SQL connections. The definition is only available 
for the superuser and instructors are allowed to use them in the upload/merge
 page.
 
- Use of plugins. Arbitrary transformations of a subset of the dataframe are 
now allowed by installing python modules in a specific folder. 

### Changed

- Revamped the structure of the page to edit the action ins.

- Extended and polished documetation

### Fixed

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
