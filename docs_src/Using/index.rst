.. _using:

**************
Using the tool
**************

.. contents:: Contents
   :local:
   :backlinks: none
   :depth: 3

In a nutshell, the idea of OnTask is to help instructors, learners and designers to exchange data  about what is happening in a learning experience to design and deploy personalized learner support actions. This last term, *personalized support actions* is purposefully vague to include any action that is offered to learners in different forms depending on personalized conditions. The typical *workflow* to use OnTask starts by uploading and combining available data about the learning experience, either provided through some platform (LMS, video platform), provided by the students (questionnaires), or reported by the instructors. The instructors then write simple rules to select a subset of students and create a resource (HTML page, a message, a visualization) so that its content depends on the data available for each learner. The following figure shows an illustration of this workflow:

.. figure:: ontask_workflow.png
   :align: center
   :width: 100%

Imagine a learning experience in which you want to provide personalized messages to the learners in three instances. In the first week, you want to send a welcome email and change slightly the text based on the student background (courses taken before this one). The second week you want to send some comments and suggestions about the participation in the forum and the text will depend on the measures of engagement obtained from the platform. Finally, you want to send a third personalized email depending on the level of engagement with the videos in the course. The idea of these messages is that you want to change the text in the message for each learner based on the information stored in the table.

The main entity in the platform is a :ref:`*workflow* <workflow>` and represents a set of data capturing procedures, a table with current data, and a set of actions. The usual steps require first to populate the table with data extracted from the learning environment. In the figure we assume a variety of data sources ranging from those coming from the use of technology, self-reported by the students, or observed and reported by the instructors.

These three sources are combined and stored in the second entity in OnTask: the table. Think of the table as a conventional excel sheet storing the information about the learners (one learner per row and a set of features about each learner as columns).

The third entity in OnTask is the *personalized action* that is a text with elements that are selected and adapted to each learner based on a set of basic rules that depend on the student features stored in the table. This text can be included in an email, made available through a web page, or forwarded to another system for further processing.

A workflow in OnTask contains a single table (rows and columns) and a set of actions. This container is conceived to manage the data and actions related to a learning experience. You may use the workflow shown in the documentation importing  the :download:`initial workflow <../../initial_workflow.gz>`.

The following sections offer a more in-depth description of all these elements as well as examples with real scenarios.

.. _workflow:

The Workflow
============

    "But anyone who has experienced flow knows that the deep enjoyment it provides requires an equal degree of disciplined concentration."
    -― Mihaly Csikszentmihalyi

The workflow in OnTask is an entity that contains the data table and the actions (personalized content, emails, surveys). The initial screen in OnTask shows the available workflows as ilustrated in the following figure.

.. figure:: /scaptures/workflow_index.png
   :align: center
   :width: 100%

Clicking in the *Home* in the top menu bar brings you back to this page. Clicking in the book icon in the upper right side of the menu bar opens the documentation page.

For every workflow available in the home screen the following operations are available:

.. sidebar:: Going back

   Clicking in the *Home* link at the top left corner *closes* brings you back to the list of available workflows **and** unlocks or the workflow you were manipulating up to that point.

.. _workflow_create:

1. *New workflow* This button opens a dialog to introduce the name and description of a new workflow, and then go to the page to upload data.

.. _workflow_import:

2. *Import workflow*: This button opens a dialog requesting a workflow name and a file containing a previously exported OnTask workflow as shown in the following figure:

   .. figure:: /scaptures/workflow_import.png
      :align: center
      :width: 100%

Each of your workflows is represented by a card as shown in the following figure:

.. figure:: /scaptures/workflow_card.png
   :align: center
   :width: 60%

The icons in the bottom part of this element allow you to perform the following operations:

1. *Open a workflow*: Click in either the workflow box or the *Open* link. This operation opens the workflow and selects it for further manipulation. The name of the currently open workflow is always shown right under the top navigation bar as illustrated in the following figure.

   .. figure:: /scaptures/navigation_bar.png
      :align: center
      :width: 100%

2. *Change name or description*: Click in this icon to change the name of the descxription given to the workflow.

3. *Create a duplicate*: This operation will create an exact copy of the workflow with the prefix *Copy_of_* added to the current workflow name.

4. *Delete all data*: This operation removes the information and actions stored in the workflow (turns it into an empty workflow).

5. *Delete the workflow*: Remove the workflow completely from the system.

Once you open a workflow, the platform *locks it* so that no other user can manipulate it (see :ref:`sharing a workflow <details_sharing>`). If you access a workflow and another user is currently using it, the platform will not allow you to see the data and will show who is holding the lock.

The operations to manage a workflow all become visible once you select it by clicking on its name.

.. _dataops:

Data Table
==========

    "May be stories are are just data without a soul"
    -- Brené Brown


This section describes the operations to upload and merge data into the table. It may be the case that this task is already done, or it is done automatically before you work with a workflow. If this is the case, you may skip this section. The data operations page offers various options to upload and merge data to the table and the process is divided into several steps. This functionality is available from the *Details*, *Table* or *Actions* screens.

Upload Data
-----------

If the table in a workflow is empty, OnTask allows to upload data from various sources. If, on the other hand, the table already contains data, then OnTask performs a *merge* operation in which the existing data is combined with the new data.

Upload CSV Files
^^^^^^^^^^^^^^^^

CSV or "comma separated value" files are plain text files in which the first line contains a comma-separated list of column names, and every subsequent line contains the values of these columns for each row. It is a popular format to exchange data that can be represented as a table, and it is for this reason that OnTask allows to upload data in this format.

This operation allows you to upload the values in a CSV file into the workflow table.

.. figure:: /scaptures/dataops_csvupload.png
   :align: center

In some cases, the comma-separated values are surrounded by several lines that need to be ignored when processing the data. The page to upload the CSV file allows you to specify the number of lines to ignore at the start and end of the file.

Upload Excel Files
^^^^^^^^^^^^^^^^^^

OnTask also supports the upload of data from Excel files.

.. figure:: /scaptures/dataops_upload_excel.png
   :align: center

In this case the file is assumed to have multiple *Sheets* and one of them
has to be selected to upload the data.

.. _google_spreadsheet_file:

Upload Google Spreadsheet Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OnTask allows you to upload a data table stored in a Google Spreadsheet that is publicly accessible.

.. figure:: /scaptures/dataops_upload_gsheet.png
   :align: center



.. _sql_connection_run:

SQL connection
^^^^^^^^^^^^^^

The third method to upload data into the current workflow is through a SQL connection to a remote database. These connections have to be :ref:`previously defined and configured by the system administrator <sql_connections>`. Instructors can use them to access the content of a previously defined table in a remote database. The option to upload data with a SQL connection shows the available connections and the possibility to *Run* each one of them:

.. figure:: /scaptures/dataops_SQL_available.png
   :align: center

When *running* a SQL connection the platform shows the configuration parameters and requests the password to access the remote database (if required).

.. figure:: /scaptures/dataops_SQL_run.png
   :align: center

When uploading data for the first time, the values are prepared to be assigned as the initial content of the table. Before this assignment is done, the platform first automatically detects those columns that have unique values (no repetitions) and marks them as *keys*. Key columns are very important because the values (as they are different for every row) are used for various operation. There must be **at least one key column** in the workflow and it is possible to remove the *key* mark from any column and only possible to mark a column as key if the values are all different. Before assigning the data to the table, the platform also allows to change the name of the columns as shown in the Step 2 of the upload process.

.. figure:: /scaptures/dataops_upload_merge_step2.png
   :align: center

After this step (if the table is empty), the data is stored and the platform shows the :ref:`details` page. If the upload operation is executed with a workflow with existing data in the table, then instead of an upload, the platform executes a **merge** operation.

.. _data_merge:

Data Merge
==========

.. sidebar:: Merge a.k.a "Join"

   Merging is a common operation in databases and is commonly known as *join*. There are several variants of join operations depending how the differences between the key columns are handled. These same variants exist when combining columns in data frames (or a table).

A merge operation is required when uploading a set of columns with an **already existing table**. This operation is very common in data science contexts. One of the problems is to specify how the values in the columns are *matched* with respect to the ones already existing in the table. In other words, each new column has a set of values, but they need to be in the right order so that the information is matched appropriately for every row. The solution for this problem is to include in both the existing table and the new data being merged a **unique or key column**. These columns have the property that uniquely distinguish each row with a value and therefore they are used to make sure that rows with matching values in these columns are merged. When uploading data into a workflow that already contains data in its table, the platform automatically executes additional steps to complete a *merge* operation.

After detecting the key columns and offering the option of changing their names, the following steps requires to identify the key columns used to match rows from the existing table and the one being uploaded.

.. figure:: /scaptures/dataops_upload_merge_step3.png
   :align: center
   :width: 100%

Key columns
  You have to select a key column present in the table to be merged (mandatory) and a key column from the existing table (mandatory).

Merge method
   Once you choose a merge method, a figure and explanation appear below.There are four possible merging methods:

  Select only the rows with keys in both existing **and** new table
    It will select only the rows for which values in both key columns are present. Or in other words, any row for which there is no value in either of the key columns **will be dropped**.

    .. figure:: ../../src/media/merge_inner.png
       :align: center

  Select all rows in either the existing or new table
    All rows in both tables will be considered. You have to be careful with this option because it may produce columns that are no longer unique as a result.

    .. figure:: ../../src/media/merge_outer.png
       :align: center

  Select the rows with keys in the existing table
    Only the rows in the new table with a value in the key column that is present in the existing table will be considered, the rest will be dropped.

    .. figure:: ../../src/media/merge_left.png
       :align: center

  Select the rows with keys in the new table
    Only the rows in the existing table with a value in the key column that is present in the key column from the new table will be considered, the rest will be dropped.

    .. figure:: ../../src/media/merge_right.png
       :align: center

In any of these variants, for those columns that are present in both the existing table and the new table, the values of the second will update the existing ones. This updating operation may introduce non-values in some of the columns. You have to take extra care when performing this operation as it may destroy part of the existing data. In the extreme case, if you try to merge a table with a key column with no values in common with the existing key and you select the method that considers rows with keys in both the existing and new table, the result is an empty table.

After selecting these parameters the last step is to review the effect of the operation and proceed with the merge as shown in the following figure.

.. figure:: /scaptures/dataops_upload_merge_step4.png
   :align: center

.. _table:

The Table
=========

   "You're here because you know something. What you know you can't explain,
   but you feel it"
   -- Morpheus, The Matrix

This functionality is to show the values stored in the workflow. Since this data can be arbitrarily large, it is likely that only a portion of the columns is shown on the screen at any given point.

.. figure:: /scaptures/table.png
   :align: center
   :width: 100%

The buttons at the top of the page allow to execute several operations.

.. figure:: /scaptures/table_buttons.png
   :align: center
   :width: 100%

Add row
  A form to introduce a new row in the table with one field per column.

Add Column
  The options to add a regular column, a column with values calculated with a formula, or a column with random values (See :ref:`Adding a column <details_add_column>` for a detailed explanation).

Manage table data
  Menu to upload/merge data to the table or execute a plugin (See :ref:`dataops` for a detailed explanation).

Views
  Menu to either show a subset of the table (a view) or manage the views in the workflow (described in :ref:`the next section <table_views>`).

Dashboard
  The dashboard is a page that shows a statistical summary for the columns shown in the table. This number may be too high, so you should consider using :ref:`table_views` to simplify the information shown.

CSV Download
  This functionality allows to obtain a CSV file with the data shown on the screen. Combine this functionality wit the :ref:`table_views` to handle large tables.

The rows shown in the screen are automatically grouped into pages (you may choose the number of entries per page in the upper left side of the table). Additionally, the table offers a search box in the the upper left corner. The operations in the left side of the row allow you to access a statistical summary of the values in the row, edit any of the values or delete the row.

.. _table_views:

Table Views
-----------

Due to the potentially large size of this table in either number of rows or columns, OnTask offers the possibility to define *views*. A view is simply a table that shows a subset of columns and rows. You may define as many views as needed for the table.

.. figure:: /scaptures/table_views.png
   :align: center
   :width: 100%

When creating or editing the content of the view, aside from the name and the description, you may select those columns to show, and a expression to restrict the rows to those for which that expression is correct (you may leave this expression empty and all rows will be shown).

.. figure:: /scaptures/table_view_edit.png
   :align: center
   :width: 100%

Once defined, you may select the view to show the corresponding data subset.

.. figure:: /scaptures/table_view_view.png
   :align: center
   :width: 100%

The *Dashboard* and *CSV Download* buttons, when used while using a view, will apply to the selected data subset.

.. _action:

The Actions
===========

    "In order to carry a positive action we must develop here a positive
    vision"
    -- Dalai Lama

This is the most important functionality of the platform. Actions are used exchange information with the learners, either offering a personalized document, or requesting data. A workflow contains an arbitrary number of actions shown in the *Table* page.

.. figure:: /scaptures/actions.png
   :align: center
   :width: 100%

Each action is identified by a name (unique) and an optional description. OnTask currently offers the following types of actions: personalized text, personalized JSON, and surveys. The action table shows also the operations available for each of them (right most column in the table shown in the previous figure).

.. _personalized_content:

Personalized Content
--------------------

These actions allow to create a resource (similar to a HTML page) and mark certain elements with *conditions* that will control if they are included or ignored when showing the document. Think of this personalized content as a resource (message, tip, comment) you would offer learners but with content that is different depending on the data stored in the table. You may have several of these items prepared to be used at different points during the experience. The personalized content action is manipulated with the screen shown in the following figure:

.. figure:: /scaptures/action_edit_action_out.png
   :align: center
   :width: 100%

Before describing in detail the structure of this screen let's explore the concept of *condition*. A condition is an expression that when evaluated will either be **True** or **False**. These expressions are commonly used in other applications such as spreadsheets or programming languages. The following image shows an example of this condition.

.. figure:: /scaptures/action_action_out_edit_filter.png
   :align: center

The expression in the previous figure is contained under the title **Formula** and can be read as:

  Video_1_W4 = 0 or Video_2_W4 = 0

The first element of the expression is the sub-expression ``Video_1_W4 = 0`` which contains the variable ``Video_1_W4``, the equal sign, and the constant zero. The second element is a sub-expression with the variable ``Video_2_W4``, the equal sign, and the constant 0. These two sub-expresssions are connected through the **OR** operator, which means that the expression will be **True** if either of the sub-expressions are **True**, and **False** in any other case. When evaluating this expression, the variables are replaced by concrete values (numbers). For example, if ``Video_1_W4`` is replaced by 3, and ``Video_2_W4`` is replaced by 4, the evaluation will transform the expression into :math:`3 = 0 or 4 = 0`. The sub-expression :math:`3 = 0` is clearly **False** and so is the other sub-expression :math:`4 = 0`. This means the initial expression is **False**. result is either **True** or **False**. Another possible evaluation is if ``Video_1_W4`` is equal to zero (and ``Video_2_W4`` remains equal to 4). In this case the resulting expression is :math:`0 = 0 or 4 = 0`. In this case, the first sub-expression is **True**, and although the second is **False**, only one is needed for the overall expression to be **True**.

These conditions can have nested sub-expressions and get complex fairly quickly. However, the underlying mechanism to evaluate them remains the same: replace variables with values and decide the result (**True** or **False**). OnTask relies on these expressions to personalize the content of the actions. Let's now go back to the screen to edit an action. The area has four components

The filter
  The top area contains a *filter*. This element is an expression used to decide which learners (or more precisely, the corresponding rowsin the data table that) will be selected and used in this action.

  .. figure:: /scaptures/action_action_out_filterpart.png
     :align: center
     :width: 100%

  In the example above, the expression selects 3 out of all 14 learners in the data table. This filter is useful when you want to provide the personalized text to a sub-set of the learners. For example, you may want to send a reminder about the submission deadline the day before but only to those students that haven't connected to the system. If you have that informatio in a column of the data table, you may create the condition that selects only those learners.

The conditions
  This area contains additional expressions called *conditions*.

  .. figure:: /scaptures/action_action_out_conditionpart.png
     :align: center
     :width: 100%

  A condition is another expression (identical to the filter) but it will be used in the middle of the text to decide if a portion of the text will be shown or ignored. The buttons in the screen allow you to edit the expression, insert the condition to control the appearance of text in the editor (below), clone the condition, or delete it from the action.

  For each condition, the button shows the number of learners for which the expression in that condition evaluates to **True**. If this value is zero, it means that any text you include in the editor surrounded by this condition will not appear for any of the learners.

The HTML text editor
  This is the area to create the personalized document. It is a conventional HTML editor offering the usual functionalities (inserting text in various forms, headings, lists, links, images, etc.) Right above the editor window you have two choice menus that you can use to insert either a :ref:`workflow attribute <details_attributes>` or a column name that will be replaced by the corresponding value.

  .. figure:: /scaptures/action_action_out_editorpart.png
     :align: center
     :width: 100%

The Preview button
  The Preview button shows how the text in the editor is shown for those
  learners selected by the filter (if any). After clicking in the button you
  will see a window with the resulting text. If there are any elements in the
  text that are controlled by any condition, the bottom area will show their
  values.

  .. figure:: /scaptures/action_action_out_preview.png
     :align: center
     :width: 100%

  Use the arrow buttons to see all the different versions of the text
  depending on the values stored in the table for each learner.

  .. figure:: /scaptures/Ontask____howtopreviewtext.gif
     :align: center

The Save button
  This button saves the content of the text editor and returns to the page
  showing all the actions in the workflow.

Using column values, attributes and conditions in a Personalized Text
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The text in these actions may include three types of elements that
are personalized for each learner: an attribute name, a column name or a
portion of text marked with a condition.

Attributes
  Attributes are simply synonyms that you may want to use in more than one
  action. For example, if you have several actions that include the name of a
  course, instead of including that name if all actions, you may define an
  *attribute* with name *course name* and value *Biology 101* and include in
  the actions the attribute name. OnTask will replace that attribute with its
  value when showing the text to the learners. If you then change the name of
  the course (or you export this workflow and import it to be used in
  anotehr course), you only need to change the attribute and the name of the
  course will appear correctly in all actions (in what is called a *single
  point of change*).

  To insert an attribute name in the text simply place the cursor in the
  editor where you want the value of that attribute to appear and select
  the attribute from the area above the editor. The name of the attribute
  will be inserted in the text surrounded by double curly braces, (for
  example ``{{ course_name }}``. Only :ref:`the attributes <details_attributes>`
  you previously created in the details page are available.

Column names
  The other element that can be personalized is a column name. For example,
  suppose you have a column in your table with the first name of the learners.
  You can use the column name to personalize the greeting in the text.
  To insert a column name, you follow the same steps used for the attribute but
  this time you select the column name from the pull-down menu. You will see
  that the name of the column appears in the text also surrounded by
  double curly braces (for example ``Hi {{ GivenName }}``. The double curly
  braces is the way OnTask has to mark that text to be personalized or
  replaced by the corresponding value for each learner extracted from the data
  table.

Conditional text
  Using a condition to control if a portion of the text is shown or
  ignored is slightly different. First highlight the text you want to appear
  depending on the condition in the
  editor. Then go to the corresponding button for the condition, click in the
  arrow next to its name, and select *Insert in text*. The text will be
  surrounded by two marks. For example
  if the condition name is ``Video_active``, the text you highlighted will
  appear in the editor afer clicking in the *Insert in text* as::

    {% if Video_active %}Good work with this week's video{% endif %}

  This format marks the message *Good work with this week's video* to
  appear only for those learners for which the condition ``Video_active``
  evaluates to **True** with their current values in the data table.
  Otherwise, the text will be ignored. The following figure illustrates this process.

  .. figure:: /scaptures/Ontask____howtocreatetext.gif
     :align: center
     :width: 100%

Personalized JSON Object
------------------------

This type of action allows the creation of a `JSON object <https://www.json.org/>` with content that is personalized with the same functionality as described in the section about :ref:`Personalized Content <personalized_content>`. The difference is that instead of creating a text, the action creates a JSON object that will eventually be sent to another platform for further processing. This object is also a resource that is different for every student but the difference is that instead of being prepared to be visualized, it is packaged with a structure suitable to be received by another platform through a URL.

The screen to create a Personalized JSON object is shown in the following figure.

.. figure:: /scaptures/action_personalized_json_edit.png
   :align: center
   :width: 100%

The areas number 1 and 2 have the same functionality than in the case of :ref:`personalized text <personalized_content>`. The first area allows the definition of an expression to select a subset of rows in the table for processing. The second area contains the conditions that can be used within the body of the JSON object to select content (in exactly the same way as in the :ref:`personalized text <personalized_content>`). The text shown in the previous figure defines a JSON object with three fields ``sid``, ``midterm_total`` and ``msg``. The first two contain column names that will be replaced by their corresponding values. The field ``msg`` will include one of the two messages depending on the value of the conditions.

The third area contains the editor to create the JSON object followed by an extra field to specify the target URL where the objects will be submitted.

The preview button in the perosnalized JSON action shows the resulting object after verifying that the structure after evaluating the corresponding expressions is a valid JSON object.

.. _personalized_emails:

Sending personalized emails
---------------------------

Once you created a personalized text action and verified its content using the
*Preview* button, save its content. The right-most column shows a button with
name *Email*. Click on that button.

.. figure:: /scaptures/action_action_ops.png
   :align: center

The following screen shows a form to introduce the required parameters to
send the personalized text to each learner by email.

.. figure:: /scaptures/action_email_request_data.png
   :align: center

The subject
  A line to be included as subject of all the emails.

The column with the email address
  OnTask needs to know where to send the email. It assumes that you have a
  column containing that information for each learner and it needs you to
  select that column.

List of emails in CC
  A comma-separated list of emails to include in the *carbon copy* or *CC*
  email field.

List of emails in BCC
  A comma-separated list of emails to include in the *blind carbon copy* or
  *BCC* email field.

Send a summary message
  If you select this option OnTask will send you an email with the summary of
  this operation (number of rows in the table that were selected by the
  filter, number of emails sent, date/time of the operation, etc.

Track email reading
  Include in the messages a HTML snipped to detect if the email is read.
  OnTask adds an extra column to the table to store the number of times the
  message is opened. This detection relies on how the email client opens the
  message and processes the included images, therefore, the information in
  this column may not accurately reflect this information.

Snapshot of the workflow
  If you select this option, after the emails are sent, the platform returns
  you a file that contains a snapshot (picture) of the workflow. It basically
  freezes the content of the workflow and places it in a file given to you.
  You may take this file and :ref:`import back the workflow <workflow_import>`.
  In this new workflow you can check the values and messages at the time the
  operation was executed.

Check/exclude emails
  If selected, this option inserts an extra step in which you can eliminate
  certain emails form the action. This feature is useful to remove certain
  emails that cannot be removed with the filter.

Once these fields are provided, the operation is queued in a batch system and processed separated from the web application.

.. _personalized_canvas_emails:

Sending personalized emails in Canvas
-------------------------------------

If :ref:`appropriately configured <canvas_email_config>`, OnTask allows to send the emails to the internal email service in a `Canvas Learning Management System <https://www.canvaslms.com.au/>`_. The messages delivered with this service need to be created with a special action of type *Personalized Canvas Email*.

.. figure:: /scaptures/action_personalized_canvas_email_create.png
   :align: center
   :width: 100%

The definitions of a filter and text conditions are identical to those used in the :ref:`personalized content actions <personalized_content>`. The body of the email can only contain plain text without any HTML markup.

.. figure:: /scaptures/action_personalized_canvas_email_edit.png
   :align: center
   :width: 100%

Once a *Personalized Canvas Email* action has been created, it will appear in the action table with the rest of actions and with the possibility of execute the *Email* operation. Before sending the messages OnTask requests the following data:

- Column in the table containing Canvas ID values. This column is essential to send the emails to the platform as it is used to uniquely identify every Canvas user. The data can be obtained downloading the marks of a course as a CSV file and uploading and merging this column as part of the table.

- Email subject: The text to use as subject for the messages.

- If there is more than one Canvas platform configured in OnTask, an additional pull-down menu will appear to select which one to use. If there is a single Canvas platform configured, it will be used by default and this field will not be shown in the form.

- Check/Exclude Canvas IDs before sending messages. As in the case of the other actions that send email, if selected OnTask adds an extra step to check those identifies and exclude some of them.

- Download a snapshot of the workflow. If selected, a snapshot of the workflow (data and actions) will be downloaded after the messages have been queued for delivery.

.. figure:: /scaptures/action_personalized_canvas_email_run.png
   :align: center
   :width: 100%

After introducing this data, OnTask will check if it has credentials for the user to access Canvas. If not, the user will be redirected to a page in the Canvas Learning Management System to 1) authenticate, and 2) authorize the access to the platform through OnTask. If these steps are successful, the user is redirected back to OnTask and the messages are delivered. The credentials retrieved from Canvas will be reused for future executions of actions requiring access to Canvas.

Making personalized content available to learners
-------------------------------------------------

Sending a personalized email is just one possible way to make this content
available to learner. Another one is to offer the content
through a URL that can be given to the learners. To enable such URL click in
the button labeled ``URL`` followed by either the word ``(Off)`` or ``(On)``.

.. figure:: /scaptures/action_action_ops.png
   :align: center

The following window shows the URL in which the content is available as well
as the field to enable/disable it.

.. figure:: /scaptures/action_URL_on.png
   :align: center
   :width: 60%

In order for the learners to be able to view their personalized content,
they have to be users of the OnTask platform. This functionality is
conceived for a context in which OnTask authenticates users either through
a corporate Single-sign on layer, or learners access the OnTask through the
Learning Management System with a LTI interface (see :ref:`authentication`).

Sending personalized JSON objects to another platform
-----------------------------------------------------

The analogous operations for personalized JSON actions is to send the resulting objects to the given URL and is available when clicking in the ``Run`` button. The execution of these actions require two fields.

.. figure:: /scaptures/action_json_run_request_data.png
   :align: center
   :width: 100%

The first field is the column to perform a last review of the elements to send and select some of them to exclude in an extra step. If the field is empty, this step is skipped. The second field is the token to use for authentication when sending the JSON objects to the URL given when editing the action.

Similarly to the email actions, once these fields are provided, the operation to send the JSON objects to the target URL is queued in a batch system and processed separated from the web application.

Creating a ZIP file with the personalized text
----------------------------------------------

The personalized text actions offer the possibility of creating a ZIP file containing one HTML file per personalized text. You may use two columns and a fixed suffix to control the format of each file name.

.. figure:: /scaptures/action_zip_request_data.png
   :align: center
   :width: 100%

The first part of the file name is taken from the values of a key column. The second part of the file name is taken from a second column (optional). Additionally, the user may include a third suffix to be used for the last part of the file name (if none is given the default suffix is ``feedback.html``. For example if the first column has the values ``submission 01, submission 02, submission 03``, the second column has the names ``John, Paul, Mary``, and the file suffix is empty, the ZIP file will be created with three HTML files with names ``submission 01_John_feedback.html``, ``submission 02_Paul_feedback.html`` and ``submission 03_Mary_feedback.html``.

.. _upload_feedback_to_moodle:

Uploading feedback files for a Moodle Assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


Surveys
-------

The personalized text actions described in the previous section is
information made available to the learners. The *survey* actions collect
information from the learners and store it in the table. This functionality
is a simplified version of other survey engines such as Google Forms,
SurveyMonkey or Quantrix. In a learning context a survey can be used equally
to ask students to submit certain data, or for an instructor to collect
annotations about learners throughout the experience.

When you edit a survey action, the editor contains the elements shown in the
following figure:

.. figure:: /scaptures/action_edit_action_in.png
   :align: center
   :width: 100%

From top to botton, the first area in the screen is a filter to restrict the
learners in the table considered for data entry. This functionality is
identical to the one described for the personalized text. Those learners for
which the condition in the filter is true, area considered for data entry. The
second area is text that will be shown at the top of the page requesting
the data. The next section is they key column used to match the data entry
with the user authentication, typically the column that contains the user
email. The last section of the screen is a set of non-key table columns, each
one of them corresponding to one question in the survey. If a column is
included in the survey, its description text is shown as the *question text*.
The *Preview* button at the bottom of the page shows the content as it will be
shown to the learners.

.. figure:: /scaptures/action_action_out_preview.png
 :align: center
 :width: 100%

Running a survey action
^^^^^^^^^^^^^^^^^^^^^^^

After creating a *survey action* there are two operations available
represented by the buttons with labels *Run* and *URL*. The *Run* is intended
for the instructors to enter the data for each learner. After
clicking the link, the platform shows a table with the learners considered
for the survey action as well as the data collected so far. Each row contains
a link to access the data entry screen. The table has a search box in the
upper left corner to quickly find a person.

.. figure:: /scaptures/action_run_action_in.png
   :align: center
   :width: 100%

Instructors may click in the link available in the right-most column to
either enter new information or modify the already existing information for
that learner.

.. figure:: /scaptures/action_enter_data_action_in.png
   :align: center
   :width: 100%

After entering the information the list of students for
which the data entry is still allowed.

Offering the survey to the learners
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The second operation available for *survey* actions is to make available the
URL to learners so that theyindividually enter the information themselves. In
the action table each survey action has a button labeled *URL*. If you click
in this button the screen shows the URL for the survey and the possibility of
enable/disable it or even provide a date/time window for its availability.

.. figure:: /scaptures/action_action_in_URL.png
   :align: center
   :width: 80%

Once enabled, you may send the URL to the students (you may even use a personalized text action for that). Once the students click in the action, after authentication, and if their email is part of hte table, they will be able to enter the information and the values are automatically stored in the right row and column in the table.

These survey actions are ideal to collect information about any aspect of a course in a way that is centralized and available for further processing through personalized text actions. For example, users may choose from a pre-defined set of topics those that were more challenging. This information can then be used in a personalized text action to provide the adequate resources to each learner.


.. _workflow_settings:

Workflow Settings
=================

[SOME TEXT GOES HERE]

.. include:: include_details.rst

.. _scheduler:

Scheduled Actions
-----------------

   "I have no regular schedule. I get up whenever I can."
   -- Jimmy Wales


The *personalized text* and *personalized JSON* actions can be scheduled to execute at some point in the future. To schedule the execution go to the *Actions* page (select the option from the top menu), click in the *More* button for the action and then in the button *Schedule*.

.. _schedule_email:

Scheduling a Personalized Text Action
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
  If selected, this option inserts an extra step select emaisl and eleminate them from the action. This option is useful to perform a final check and remove emails that cannot be removed with action the filter.

.. _schedule_json:

Scheduling a Personalized JSON Action
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

The Scheduler Menu
^^^^^^^^^^^^^^^^^^

The *Scheduler* in the top menu is a link to a page that shows the tasks scheduled for execution in the selected workflow.

.. figure:: /scaptures/schedule.png
   :align: center

The left-most column offers the operations to edit or delete the scheduled execution.

.. _logs:

View Logs
---------

The platform keeps a log of most of the operations that are executed when managing a workflow. These records are available through the *Logs* link in the navigation bar at the top of the screen.

.. figure:: /scaptures/logs.png

You may download all logs as a CSV file.

.. _plugin_run:

Plugins -- Transforming the data with your own code
===================================================

The additional method offered by OnTask to manipulate the data in a workflow's table is to execute arbitrary Python code encapsulated as a Python module and placed in a predefined folder in the computer hosting the server. In the context of the platform, these Python modules are called **Plugins** and require some :ref:`previous configuration <plugin_install>`. Before their execution, a plugin must be written and installed in the folder previously considered for that purpose.

The purpose of the plugins is to allow arbitrary transformations of the data attached to a workflow. The list of plugins available for execution can be accessed through the link *Transform* in the *Dataops* top menu item.

.. figure:: /scaptures/dataops_transform_list.png
   :align: center

Each plugin is shown with a (unique) name, a description, the last time the code was modified (based on the file modification time), if the plugin is ready to execute, and the link for either the *Run* operation, or a link to the diagnostics if the execution is not possible.

The plugin execution request shows a form to collect the parameters required for the operation.

.. figure:: /scaptures/dataops_transformation_run.png
   :align: center

Input columns
  The columns from the data table that will be passed to the plugin. The plugin can define a set of *fixed* column names to extract. If this list is empty, the list is requested from the user.

Key column for merging
  The plugins are supposed to create additional columns, and they need to be merged with the existing data. For this procedure, a key-column is needed to make sure the rows of the newly created data are correctly stored. They key column from the current data frame is added as part of the input data frame passed to the plugin.

Output column names
  The plugins defines the names of the result columns. However, the upon execution, the user may rename any of those columns.

Suffix to add to the result columns
  This field is provided to do a one-place renaming. If given, this suffix is added to the names of all output columns.

Execution parameters
  This part of the form requests the pairs *(name, value)* as defined by the plugin.

After the appropriate data is provided the tool shows a plugin executing report showing the columns that will be created and how will they be merged with the existing data.

.. _plugin_requirements:

Plugin requirements
-------------------

The Python modules installed in the predefined folder need to satisfy various requirements to be considered for execution within OnTask. More precisely, the file ``__init__.py`` must contain:

1. Module variable ``class_name`` with the name of the class in the file that contains the required definitions.

1. Class field ``name`` with the plugin name to show to the users.

2. Class field ``escription_txt`` with a string with the detailed description of what the
   plugin does

3. Class field ``input_column_names`` with a potentially empty list of column names
(strings). If the list is empty, the columns are selected by the user at
execution time.

4. Class field ``output_column_names`` with a non empty list of names (strings) of the
columns to be used for the output of the transformation.

5. Class field ``parameters`` with an optionally empty list with tuples with the following
structure:

   ``('name', type, [list of allowed values], initial value, help_text)``


   These elements will be requested from the user before executing the
   plugin through a form. The conditions on these values are:

   - name must be a string

   - type must be a string equal to "integer", "double", "string",
     "datetime" or "boolean".

   - The list of values is to restrict the
     possible values

   - The initial value must be of the type specified by the second
     element.

   - Help_text a string to show as help text

6. Class method ``run`` that receives:

   - a pandas data frame with the data to process

   - a string with the name of the key column that will be used to merge
     the result.
   - A dictionary of pairs (name, value) with the parameters described in
     the previous element.

   an d returns a result Pandas data frame. This frame **must** have one
   column with the key column name provided so that it can be properly
   merged with the existing data.

If a plugin does not comply with these properties the platform shows a summary of these checks to diagnose the problem.

.. figure:: /scaptures/dataops_plugin_diagnostics.png
   :align: center


