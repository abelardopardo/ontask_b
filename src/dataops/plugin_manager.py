# -*- coding: utf-8 -*-


from builtins import zip
from builtins import map
import os
import time

import pandas as pd
from builtins import str
from django.conf import settings as django_settings
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _

from logs.models import Log
from . import plugin, settings
from .models import PluginRegistry


def get_plugin_path():
    plugin_folder = str(getattr(settings, 'PLUGIN_DIRECTORY'))

    if os.path.isabs(plugin_folder):
        return plugin_folder

    return os.path.join(django_settings.PROJECT_PATH, plugin_folder)


def verify_plugin_elements(plugin_instance):
    """
    Verify all elements in the plugin and return a list of messages with the
    result of the tests.
    :param plugin_instance: Instance of the plugin to verify
    :return: List of messages with the results of these tests.
    """
    result = ['Unchecked'] * 5
    check_idx = 0
    try:
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
        if not (plugin_instance.output_column_names and
                isinstance(plugin_instance.output_column_names, list) and
                len(plugin_instance.output_column_names) > 0 and
                all(isinstance(s, str) for s in
                    plugin_instance.output_column_names)):
            result[check_idx] = _('Incorrect type/value')
        else:
            result[check_idx] = _('Ok')
        check_idx += 1

        result[check_idx] = _('Not found')
        if not isinstance(plugin_instance.parameters, list):
            result[check_idx] = _('Incorrect type')
            return result

        for (k, p_type, p_allowed, p_initial, p_help) in \
                plugin_instance.parameters:

            if not isinstance(k, str):
                # The type should be a string
                result[check_idx] = _('Key values should be strings')
                return result

            if not isinstance(p_type, str):
                # The type should be a string
                result[check_idx] = \
                    _('First tuple element should be as string')
                return result

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
                return result

            # If the column is of type datetime, the list of allowed values
            # should be empty
            if p_type == 'datetime' and p_allowed:
                result[check_idx] = \
                    _('Parameter of type datetime cannot have '
                      'list of allowed values')
                return result

            # Translate all values to the right type
            result[check_idx] = _('Incorrect list of allowed value')
            __ = list(map(t_func, p_allowed))

            # And translate the initial value to the right type
            result[check_idx] = _('Incorrect initial value')
            if p_initial:
                item = t_func(p_initial)
                if item is None:
                    return result

            if p_help and not isinstance(p_help, str):
                result[check_idx] = _('Help text must be as string')
                # Help text must be a string
                return result

        result[check_idx] = 'Ok'
        check_idx += 1

        # Test
        if not (hasattr(plugin_instance, 'run') and
                callable(getattr(plugin_instance, 'run'))):
            # Run is either not in the class, or not a method.
            result[check_idx] = _('Incorrect run method')
            return result
        result[check_idx] = _('Ok')
    except Exception:
        return result

    # If all steps are clear, the plugin is good to go
    return result


def verify_plugin(plugin_instance):
    """
    Run some tests in the plugin instance to make sure it complies with the
    requirements. There is probably a much better way to do this, but it'll
    have to do it by now. The tests are:

    1. Presence of string field "name"

    2. Presence of string field "description_txt

    3. Presence of a list of strings (possibly empty) with name
       "input_column_names"

    4. Presence of a non-empty list of strings with name "output_column_names"

    5. Presence of a dictionary with name "parametes" that contains the
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
        _('Presence of a string field with name "name"'),
        _('Presence of a string field with name "description_txt"'),
        _('Presence of a field with name "input_column_names" storing a ('
          'possible empty) list of strings'),
        _('Presence of a field with name "output_column_names" storing a '
          'non-empty list of strings'),
        _('Presence of a (possible empty) list of tuples with name '
          '"parameters". The tuples must have six '
          'elements: name (a string), type (one of "double", "integer", '
          '"string", "boolean", '
          'or "datetime"), (possible empty) list of allowed values of the '
          'corresponding type, an initial value of the right type or None, '
          'and a help string to be shown when requesting this parameter.')
    ]

    return list(zip(verify_plugin_elements(plugin_instance), checks))


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
        if not all(x == 'Ok' for x, _ in tests):
            return (None, tests)
    except AttributeError as e:
        return (None, [(e, _('Class instantiation'))])
    except Exception as e:
        return (None, [(e, _('Instance creation'))])

    return (plugin_instance, tests)


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
            pinstance = load_plugin_info(rpin.filename, rpin)

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


def run_plugin(plugin_instance, df, merge_key, params):
    """
    Execute the run method in a plugin with the given data frame
    :param plugin_instance: Plugin instance
    :param df: data frame to be passed as parameter
    :param params: Parameter dictionary: (name, value)
    :return: (result, message) If message is None, result is a valid data frame
    """

    # Try the execution and catch any exception
    try:
        new_df = plugin_instance.run(df, merge_key, parameters=params)
    except Exception as e:
        return None, str(e)

    # If plugin does not return a data frame, flag as error
    if not isinstance(new_df, pd.DataFrame):
        return None, _('Result is not a pandas data frame.')

    # Execution was correct
    return new_df, None
