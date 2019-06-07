.. _using:

Using OnTask
############

.. contents:: Contents
   :local:
   :backlinks: none
   :depth: 3

The idea behind OnTask is to help instructors, learners and designers to exchange data  about what is happening in a learning experience to design and deploy personalized learner support actions. This last term, *personalized support actions* refers to any action that is offered to learners in different forms depending on personalized conditions. The typical *workflow* to use OnTask starts by uploading and combining available data about the learning experience, either extracted from some platform (LMS, video annotation, quizzes), provided by the learners (questionnaires), or captured by the instructors. The instructors then write simple rules to select a subset of students and create a resource (HTML page, a message, a visualization) so that its content depends on the data available for each learner. The following figure illustrates of this workflow:

.. figure:: ontask_workflow.png
   :align: center
   :width: 100%

Imagine a learning experience in which you want to provide three personalized messages to the learners. In the first week, you want to send a welcome email and personalize slightly the text of this message based on the student background (courses taken before this one). The second week you want to send some comments and suggestions about the participation in the forum and the text will depend on the measures of engagement obtained from the platform. The third personalized email will vary depending on the level of engagement with the videos in the course. The idea of these messages is that you want to change the text in the message for each learner based on the information stored in the table.

OnTasks allows instructors to manage a set of **workflows**. A :ref:`workflow <workflow>` contains a **table** with data about the learners and a set of **actions**. After creating and opening a workflow you need to populate the table with data extracted from the learning environment. We assume that there several data sources (coming from the use of technology, self-reported by the students, or observed and reported by the instructors). These data sources are combined and stored in the **table**. Think of the table as a conventional excel sheet storing the information about the learners (one learner per row and a set of features about each learner as columns).

The other relevant entity in OnTask is the **action** that is either a set of questions to collect information from the learner or a text with elements that are selected or ignored based on **conditions** that are evaluated with respect to the learner student features stored in the table. This text can be included in an email, made available through a web page, or forwarded to another system for further processing.

The rest of the material in this section will use an :download:`initial workflow <../../initial_workflow.gz>` that can be downloaded and imported to your collection of workflows in OnTask.

.. _workflow:

Workflow
********

    "But anyone who has experienced flow knows that the deep enjoyment it provides requires an equal degree of disciplined concentration."
    -― Mihaly Csikszentmihalyi

After logging into OnTask, the platform shows the buttons to create or import a workflow as well as those already available to the user as shown in the following figure.

.. figure:: /scaptures/workflow_index.png
   :align: center
   :width: 100%

.. sidebar:: Going back

   The **Workflows** link at the left corner of the top menu *closes* the workflow being manipulated and shows you the list of available workflows. The workflow is also *unlocked* so that it can be accessed by those users :ref:`sharing <details_sharing>` its access.

The navigation through the platform is done using the links in the top menu bar. The *Workflows* icon in the left side of the menu brings the user back to the page showing the available workflows. The book icon in the upper right side of the menu bar opens the documentation page, and the user icon provides access to the user profile (name, last name, bio, password and authentication tokens).

The home page offers the following operations:

.. _workflow_create:

*New workflow*
  Opens a dialog to set the name and description of a new workflow and then show the page to upload data in the table.

  .. figure:: /scaptures/workflow_create.png
     :align: center
     :width: 60%

.. _workflow_import:

*Import workflow*
  Opens a dialog requesting a workflow name and a file containing a previously exported OnTask workflow as shown in the following figure:

  .. figure:: /scaptures/workflow_import.png
     :align: center
     :width: 100%

This page also shows those workflows previously created by the user. Each workflow is shown as depicted in the following figure.

.. figure:: /scaptures/workflow_card.png
   :align: center
   :width: 60%

The icons in the bottom of this element allow you to perform the following operations:

*Open the workflow*
  Selects the workflow for further manipulation. Once selected, workflow name is shown under the top navigation bar as illustrated in the following figure.

  .. figure:: /scaptures/navigation_bar.png
     :align: center
     :width: 100%

|fa-pencil| *Change name or description*
  Changes the name of the description given to the workflow.

|fa-clone| *Create a duplicate*
  Creates a duplicate or exact copy of the workflow with the prefix *Copy_of_* added to the  workflow name.

|fa-minus-square| *Delete all data*
  Deletes all data and actions stored in the workflow (turns it into an empty workflow with just the name and the description).

|fa-trash| *Delete the workflow*
  Delete the workflow from the system.

When a workflow is open, the top-bar menu appears with the structure shown in the following figure.

.. figure:: /scaptures/tutorial_top_menu_bar.png
   :align: center

.. include:: ../Tutorial/Tasks/include_top_menu.rst

Once you open a workflow, the platform *locks it* so that no other user can manipulate it (see :ref:`sharing a workflow <details_sharing>`). The lock is released navigating back to the home page, logging out, or the session expires after lack of activity. If you access a workflow and another user is currently using it, the platform will tell you that is locked and show who is holding the lock.

.. _dataops:

Data
****

    "May be stories are are just data without a soul"
    -- Brené Brown


This section describes the operations to either upload the first set of data into the table, or merge additional data with the one already stored. This step may be done automatically before you work with a workflow. If this is the case, you may skip this section or revisit it when you need to manipulate the existing data.

The data operations are divided into the following categories:

Upload
  Load the first data set in an empty table.

Merge
  Combine the existing data with new data

Run a Transformation
  Execute an operation in the existing data and store the result as additional columns.

Run a model
  Use the existing data to **predict** additional values.

These operations are available after selecting a workflow for manipulation under the top menu option **Table**.

If the workflow table is empty, OnTask will request the parameters required to :ref:`upload data <upload_data>` from a given data source. On the other hand, if the workflow table already contains data, OnTask will request the parameters to perform a *merge operation* in which the existing data is combined with the data extracted from the given source.

.. _upload_data:

Upload Data
===========

These operations are provided to upload the initial set of data into the workflow table using a variety of sources.

.. figure:: /scaptures/dataops_datauploadmerge2.png
   :align: center

Upload CSV Files
----------------

CSV or "comma separated value" files are plain text files in which the first line contains a comma-separated list of column names, and every subsequent line contains the values of these columns for each row. It is a popular format to exchange data that can be represented as a table (Microsoft Excel allows to save one sheet in a spreadsheet file into this format). The following figure shows the first step to perform this operation.

.. figure:: /scaptures/dataops_csvupload.png
   :align: center

In some cases, the file with comma-separated values contains several lines at either the top or the bottom of that need to be skipped when processing the data. The page to upload the CSV file allows you to specify the number of lines to skip at the start and end of the file.

Upload Excel Files
------------------

OnTask is also capable of uploading the data from one sheet of a Excel file. The following figure shows the first step to perform this operation.

.. figure:: /scaptures/dataops_upload_excel.png
   :align: center

In this case the file is assumed to have multiple *Sheets* and one of them
has to be selected to upload the data.

.. _google_spreadsheet_file:

Upload Google Spreadsheet Files
-------------------------------

OnTask allows you to upload a data table stored in a Google Spreadsheet that is publicly accessible.

.. figure:: /scaptures/dataops_upload_gsheet.png
   :align: center

.. _s3_bucket_file:

Upload a CSV file stored in Amazon S3 Bucket
--------------------------------------------

Amazon Simple Storage Service (S3) offers the possibility of storing files in *buckets*. The service offers an API to access these files. This page in OnTask requests the credentials required to access the CSV file stored in a bucket and process its content.

.. figure:: /scaptures/dataops_upload_s3.png
   :align: center

.. _sql_connection_run:

SQL connection
--------------

This operation uploads the data into the current workflow table using a SQL connection to a remote database. These connections have to be :ref:`previously defined and configured by the system administrator <sql_connections>`. Instructors can use them to access the content of a previously defined table in a remote database. Once selected, the platform shows the SQL connections available and the possibility to view the connection parameters (click on the connection name), or *Run* the connection to upload the data as shown in the following figure.

.. figure:: /scaptures/dataops_SQL_available.png
   :align: center

When *running* a SQL connection the platform shows the configuration parameters and requests the password to access the remote database (if required).

.. figure:: /scaptures/dataops_SQL_run.png
   :align: center

Confirmation step to upload data
--------------------------------

When uploading data for the first time, the values are prepared to be assigned as the initial content of the workflow table. But before this assignment is done, the platform needs you to verify some information. Upon reading the new data, OnTask will automatically detect the data type in each column and those columns that have unique values (no repetitions) and mark them as **keys**. Key columns are very important because their values (as they are different for every row) are required for several operations. The workflow table **must have at least one key column**. If here are several columns with this property, OnTask :ref:`allows you to *unmark* some of them as non-key <details>` as long as there is always one of them wih such mark. Additionally, you may :ref:`mark any column as a key column <details>` if the values are all different. The operations to manipulate column information is described in the section :ref:`details`.

Before finishing the upload step and storing the data in the table, OnTask also allows you to change the name of the columns or change the **Key** attribute as shown in the following figure.

.. figure:: /scaptures/dataops_upload_merge_step2.png
   :align: center

After this step the data is stored and the platform shows the :ref:`table` page.

.. _data_merge:

Data Merge
==========

.. sidebar:: Merge a.k.a "Join"

   Merging is a common operation in databases and is commonly known as *join*. There are several variants of join operations depending how the differences between the key columns are handled. These same variants exist in OnTask when combining the data already existing in the table. The operation relies on the **key column** to merge the two sources.

A merge operation is executed when data is uploading and the workflow **already has data in its table**. Although this operation is common in data science contexts, it has several variants that make it challenging to use properly. These variants derive mostly from the method used to specify how the values in the new columns are *matched* with respect to the ones already existing in the table. In other words, each new column has a set of values, but they need to be in the right order so that the information is matched appropriately for every row. For example, if the table contains a column with the age of the learners, and a new column with the gender is merged, the rows of the new column need to correspond with the learners in the existing table. The way to address this issue is to use a **key column* in the existing table and another ** key column** in the new data. These columns uniquely distinguish each row with a value so they are used to make sure that the information for the rows with matching values in these columns are merged. These operations are executed in a set of additional steps. The first step of the merge operation is identical to the upload operation. After detecting the column data types, the key columns and offering the option of changing their names, the next steps identify the key columns to use in the merge, the variant to merge, and shows a summary of the changes that will result from the operation.

Step four: select keys and merge option
----------------------------------------

The following figure shows the third step of the merge operation.

.. figure:: /scaptures/dataops_upload_merge_step3.png
   :align: center
   :width: 100%

The form requires the following fields:

Key columns
  A key column in the external table about to be merged and a key column in the existing table (both fields are required).

Merge method
   After choosing a merge method, a figure and explanation are shown below.

There are four possible merge variants:

1) **Select only the rows with keys in both existing and new table**.
   It will select only the rows for which values in both key columns are present. Or in other words, any row for which there is no value in either of the key columns **will be dropped**.

   .. figure:: ../../src/media/merge_inner.png
      :align: center
      :width: 50%

#) **Select all rows in either the existing or new table**.

   All rows in both tables will be considered. You have to be careful with this option because it may produce columns that are no longer unique as a result.

   .. figure:: ../../src/media/merge_outer.png
      :align: center
      :width: 50%

#) **Select the rows with keys in the existing table**.

   Only the rows in the new table with a value in the key column that is present in the existing table will be considered, the rest will be dropped.

   .. figure:: ../../src/media/merge_left.png
      :align: center
      :width: 50%

#) **Select the rows with keys in the new table**.

   Only the rows in the existing table with a value in the key column that is present in the key column from the new table will be considered, the rest will be dropped.

   .. figure:: ../../src/media/merge_right.png
      :align: center
      :width: 50%

In any of these variants, for those columns that are present in both the existing table and the new table, the values of the second will update the existing ones in the first. This update may introduce non-values in some of the rows (for example in columns for with the new data does not provide any value). Additionally, extra care needs to be taken when performing this operation as some of the merge variants may eliminate data in the existing table. In the extreme case, if you try to merge a table with a key column with no values in common with the existing key and you select the method that considers rows with keys in both the existing and new table, the result is an empty table.

Step five: verify upcoming changes
----------------------------------

After selecting these parameters the last step is to review the effect of the operation and proceed with the merge as shown in the following figure.

.. figure:: /scaptures/dataops_upload_merge_step4.png
   :align: center

.. _table:

Table
*****

   "You're here because you know something. What you know you can't explain,
   but you feel it"
   -- Morpheus, The Matrix

The information stored in the workflow table is accessed through the |fa-table| *Table* link in the top bar menu selecting the option **Full view**. As this table can be arbitrarily large, the application groups the rows into pages and provides links to each of the pages at the bottom of the table. The top of the table includes a pull down menu to choose how many rows are shown per page. If the table has a large number of columns, a horizontal scroll is available to show the additional content. The order of the columns in the table can be changed by dragging them from the top row and dropping them in a new position.

The following figure shows an example of the main table page.

.. figure:: /scaptures/table.png
   :align: center
   :width: 100%

The table also offers the possibility of searching for a value. The given string is used to search all the columns in the table.

.. figure:: /scaptures/table_buttons.png
   :align: center
   :width: 100%

.. include:: /Tutorial/Tasks/include_table_top_buttons.rst

The left-most column in the  table shows the operations to manipulate a row:

|fa-pencil| Edit content
  This link opens a form with one field per column to modify the values in the row. The key columns are shown but not allowed to be changed.

|fa-bar-chart| Dashboard
  A dashboard showing the population measures for all the columns and a mark showing where are the values for this row.

|fa-trash| Delete
  Delete the row from the table.

.. _table_views:

Table Views
===========

Due to the potentially large size of the workflow table in either number of rows or columns, OnTask offers the possibility to define *Views*. A view is a subset of columns and rows of the original table. You may define as many views as needed. The link *Views* in the main table page shows the views available and the operations to manage them.

.. figure:: /scaptures/table_views.png
   :align: center
   :width: 100%

The buttons at the top of the page offer the following operations:

Full Table
  Go back to the page showing the entire data table.

|fa-plus| View
  Create a new view

When creating a view you need to provide a name (required), a description, a subset of columns to show (at least one of them must be a **key column**), and an expression to select a subset of rows. This expression is evaluated with the values of every row and if the result is *True*, the row is included in the view. The following figure shows an example of the information that is included in the definition of a view.

.. figure:: /scaptures/table_view_edit.png
   :align: center
   :width: 60%

Once a view is created, the following operations are available:

Edit
  Click in the view name to edit its elements (name, description, set of columns to show and row filter)

|fa-eye| Show
  Show the subset of the table selected by the view

|fa-clone| Clone
  Create a duplicate of this view with the prefix *Copy_of* added to its name. This operation is useful to create a new view with content that is similar to an already existing one (clone and edit).

|fa-trash| Delete
  Delete the view.

The page to show the subset of the table defined by the view is identical to the full table view, but the table is restricted to the appropriate columns and rows. The view shown in the previous figure defines a subset of 12 columns of the table that is rendered as shown in the following figure.

.. figure:: /scaptures/table_view_view.png
   :align: center
   :width: 100%

The |fa-dashboard| *Dashboard* and |fa-download| *CSV Download* buttons, when used while in a view, will apply to the selected data subset.

.. _action:

Actions
*******

    "In order to carry a positive action we must develop here a positive
    vision"
    -- Dalai Lama

This is the most important functionality of the platform. Actions are used exchange information with the learners or other platforms, either through personalized information, or requesting data through a survey. A workflow contains a set of actions shown when selecting |fa-comments| *Actions* page in the top-bar menu. The next figure shows an example of the actions available in one workflow.

.. figure:: /scaptures/actions.png
   :align: center
   :width: 100%

The buttons at the top of the page offer the following operations:

|fa-plus| Action
  Create a new action in the workflow. The form requires a name (unique for the current workflow), a description (optional), and the type of action. OnTask offers the following types of actions: personalized text, personalized Canvas email, personalized JSON, and surveys.

|fa-upload| Import action
  Upload an action previously downloaded from another workflow.

The actions in the workflow are shown in a tabular format. For each action the following main operations are offered:

Edit
  Click in the name action to edit its content.

|fa-rocket| Run
  Use the action to either provide personalized content or run a survey (see :ref:`running_actions` for more information)

|fa-link| URL
  Provide access to learners to the content of the action through a link (only available for actions of type Personalized Text)

|fa-file-archive-o| ZIP
  Download a ZIP file with as many files as selected learners in the action. Each file contains the personalized document for the learner (only available for Personalized Text actions)

|fa-calendar| Schedule
  Schedule the execution of the action for some time in the future

|fa-pencil| Rename
  Edit the name and description of the action.

|fa-clone| Clone
  Create an exact duplicate of the action adding the prefix "Copy_of" to its name.

|fa-download| Export
  Download a file containing the definition of the action suitable to be uploaded into another workflow.

|fa-trash| Delete
  Remove the action from the workflow.

.. _personalized_content:

Personalized Text
=================

These actions allow to create a document (similar to a HTML page) and mark elements (paragraphs, sentences, images) with *conditions* that will control if they are included or ignored when showing the document. The conditions are stated in terms of the columns of the data table. Think of this personalized content as a resource (message, tip, comment) you would offer learners but with content that is different depending on the data stored in the table. You may have several of these actions prepared to be used at different points during a learning experience. The personalized text action is manipulated with the screen shown in the following figure:

.. figure:: /scaptures/action_edit_action_out.png
   :align: center
   :width: 100%

The screen has three tabs: the left one contains the editor, the center one the definition of a filter (optional) to select a subset of the learners to consider for this action, and the right tab contains the conditions used in the text (if any).

.. _personalized_text_editor:

The Personalized Text HTML Editor (left tab)
  This is a conventional HTML editor offering the usual operations (inserting text, headings, lists, links, images, etc.) Right above the editor window you have three pull down menus to: insert a column value in the text (a placeholder), use a condition to conditionally show the text currently highlighted, or insert a :ref:`workflow attribute <details_attributes>` that will be replaced by the corresponding value.

  .. figure:: /scaptures/action_edit_action_out.png
     :align: center
     :width: 100%

.. _personalized_text_filter:

The filter
  The center tab shows a *filter*. This element is an expression used to decide which learners (or more precisely, the corresponding rows in the data table that) will be selected and used in this action.

  .. figure:: /scaptures/action_action_out_filterpart.png
     :align: center
     :width: 100%

  The filter element shows the name, description, and the formula defined. The icons at the bottom of the object provide access to the following operations:

  |fa-pencil| Edit
    Edit the name, description, and formula of the filter.

  |fa-trash| Delete
    Remove the filter from the action.

  When editing or creating a filter, the form shows the information as in the following figure:

  .. figure:: /scaptures/action_action_out_edit_filter.png
     :align: center
     :width: 60%

  The expression in this condition is shown under the title **The learner will be selected if** and can be read as:

    Video_1_W4 = 0 or Video_2_W4 = 0

  The first element of the expression is the sub-expression ``Video_1_W4 = 0`` which contains the variable ``Video_1_W4``, the equal sign, and the constant zero. The second element is a sub-expression with the variable ``Video_2_W4``, the equal sign, and the constant 0. These two sub-expressions are connected through the **OR** operator, which means that the expression will be **True** if either of the sub-expressions are **True**, and **False** in any other case. When evaluating this expression, the variables are replaced by concrete values (numbers). For example, if ``Video_1_W4`` is replaced by 3, and ``Video_2_W4`` is replaced by 4, the evaluation will transform the expression into :math:`3 = 0 or 4 = 0`. The sub-expression :math:`3 = 0` is clearly **False** and so is the other sub-expression :math:`4 = 0`. This means the initial expression is **False**. result is either **True** or **False**. Another possible evaluation is if ``Video_1_W4`` is equal to zero (and ``Video_2_W4`` remains equal to 4). In this case the resulting expression is :math:`0 = 0 or 4 = 0`. In this case, the first sub-expression is **True**, and although the second is **False**, only one is needed for the overall expression to be **True**.

  These conditions can have nested sub-expressions and get complex fairly quickly. However, the underlying mechanism to evaluate them remains the same: replace variables with values and decide the result (**True** or **False**).

.. _personalized_text_conditions:

Text conditions
  The right tab contains the *text conditions*. A condition is an expression that when evaluated with respect to the values in the table for each learner will either be **True** or **False**. These expressions are commonly used in other applications such as spreadsheets. The following screen shows an example of the content of this tab with two conditions.

  .. figure:: /scaptures/action_action_out_conditionpart.png
     :align: center
     :width: 100%

  The button |fa-plus| *Condition* at the top of the tab opens the form to define a new condition. Once created
  The buttons in the screen allow you to edit the expression, insert the condition to control the appearance of text in the editor (below), clone the condition, or delete it from the action. The button |fa-clone| *Clone other conditions* creates a duplicate of a condition used in any other action. The button |fa-bar-chart| *Column statistics* allows to select a column and show a statistical summary of its values.

  Each condition shows the number of learners for which the expression in that condition evaluates to **True** (if this value is zero, it means that any text you include in the editor controlled by this condition will not appear for any of the learners), the name, description, and the defined formula.

  The icons in the bottom of the condition element allow the following operations:

  |fa-pencil| Edit
    Open a form to edit the name, description and expression in a condition.

  |fa-clone| Clone
    Create an exact duplicate of this condition with the prefix "Copy_of" added to its name. This operation is useful when creating a new condition with an expression very similar to an existing one.

  |fa-trash| Delete
    Delete the condition from this action.

  The following image shows an example of this condition.

  .. figure:: /scaptures/action_action_out_edit_condition.png
     :align: center
     :width: 60%

  The expression in the previous condition is shown under the title **The text will be shown if** and can be read as:

    Correct_1_W4 equal to zero

  The first element is the column name ``Correct_1_W4``, followed by the equal sign, and then the constant zero. When evaluating this expression, the column name is replaced by the value from the corresponding to each learner. For example, if a given learner has ``Correct_1_W4`` equal to 3 the evaluation will transform the expression into :math:`3 = 0` which is **False**. Another possible evaluation is if another learner has ``Correct_1_W4`` equal to zero. After substitution of the column by the values for the learner, the resulting expression is :math:`0 = 0`. In this case, the expression is **True**. Once defined this condition can be applied to a part of the personalized text. When creating the texts, the condition is evaluated with the values for each student. If the expression is true, the text is included, if not, it is ignored. This mechanism is at the heart of how OnTask personalizes the content of the actions. In the example above, the expression in the condition one of the learners in the data table.

The buttons at the top of the page offer the following operations:

|fa-eye| Preview
  The Preview button shows how the text in the editor is shown for those
  learners selected by the filter (if any). After clicking in the button you
  will see a window with the resulting text. If there are any elements in the
  text that are controlled by any condition, the bottom area will show their
  values.

  .. figure:: /scaptures/action_action_out_preview.png
     :align: center
     :width: 60%

  Use the arrow buttons to see all the different versions of the text
  depending on the values stored in the table for each learner.

|fa-floppy-o| Save
  This button saves the content of the text editor and continues in the same editor page.

|fa-check| Close
  This button saves the content of the text editor and returns to the page
  showing all the actions in the workflow.

.. _using_values_attributes_conditions:

Using column values, attributes and conditions in a Personalized Text
---------------------------------------------------------------------

As previously described the :ref:`Personalized Text Editor <personalized_text_editor>` may include three per-learner personalized elements: an attribute name, a column name or a portion of text marked with a condition.

Attributes
  Attributes are simply synonyms that you may want to use in more than one action. For example, if you have several actions that include the name of a course, instead of including that name if all actions, you may define an *attribute* with name *course name* and value *Biology 101* and include in the actions the attribute name. OnTask will replace that attribute with its value when showing the text to the learners. If you then change the name of the course (or you export this workflow and import it to be used in another course), you only need to change the attribute and the name of the course will appear correctly in all actions (in what is called a *single point of change*).

  To insert an attribute name in the text simply place the cursor in the editor where you want the value of that attribute to appear and select the attribute from the area above the editor. The name of the attribute will be inserted in the text surrounded by double curly braces, (for example ``{{ course_name }}``. Only :ref:`the attributes <details_attributes>` you previously created in the details page are available.

Column names
  The other element that can be personalized is a column name. For example, suppose you have a column in your table with the first name of the learners. You can use the column name to personalize the greeting in the text. To insert a column name, you follow the same steps used for the attribute but this time you select the column name from the pull-down menu. You will see that the name of the column appears in the text also surrounded by double curly braces (for example ``Hi {{ GivenName }}``. The double curly
  braces is the way OnTask has to mark that text to be personalized or replaced by the corresponding value for each learner extracted from the data table.

Conditional text
  Using a condition to control if a portion of the text is shown or ignored is slightly different. You need to first highlight the text you want to appear depending on the condition in the editor. Then click in the pull down menu **Use condition in highlighted text** and select the condition to use. The text will be surrounded by two marks. For example if the condition name is ``No Video 1``, the text you highlighted will appear in the editor after clicking in the *Insert in text* as::

    {% if No Video 1 %}You need to review his week's video{% endif %}

  This format marks the message *You need to review this week's video* to appear only for those learners for which the condition ``No Video 1`` evaluates to **True** with their current values in the data table. Otherwise, the text will be ignored. The following figure illustrates this process.

  .. figure:: /scaptures/Ontask____howtocreatetext.gif
     :align: center
     :width: 100%

.. _surveys:

Surveys
=======

The personalized text actions described in the previous section make information available to the learners. The *survey* actions perform the operation in the opposite direction, they collect information from the learners and store it in the table. In a learning context a survey can be used by the learners to submit certain data, or by the instructor to collect annotations about learners throughout the experience. OnTask supports these two modalities. Survey actions are edited with a page with four tabs as shown in the following figure.

.. figure:: /scaptures/action_edit_action_in.png
   :align: center
   :width: 100%

The information collected for each question will be represented in the table by a column. The editor page allows you to use any of the existing questions to be included in a survey. The three tabs in the screen offer the following functionality.

Survey parameters
  This tab shows the additional parameters to deploy the survey. More precisely the screen allows to define the text that is shown at the top of the survey (*Survey description*), the key column used to identify the users, and if the questions should be shown in different order for each user.

  .. figure:: /scaptures/action_edit_action_in_parameters.png
     :align: center
     :width: 100%

Survey Questions
  This tab shows the questions that are contained in the survey. The two buttons at the top of the screen allow you to either insert an existing question (the pull-down menu will show all the column names available in the table) or create a new question. When creating a new question, the following form is used:

  .. figure:: /scaptures/action_edit_action_in_create_question.png
     :align: center
     :width: 60%

  The field *Question name* will be used internally as the column name in the table. The *Description* field is the text shown to the learners next to the question. If the question includes a set of values allowed, the form available to the students will collect the answers using a pull-down menu with the given choices.

  Once a question has been defined, its inclusion in the survey can be controlled using a condition defined in the *Conditions* tab. The pull down menu to the right of the question description allows to select the condition.

  .. figure:: /scaptures/action_edit_action_in_question_tab.png
     :align: center


  As with other tables in OnTask, if the number of elements (in this case questions) is too large, they will be divided into pages with a link to access each page, and the content of the questions is searchable.

Filter Learners
  This tab is identical to :ref:`the filter in the personalized text action <personalized_text_filter>`. The tab allows to include an expression to decide if a learner is included or not in the survey. This survey has no filter defined.

Conditions
  This tab allows the definition of conditions identical to :ref:`the text condition tab <personalized_text_conditions>` in the personalized text actions. The conditions can then be attached to the questions to decide if they are present or not in the survey.

The *Preview* button at the bottom of the page shows the content as it will be shown to the learners.

.. figure:: /scaptures/action_action_in_preview.png
 :align: center
 :width: 60%

.. _personalized_json:

Personalized JSON Object
========================

This type of action allows the creation of a `JSON object <https://www.json.org/>`__ with content that is personalized with the same functionality as described in the section about :ref:`Personalized Content <personalized_content>`. The difference is that instead of creating a text, the action creates a JSON object that will eventually be sent to another platform for further processing. This object is also a resource that is different for every student but the difference is that instead of being prepared to be visualized, it is packaged with a structure suitable to be received by another platform through a URL.

The screen to create a Personalized JSON object is shown in the following figure.

.. figure:: /scaptures/action_personalized_json_edit.png
   :align: center
   :width: 100%

The tabs have the same functionality than in the case of :ref:`personalized text <personalized_content>`.

Text
  This tab contains a plain text editor to describe the structure of the object and :ref:`insert column values, attribute values or use conditions to control the presence of elements in the object <using_values_attributes_conditions>`.

Filter Learners
  This tab allows the definition of an expression to select a subset of rows in the table for processing.

Text Conditions
  This tab contains the conditions that can be used within the body of the JSON object to select content (in exactly the same way as in the :ref:`personalized text <personalized_content>`).

The text shown in the previous figure defines a JSON object with three fields ``sid``, ``midterm_total`` and ``msg``. The first two contain column names that will be replaced by their corresponding values. The field ``msg`` will include one of the two messages depending on the value of the conditions.

The field *Target URL* is to introduce the URL where the object will be sent.

The preview button in the personalized JSON action shows the resulting object after verifying that the structure after evaluating the corresponding expressions is a valid JSON object.

.. _personalized_canvas_email:

Personalized Canvas Email
=========================

This type of action is only available if OnTask is :ref:`appropriately configured <canvas_email_config>` to communicate with a `Canvas Learning Management System <https://www.canvaslms.com.au/>`_. The creation of this type of action is almost identical to the :ref:`Personalized Text <personalized_content>`. The action is created selecting the corresponding action type as shown in the following figure.

.. figure:: /scaptures/action_personalized_canvas_email_create.png
   :align: center
   :width: 60%

The page to edit this action is almost identical to the one to edit a :ref:`Personalized Text actin <personalized_content>`.

.. figure:: /scaptures/action_personalized_canvas_email_edit.png
   :align: center
   :width: 100%

It contains three tabs: *Personalized Canvas Email*, *Text Conditions* and *Filter Learners*. The last two, :ref:`Conditions <personalized_text_conditions>` and :ref:`Filter Learners <personalized_text_filter>` offer the same functionality. The *Personalized Canvas Email* allows the creation of a plain text message (no HTML markup is allowed).

.. _running_actions:

Running actions
===============

Once an action has been created, it can be *run*. The meaning of this term is different for the various types of actions supported in OnTask.

.. _personalized_emails:

Sending personalized emails (Personalized Text Actions)
-------------------------------------------------------

Once you created a personalized text action and verified its content using the *Preview* button, save its content. The right-most column has a button with name *Run*.

.. figure:: /scaptures/action_action_ops.png
   :align: center

If selected, the next page is a form requesting information about how to send the messages to the learners. The next figure shows an example of this page.

.. figure:: /scaptures/action_email_request_data.png
   :align: center

The fields in this form are:

Email subject
  A line to be included as subject of all the emails.

Column to use for target email address
  OnTask needs to know where to send the email. It assumes that you have a column containing that information for each learner and it needs you to select that column.

Comma separated list of CC emails
  A comma-separated list of emails to include in the *carbon copy* or *CC* email field.

Comma separated list of BCC emails
  A comma-separated list of emails to include in the *blind carbon copy* or *BCC* email field.

Check/exclude emails
  If selected, this option inserts an extra step in which you can eliminate certain emails form the action. This feature is useful to remove certain emails that cannot be removed with the filter.

Send you a summary message
  If you select this option OnTask will send you an email with the summary of this operation (number of rows in the table that were selected by the filter, number of emails sent, date/time of the operation, etc.

Track email reading
  Include in the messages a HTML snipped to detect if the email is read. OnTask adds an extra column to the table to store the number of times the message is opened. This detection relies on how the email client opens the message and processes the included images, therefore, the information in this column may not accurately reflect this information.

Snapshot of the workflow
  If you select this option, after the emails are sent, the platform returns you a file that contains a snapshot (picture) of the workflow. It basically freezes the content of the workflow and places it in a file given to you. You may take this file and :ref:`import back the workflow <workflow_import>`. In this new workflow you can check the values and messages at the time the operation was executed.

If the option to *Check/exclude emails* has been selected, clicking in the *Next* button leads to a page where the list of emails is shown and the user can select some of them to remove from the operation. If this option is not selected, the operation to send the emails is sent to a queue for processing. The browser will show the record that contains the information about the status of this request.

Making personalized content available to learners
-------------------------------------------------

Sending a personalized text is just one possible way to make this content available to learner. Another one is to offer the content through a URL that can be given to the learners. To enable such URL click in the icon with three dots in the right most corner of a personalized text action.

.. figure:: /scaptures/action_action_ops.png
   :align: center

You will see an operation labeled ``URL`` followed by either the word ``(Off)`` or ``(On)``. Select that operation. The following window shows the URL in which the content is available as well as the field to enable/disable it.

.. figure:: /scaptures/action_URL_on.png
   :align: center
   :width: 60%

In order for the learners to be able to view their personalized content, they have to be users of the OnTask platform and their ID present in the data table. This functionality is conceived for a context in which OnTask authenticates users either through a corporate Single-sign on layer, or learners access the OnTask through the Learning Management System with a LTI interface (see :ref:`authentication`).

Running a survey
----------------

After creating a :ref:`survey action <surveys>` it can be used in two modalities: run by the instructor, or given to the learners to fill out the data. The first modality is used as a mechanism to capture instructor observations. For example, surveys run by the instructor can be used as an attendance capturing mechanism (if the instructor has a device or procedure to capture who is in attendance). If the *Run* operation is selected, OnTask shows a table with the learners selected for the action, and the values for the survey collected so far.

.. figure:: /scaptures/action_run_action_in.png
   :align: center
   :width: 100%

Each row contains the identifier of the student (in the previous table, the email) as a link. Instructors may click in a link available to enter the survey information or modify the already existing information for that learner.

.. figure:: /scaptures/action_enter_data_action_in.png
   :align: center
   :width: 100%

After entering the information the list of students for which the data entry is still allowed.

Making the survey available to the learners
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The second operation available for *survey* actions is to make available the URL to learners so that they individually enter the information themselves. The right-most column of the action table contains an icon with three dots that if selected shows a set of additional operations, and one of them has the text *URL*. If selected OnTask shows the URL for the survey, the possibility of enable/disable it, or even provide a date/time window for its availability.

.. figure:: /scaptures/action_action_in_URL.png
   :align: center
   :width: 60%

Once enabled, you may send the URL to the students (you may even use a personalized text action for that). Once the students click in the action, and if they are allowed to connect to OnTask as basic users, after authentication, if their email is part of the table, they will see a form with the survey questions and after answering it, the values are automatically stored in the right row and column in the table.

These two survey actions are ideal to collect information about any aspect of a learning experience in a way that is centralized and available for further processing through personalized text actions. For example, users may choose from a predefined set of topics those that were more challenging. This information can then be used in a personalized text action to provide the adequate resources to each learner.

.. _send_personalized_canvas_emails:

Sending personalized emails in Canvas
-------------------------------------

The execution of a :ref:`Personalized Canvas Email <personalized_canvas_email>` action requires additional information as shown in the following figure:

.. figure:: /scaptures/action_personalized_canvas_email_run.png
   :align: center
   :width: 100%

Column in the table containing Canvas ID values
  This column is essential to send the emails to the platform as it is used to uniquely identify every Canvas user. The data can be obtained downloading the marks of a course as a CSV file and uploading/merging this column with the existing table.

Email subject
  The text to use as subject for the messages.

Canvas Host
  If there is more than one Canvas platform configured in OnTask, an additional pull-down menu will appear to select which one to use. If there is a single Canvas platform configured, it will be used by default and this field will not be shown in the form.

Check/Exclude Canvas IDs before sending messages
  If this option is selected OnTask adds an extra step to check the identifiers that will be used and offer the possibility of excluding some of them.

Download a snapshot of the workflow
  If selected, a snapshot of the workflow (data and actions) will be downloaded after the messages have been queued for delivery.

After introducing this data, OnTask will check if it has credentials for the user to access Canvas through its API. If not, the user will be redirected to a page in the Canvas Learning Management System to 1) authenticate, and 2) authorize OnTask to access the platform. If these steps are successful, the user is redirected back to OnTask and the messages are delivered. The credentials retrieved from Canvas will be reused for future executions of this action.

Sending personalized JSON objects to another platform
-----------------------------------------------------

The operation to *Run* a personalized JSON action sends the objects resulting from the personalization to the given URL. The page to collect the information to run these actions is shown in the next figure:

.. figure:: /scaptures/action_json_run_request_data.png
   :align: center
   :width: 100%

The first field is the column to perform a last review of the elements to send and select some of them to exclude in an extra step. If the field is empty, this step is skipped. The second field is the token to use for authentication when sending the JSON objects to the URL given when editing the action. This operation assumes that such token has already been obtained and provides no additional functionality to execute that step as part of this operation.

Similarly to the email actions, once these fields are provided, the operation to send the JSON objects to the target URL is queued in a batch system for processing. The browser shows the record where the status of this request is reflected.


Creating a ZIP file with the personalized text
==============================================

The :ref:`personalized text actions <personalized_content>` offer the possibility of creating a ZIP file containing one HTML file with the personalized text for every learner. The execution of this operation requires the use of two columns in the table and a suffix to create the file names. The operation is available clicking in the icon with three dots in the right-most column of an action in the action page. The additional information is requested through the form shown in the following figure.

.. figure:: /scaptures/action_zip_request_data.png
   :align: center
   :width: 100%

The first part of the file name is taken from the values of a key column. The second part of the file name is taken from a second column (optional). Additionally, the user may include a third suffix to be used for the last part of the file name (if none is given the default suffix is ``feedback.html``. For example if the first column has the values ``submission 01, submission 02, submission 03``, the second column has the names ``John, Paul, Mary``, and the file suffix is empty, the ZIP file will be created with three HTML files with names ``submission 01_John_feedback.html``, ``submission 02_Paul_feedback.html`` and ``submission 03_Mary_feedback.html``.

.. _upload_feedback_to_moodle:

Uploading feedback files for a Moodle Assignment
------------------------------------------------

One of the potential uses of the ZIP file generated from a personalized text action is to upload each file as personalized feedback of an assignment in a Moodle course. However, there are some requirements in the file names so that they are uploaded each to the appropriate location, namely:

1. The table must have column named ``Identifier`` with values starting with the word ``Participant`` followed by a white space and a unique number. This column can be extracted from a Moodle Assignment by downloading the *grading worksheet*:

  .. figure:: /scaptures/downloadgradingworksheet.png
     :align: center

  The CSV file has two columns with names ``Identifier`` and ``Full name``.

  .. figure:: /scaptures/moodle_grading_sheet.png
     :align: center

2. The two columns ``Identifier`` and ``Full name`` must be :ref:`merged<data_merge>` with the current data in the workflow.

3. Choose the column ``Identifier`` and ``Full name`` as the first and second column respectively when generating the ZIP file. Make sure you select the option ``This ZIP will be uploaded to Moodle as feedback``.

4. Upload the resulting ZIP using the option ``Upload multiple files in a zip`` in the Moodle Assignment.

   .. figure:: /scaptures/multiplefeedbackzip.png
      :align: center


.. _workflow_settings:

Additional Workflow Operations
******************************

In addition to the operations described in the previous sections to upload and merge data, create actions, and run these actions, there are additional operations for the workflow that can be accessed through the |fa-cog| More pull-down menu in the top-bar menu. The settings pages offer information about: workflow operations (export, rename, clone, etc.), column operations (change column type, rename, clone, etc.), scheduled actions, and view logs.

.. include:: include_details.rst

.. _scheduler:

Scheduled Actions
=================

   "I have no regular schedule. I get up whenever I can."
   -- Jimmy Wales


The :ref:`personalized text <personalized_content>`, :ref:`personalized canvas email <personalized_canvas_email>` and :ref:`personalized JSON object <personalized_json>` actions can be scheduled to run at some point in the future. To schedule the execution of an action go to the |fa-comments| *Actions* page from the top menu, click in icon with three dots in the right-most column of the action and select the operation |fa-calendar| *Schedule*.

.. _schedule_email:

Scheduling a Personalized Text Action
-------------------------------------

The following figure shows the information requested to schedule the execution of a personalized text action (sending emails to learners):

.. figure:: /scaptures/schedule_action_email.png
   :align: center

The fields in this form are:

Name
  A name to identify this scheduling (a user may have several of these actions pending in a workflow)

Description
  A brief description explaining this scheduled action (for example, "send reminder before the exam")

Column containing email
  The column in the table used to fill out the destination email. OnTask will check that the values in that column are proper email addresses.

When to execute the action
  A date/time in the future when the action will be executed.

Email subject
  The text to be included in the email subjects.

Comma separated list of CC emails
  A comma separated list of emails to include in the *carbon copy* (or CC) field of the email.

Comma separated list of BCC emails
  A comma separated list of emails to include in the *blind carbon copy* (or BCC) field of the email.

Send confirmation email
  Select this option if you want a confirmation email sent to you.

Track when emails are read
  Try to detect if the email is read. OnTask adds an extra column to the table to store the number of times the message is opened. This detection relies on how the email client processes the message, therefore, the information in this column may not be accurate.

Check/exclude emails
  If selected, this option inserts an extra step showing the emails and offering the possibility to eliminate them from the action. This option is useful to perform a final check and remove emails that cannot be removed with the action filter.

.. _schedule_json:

Scheduling a Personalized JSON Action
-------------------------------------

The following figure shows the information requested to schedule the execution of a personalized JSON action (sending JSON object to another platform):

.. figure:: /scaptures/schedule_action_json.png
   :align: center

The fields in this form are:

Name
  A name to identify this scheduling (a user may have several of these actions pending in a workflow)

Description
  A brief description explaining this scheduled action (for example, "send reminder before the exam")

Column to select elements
  A column to show its values and allow to review and exclude some of the entries. This option is useful to perform a final check and remove entries that cannot be removed with the action filter.

Authentication Token
  The string to be use to authenticate with the external platform.

.. _schedule_canvas:


..
  Scheduling a Personalized Canvas Email Action
  ---------------------------------------------

  If OnTask is :ref:`appropriately configured <canvas_email_config>` to send emails using the Canvas API, the actions can be scheduled providing the information through a form as shown in the following figure.

  .. figure:: /scaptures/scheduler_action_canvas_email.png
     :align: center

  The fields in this form are:

  Name
    A name to identify this scheduling (not to be confused with the name of the action that has already been selected).

  Description
    A brief description explaining this scheduled action (for example, "send reminder the night before the exam).

  Column in the table containing the Canvas ID
    This field is mandatory because OnTask needs to know which column to use to differentiate the emails to send to Canvas.

  Email subject
    Text to include as subject of the message.

  When to execute the action
    A date/time value in the future.

.. _scheduler_menu:

Table with Scheduled Actions
----------------------------

The table showing all the action scheduling operations can be access through the |fa-cog| *More* link in the top-bar menu selecting the |fa-calendar| *Scheduled actions* link. The list of scheduled actions is shown as illustrated in the following figure.

.. figure:: /scaptures/schedule.png
   :align: center
   :width: 100%

The operations available for each operation are:

Edit
  Click in the name of the scheduled operation.

Action name
  The link in this field edits the action.

Scheduled
  Time/date when the executing will take place

Status
  Status of this execution

|fa-eye| View details
  View all the details for this scheduled execution (includes values in the payload)

|fa-trash| Delete
  Delete the scheduled execution.

.. _logs:

View logs
=========

The platform keeps a log of most of the operations that are executed when managing a workflow. These records are available through the *View Logs* link in the |fa-cog| *More* pull down menu at the top-bar menu. The page shows information about the records in tabular form. The following figure shows an example.

.. figure:: /scaptures/logs.png
   :align: center
   :width: 100%

The |fa-download| *CSV Download* button allows to download the logs in CSV format for further processing. Additionally, the content of the table is paginated and the links to access each page are shown at the botton. The records can be searched using the box at the top right corner of the table.

.. _plugin_run:

Transforming the data with your own code
****************************************

The additional method offered by OnTask to manipulate the data in a workflow table is to execute arbitrary Python code encapsulated as a Python module and placed in a predefined folder in the computer hosting the server. These Python modules are called either **Transformations** or **Models** and require some :ref:`previous configuration <plugin_install>` by the system administrator, namely, the Python module must be installed in a specific folder.

The purpose of these transformations and models is to allow arbitrary processing of the data attached to a workflow such as machine learning algorithms, predictive models, etc. The list of transformations available for execution can be accessed through the links *Run Transformation* and *Run Model* in the *Table* button of the top menu. The modules available for execution are shown in a table like the one in the next figure.

.. figure:: /scaptures/dataops_transform_list.png
   :align: center
   :width: 100%

Each transformation is shown with a name, a description and the last time the code was modified (based on the file modification time). The link in the name opens a form to introduce the information required for execution. The following figure shows and example of this page.

.. figure:: /scaptures/dataops_transformation_run.png
   :align: center
   :width: 100%

The information requested in this page is divided into the following tabs.

Input columns to transformation
  This field is to select the subset of columns from the data table that will be passed when invoking the transformation. It is possible for a transformation to define a set of *fixed* column names as inputs. If this is the case, the field in this tab shows those names and does not allow changes.

Columns to store the result
  The middle tab in this page includes fields to obtain the output column names (the transformation may supply suggestions, an optional suffix to add to the result column names to be able to differentiate between multiple executions of the transformation, and a key column to be use when merging the result of the transformation with the current table.

Parameters
  This tab contains a form to pairs *(name, value)* as defined by the transformation.

Description
  Text describing in detail the effect of the transformation.

Once the data is filled, the program is executed by clicking in the |fa-rocket| *Run* button. The execution is done in the background (it may take some tie), and a link to the log including the report is shown.

.. _plugin_requirements:

Transformation requirements
===========================

The information in this section is for those users that want to write a Python module. The modules installed in the predefined folder need to satisfy several requirements to be considered for execution within OnTask. More precisely, each module must be stored in its own folder (as a Python module). The file ``__init__.py`` in the module must contain:

1. Module variable ``class_name`` with the name of the class in the file that contains the required definitions.

#. The definition of a class with the name stored in the previous variable. The class must inherit either from ``dataops.plugins.OnTaskTransformation`` or ``dataops.plugins.OnTaskModel``.

#. Class field ``name`` with the transformation name to show to the users.

#. Class field ``description_txt`` with a string with the detailed description of what the transformation does

#. Class field ``input_column_names`` with a potentially empty list of column names (strings). If the list is empty, the columns are selected by the user at execution time.

#. Class field ``output_column_names`` with a potentially empty list of names (strings) of the columns to be used for the output of the transformation.

#. Class field ``parameters`` with an optionally empty list with tuples with the following structure:

   ``('name', type, [list of allowed values], initial value, help_text)``


   These elements will be requested from the user before executing the transformatino through a form. The conditions on these values are:

   - name must be a string

   - type must be a string equal to "integer", "double", "string",
     "datetime" or "boolean".

   - The list of values is to restrict the
     possible values

   - The initial value must be of the type specified by the second
     element.

   - Help_text a string to show as help text

#. Class method ``run`` that receives:

   - a pandas data frame with the data to process

   - a string with the name of the key column that will be used to merge
     the result.
   - A dictionary of pairs (name, value) with the parameters described in
     the previous element.

   an d returns a result Pandas data frame. This frame **must** have one
   column with the key column name provided so that it can be properly
   merged with the existing data.

If a transformation does not comply with these properties the system administrator will see a summary of these checks to diagnose the problem.

.. figure:: /scaptures/dataops_plugin_diagnostics.png
   :align: center
   :width: 60%

See the section :ref:`plugin_write` for an example of a module.

