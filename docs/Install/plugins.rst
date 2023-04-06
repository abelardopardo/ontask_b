.. _plugin_install:

Plugins
*******

OnTask allows also the inclusion of arbitrary Python modules to execute and transform the data stored in a workflow. The Python code in the plugins is executed the same interpreter and execution environment as the rest of the platform. Thus, **use this functionality to execute only code that is fully trusted**. There is nothing preventing a plugin to run malicious code, so use at your own risk. To configure the execution of plugins follow these steps:

1. Create a folder at any location in your instance of OnTask to store the Python modules. OnTask assumes that each directory in that folder contains a Python module (that is, a folder with a file ``__init__.py`` inside).

#. Open the administration page of OnTask as superuser and go to the section with title `Data Upload/Merge Operations`.

#. Select the `Preferences` section.

#. Modify the field `Folder where plugins are installed` to contain the absolute path to the folder created in your systems.

#. Make sure that the Python interpreter that is currently executing the Django code is also capable of accessing and executing the code in the plugin folder.

#. Restart the server to make sure this variable is properly updated.

#. To create a new plugin first create a folder in the plugin space previously configured.

#. Inside this new folder create a Python file with name ``__init__.py``. The file has to have a structure a shown in :download:`the following template <__init__.py>`:

   .. literalinclude:: __init__.py
      :language: python

#. The menu *Dataops* at the top of the platform includes the page *Transform* that provides access to the plugins and its invocation with the current workflow.

