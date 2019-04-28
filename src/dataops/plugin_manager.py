# -*- coding: utf-8 -*-


import os
import time
from builtins import map, str, zip
from datetime import datetime

import pandas as pd
import pytz
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _, ugettext

from dataops import pandas_db, ops
from dataops.plugin import OnTaskPluginAbstract
from logs.models import Log
from . import plugin, settings
from .models import PluginRegistry


def get_plugin_path():
    plugin_folder = str(getattr(settings, 'PLUGIN_DIRECTORY'))

    if os.path.isabs(plugin_folder):
        return plugin_folder

    return os.path.join(ontask_settings.BASE_DIR, plugin_folder)


def verify_plugin(plugin_instance):
    """
    Run some tests in the plugin instance to make sure it complies with the
    requirements. There is probably a much better way to do this, but it'll
    have to do it by now. The tests are:

    1. Class inherits from OnTaskPluginAbstract

    2. Class has a non empty __doc__

    3. Presence of string field "name"

    4. Presence of string field "description_txt

    5. Presence of a list of strings (possibly empty) with name
       "input_column_names"

    6. Presence of a list of strings with name "output_column_names". If the
       list is empty, the columns present in the result will be used.

    7. Presence of a dictionary with name "parametes" that contains the
       tuples of the form:

       key: (type string, [list of allowed values], initial value, help text)

       Of types respectively:

       key: string
       type string: one of "double", "integer", "string", "boolean", "datetime"
       list of allowed values: potentially empty list of values of the type
       described by the 'type string'
       initial value: one value of the type described by 'type string'
       help text: string

    :param plugin_instance: Plugin instance
    :return: List of Booleans with the result of the tests
    """
    # Initial list of results (all false until proven otherwise
    checks = [
        _('Class inherits from OnTaskPluginAbstract'),
        _('Class has a non-empty documentation string'),
        _('Presence of a string field with name "name"'),
        _('Presence of a string field with name "description_txt"'),
        _('Presence of a field with name "input_column_names" storing a ('
          'possible empty) list of strings'),
        _('Presence of a field with name "output_column_names" storing a '
          '(possibly empty) list of strings'),
        _('Presence of a (possible empty) list of tuples with name '
          '"parameters". The tuples must have six '
          'elements: name (a string), type (one of "double", "integer", '
          '"string", "boolean", '
          'or "datetime"), (possible empty) list of allowed values of the '
          'corresponding type, an initial value of the right type or None, '
          'and a help string to be shown when requesting this parameter.')
    ]

    result = ['Unchecked'] * len(checks)
    check_idx = 0
    try:
        # Verify that the class inherits from OnTaskPluginAbstract
        if issubclass(type(plugin_instance), OnTaskPluginAbstract):
            result[check_idx] = _('Ok')
        else:
            result[check_idx] = _('Incorrect parent class')
            return list(zip(result, checks))
        check_idx += 1

        # Verify that the class has a non empty documentation string
        if plugin_instance.__doc__:
            result[check_idx] = _('Ok')
        else:
            result[check_idx] = _('Class is not documented')
        check_idx += 1

        # Verify that all the fields and methods are present in the instance
        result[check_idx] = _('Not found')
        if not isinstance(plugin_instance.name, str):
            result[check_idx] = _('Incorrect type')
        else:
            result[check_idx] = _('Ok')
        check_idx += 1

        result[check_idx] = _('Not found')
        if not isinstance(plugin_instance.description_txt, str):
            result[check_idx] = _('Incorrect type')
        else:
            result[check_idx] = _('Ok')
        check_idx += 1

        result[check_idx] = _('Not found')
        if not all(isinstance(s, str)
                   for s in plugin_instance.input_column_names):
            result[check_idx] = _('Incorrect type')
        else:
            result[check_idx] = _('Ok')
        check_idx += 1

        result[check_idx] = _('Not found')
        if not (isinstance(plugin_instance.output_column_names, list) and
                all(isinstance(s, str) for s in
                    plugin_instance.output_column_names)):
            result[check_idx] = _('Incorrect type/value')
        else:
            result[check_idx] = _('Ok')
        check_idx += 1

        result[check_idx] = _('Not found')
        if not isinstance(plugin_instance.parameters, list):
            result[check_idx] = _('Incorrect type')
            return list(zip(result, checks))

        for (k, p_type, p_allowed, p_initial, p_help) in \
                plugin_instance.parameters:

            if not isinstance(k, str):
                # The type should be a string
                result[check_idx] = _('Key values should be strings')
                return list(zip(result, checks))

            if not isinstance(p_type, str):
                # The type should be a string
                result[check_idx] = \
                    _('First tuple element should be as string')
                return list(zip(result, checks))

            if p_type == 'integer':
                t_func = int
            elif p_type == 'double':
                t_func = float
            elif p_type == 'string':
                t_func = str
            elif p_type == 'datetime':
                t_func = parse_datetime
            elif p_type == 'boolean':
                t_func = bool
            else:
                # This is an incorrect data type
                result[check_idx] = \
                    _('Incorrect type "{0}" in parameter').format(p_type)
                return list(zip(result, checks))

            # If the column is of type datetime, the list of allowed values
            # should be empty
            if p_type == 'datetime' and p_allowed:
                result[check_idx] = \
                    _('Parameter of type datetime cannot have '
                      'list of allowed values')
                return list(zip(result, checks))

            # Translate all values to the right type
            result[check_idx] = _('Incorrect list of allowed value')
            __ = list(map(t_func, p_allowed))

            # And translate the initial value to the right type
            result[check_idx] = _('Incorrect initial value')
            if p_initial:
                item = t_func(p_initial)
                if item is None:
                    return list(zip(result, checks))

            if p_help and not isinstance(p_help, str):
                result[check_idx] = _('Help text must be as string')
                # Help text must be a string
                return list(zip(result, checks))

        result[check_idx] = 'Ok'
        check_idx += 1

        # Test
        if not (hasattr(plugin_instance, 'run') and
                callable(getattr(plugin_instance, 'run'))):
            # Run is either not in the class, or not a method.
            result[check_idx] = _('Incorrect run method')
            return list(zip(result, checks))
        result[check_idx] = _('Ok')
    except Exception:
        pass

    return list(zip(result, checks))


def load_plugin(foldername):
    """
    Loads the plugin given in the filename
    :param foldername: folder where the plugin code is installed. Only the
                       folder name
    :return: A pair (instance of the plugin or None,
                     List of [diagnostic msg, test description])
    """

    try:
        ctx_handler = __import__(foldername)

        class_name = getattr(ctx_handler, 'class_name')
        if not class_name:
            class_name = getattr(ctx_handler, plugin.class_name)
        plugin_class = getattr(ctx_handler, class_name)
        # Get an instance of this class
        plugin_instance = plugin_class()

        # Run some additional checks in the instance and if it does not
        # comply with them, bail out.
        tests = verify_plugin(plugin_instance)
        if not all(x == 'Ok' for x, __ in tests):
            return None, tests
    except AttributeError as e:
        return None, [(e, _('Class instantiation'))]
    except Exception as e:
        return None, [(e, _('Instance creation'))]

    return plugin_instance, tests


def load_plugin_info(plugin_folder, plugin_rego=None):
    """
    Load the plugin and transfer the information into the PluginRegistry
    table.
    :param plugin_folder: Folder to load the information from.
    :param plugin_rego: Plugin record in the table (none if it needs to
                        be created)
    :return: Record in the DB is updated and returned.
    """

    # Load the given module
    plugin_instance, _ = load_plugin(plugin_folder)

    # If there is no instance given of the registry, create a new one
    if not plugin_rego:
        plugin_rego = PluginRegistry()
        plugin_rego.filename = plugin_folder

    if plugin_instance:
        plugin_rego.name = plugin_instance.name
        plugin_rego.description_txt = plugin_instance.description_txt
        plugin_rego.is_model = \
            hasattr(plugin_instance, '_is_model') and \
            plugin_instance.get_is_model()

    plugin_rego.is_verified = plugin_instance is not None

    # All went good
    plugin_rego.save()

    return plugin_rego


def refresh_plugin_data(request, workflow):
    """
    Function to traverse the directory where the plugins live and check if
    the folders in there are reflected in the PluginRegistry model.

    :return: Reflect the changes in the database
    """

    plugin_folder = get_plugin_path()

    pfolders = [f for f in os.listdir(plugin_folder)
                if os.path.isdir(os.path.join(plugin_folder, f))]

    # Get the objects from the DB
    reg_plugins = PluginRegistry.objects.all()

    # Travers the list of registered plugins and detect changes
    for rpin in reg_plugins:
        if rpin.filename not in pfolders:
            # A plugin has vanished. Delete

            # Log the event
            Log.objects.register(request.user,
                                 Log.PLUGIN_DELETE,
                                 workflow,
                                 {'id': rpin.id, 'name': rpin.filename})

            rpin.delete()
            continue

        if os.stat(os.path.join(plugin_folder,
                                rpin.filename,
                                '__init__.py')).st_mtime > \
                time.mktime(rpin.modified.timetuple()):
            # A plugin has changed
            __ = load_plugin_info(rpin.filename, rpin)

            # Log the event
            Log.objects.register(request.user,
                                 Log.PLUGIN_UPDATE,
                                 workflow,
                                 {'id': rpin.id,
                                  'name': rpin.filename})

        pfolders.remove(rpin.filename)

    # The remaining folders are new plugins
    for fname in pfolders:
        if not os.path.exists(os.path.join(plugin_folder,
                                           fname,
                                           '__init__.py')):
            # Skip folders that do not have a __init__.py file
            continue

        # Load the plugin info in a new record.
        rpin = load_plugin_info(fname)

        if not rpin:
            messages.error(
                request,
                _('Unable to load plugin in folder "{0}".').format(fname))
            continue

        # Log the event
        Log.objects.register(request.user,
                             Log.PLUGIN_CREATE,
                             workflow,
                             {'id': rpin.id, 'name': rpin.filename})


def run_plugin(workflow,
               plugin_info,
               input_column_names,
               output_column_names,
               output_suffix,
               merge_key,
               parameters):
    """

    Execute the run method in a plugin with the dataframe from the given
    workflow

    :param workflow: Workflow object being processed
    :param plugin_info: PluginReistry object being processed
    :param input_column_names: List of input column names
    :param output_column_names: List of output column names
    :param output_suffix: Suffix that is added to the output column names
    :param merge_key: Key column to use in the merge
    :param parameters: Dictionary with the parameters to execute the plug in
    :return: Nothing, the result is stored in the log with log_id
    """

    plugin_instance, msgs = load_plugin(plugin_info.filename)
    if plugin_instance is None:
        raise Exception(
            ugettext('Unable to instantiate plugin "{0}"').format(
                plugin_info.name
            )
        )

    # Check that the list of given inputs is consistent: if plugin has a list of
    # inputs, it has to have the same length as the given list.
    if plugin_instance.get_input_column_names() and \
            len(plugin_instance.get_input_column_names()) != \
            len(input_column_names):
        raise Exception(
            ugettext(
                'Inconsistent number of inputs when invoking plugin "{0}"'
            ).format(plugin_info.name)
        )

    # Check that the list of given outputs has the same length as the list of
    # outputs proposed by the plugin
    if plugin_instance.get_output_column_names() and \
            len(plugin_instance.get_output_column_names()) != \
            len(output_column_names):
        raise Exception(
            ugettext(
                'Inconsistent number of outputs when invoking plugin "{0}"'
            ).format(plugin_info.name)
        )

    # Get the data frame from the workflow
    try:
        df = pandas_db.load_from_db(workflow.get_data_frame_table_name())
    except Exception as e:
        raise Exception(
            ugettext(
                'Exception while retrieving the data frame from workflow: {0}'
            ).format(e)
        )

    # Set the updated names of the input, output columns, and the suffix
    if not plugin_instance.get_input_column_names():
        plugin_instance.input_column_names = input_column_names
    plugin_instance.output_column_names = output_column_names
    plugin_instance.output_suffix = output_suffix

    # Create a new dataframe with the given input columns, and rename them if
    # needed
    try:
        sub_df = pd.DataFrame(df[input_column_names])
        if plugin_instance.get_input_column_names():
            sub_df.columns = plugin_instance.get_input_column_names()
    except Exception as e:
        raise Exception(
            ugettext('Error while creating data frame for plugin: {0}').format(
                e
            )
        )

    # Try the execution and catch any exception
    try:
        new_df = plugin_instance.run(sub_df, parameters=parameters)
    except Exception as e:
        raise Exception(
            ugettext('Error while executing plugin: {0}').format(e)
        )

    # If plugin does not return a data frame, flag as error
    if not isinstance(new_df, pd.DataFrame):
        raise Exception(
            ugettext('Plugin executed but did not return a pandas data frame.')
        )

    # Execution is DONE. Now we have to perform various additional checks

    # Result has to have the exact same number of rows
    if new_df.shape[0] != df.shape[0]:
        raise Exception(
            ugettext(
                'Incorrect number of rows ({0}) in result data frame.'
            ).format(new_df.shape[0])
        )

    # Merge key name cannot be part of the output df
    if merge_key in new_df.columns:
        raise Exception(
            ugettext(
                'Column name {0} cannot be in the result data frame.'.format(
                    merge_key
                )
            )
        )

    # Result column names are consistent
    if set(new_df.columns) != set(plugin_instance.get_output_column_names()):
        raise Exception(
            ugettext('Incorrect columns in result data frame.')
        )

    # List of pairs (column name, column type) in the result to create the
    # log event
    # result_columns = list(zip(
    #     list(new_df.columns),
    #     pandas_db.df_column_types_rename(new_df)))

    # Add the merge column to the result df
    new_df[merge_key] = df[merge_key]

    # Proceed with the merge
    try:
        result = ops.perform_dataframe_upload_merge(
            workflow,
            df,
            new_df,
            {'how_merge': 'inner',
             'dst_selected_key': merge_key,
             'src_selected_key': merge_key,
             'initial_column_names': list(new_df.columns),
             'rename_column_names': list(new_df.columns),
             'columns_to_upload': [True] * len(list(new_df.columns))}
        )
    except Exception as e:
        raise Exception(
            ugettext('Error while merging result ({0}).').format(e)
        )

    if isinstance(result, str):
        raise Exception(
            ugettext('Error while merging result ({0}).').format(result)
        )

    # Update execution time in the plugin
    plugin_info.executed = datetime.now(
        pytz.timezone(ontask_settings.TIME_ZONE)
    )
    plugin_info.save()

    return True


