# -*- coding: utf-8 -*-

"""Service functions to handle plugin invocations."""

from datetime import datetime
import inspect
import os
import time
from typing import List, Tuple

from django.conf import settings
from django.contrib import messages
from django.db.models.expressions import F
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.translation import ugettext, ugettext_lazy as _
import django_tables2 as tables
import pandas as pd
import pytz

from ontask import models, OnTaskServiceException
from ontask.dataops.pandas import load_table, perform_dataframe_upload_merge
from ontask.dataops.plugin import ontask_plugin
from ontask.dataops.plugin.ontask_plugin import OnTaskPluginAbstract
from ontask.dataops.services.errors import OnTasDataopsPluginInstantiationError
import ontask.settings


class PluginAdminTable(tables.Table):
    """Class to render the table with plugins present in the system."""

    description_text = tables.TemplateColumn(
        verbose_name=_('Description'),
        template_name='dataops/includes/partial_plugin_description.html',
    )

    last_exec = tables.DateTimeColumn(verbose_name=_('Last executed'))

    filename = tables.Column(verbose_name=_('Folder'), empty_values=None)

    num_executions = tables.Column(
        verbose_name=_('Executions'),
        empty_values=[])

    def render_is_verified(self, record):
        """Render is_verified as a tick or the button Diagnose."""
        if record.is_verified:
            return format_html('<span class="true">✔</span>')

        return render_to_string(
            'dataops/includes/partial_plugin_diagnose.html',
            context={'id': record.id},
            request=None)

    def render_is_enabled(self, record):
        """Render the is enabled as a checkbox."""
        return render_to_string(
            'dataops/includes/partial_plugin_enable.html',
            context={'record': record},
            request=None)

    def render_last_exec(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        log_item = models.Log.objects.filter(
            name=models.Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).order_by(F('created').desc()).first()
        if not log_item:
            return '—'
        return log_item.created

    def render_num_executions(self, record):
        """Render the last executed time.

        :param record: Record being processed in the table.

        :return:
        """
        return models.Log.objects.filter(
            name=models.Log.PLUGIN_EXECUTE,
            payload__name=record.name,
        ).count()

    class Meta(object):
        """Choose fields, sequence and attributes."""

        model = models.Plugin

        fields = (
            'filename',
            'name',
            'description_text',
            'is_model',
            'is_verified',
            'is_enabled')

        sequence = (
            'filename',
            'name',
            'description_text',
            'is_model',
            'is_verified',
            'is_enabled',
            'num_executions',
            'last_exec')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'plugin-admin-table',
            'th': {'class': 'dt-body-center'},
            'td': {'style': 'vertical-align: middle'}}


type_function = {
    'integer': int,
    'double': float,
    'string': str,
    'datetime': parse_datetime,
    'boolean': bool,
}
_checks = [
    _('Class inherits from OnTaskTransformation or OnTaskModel'),
    _('Class has a non-empty documentation string'),
    _('Class has a non-empty string field with name "name"'),
    _('Class has a string field with name "description_text"'),
    _(
        'Class has a field with name "input_column_names" storing '
        + 'a (possible empty) list of strings'),
    _(
        'Class has a field with name "output_column_names" storing '
        + 'a (possibly empty) list of strings'),
    _(
        'Class has a (possible empty) list of tuples with name '
        + '"parameters". The tuples must have six '
        + 'elements: name (a string), type (one of "double", "integer", '
        + '"string", "boolean", '
        + 'or "datetime"), (possible empty) list of allowed values of '
        + 'corresponding type, an initial value of the right type or '
        + 'None, and a help string to be shown when requesting this '
        + 'parameter.'),
    _(
        'Class has a method with name run receiving a data frame '
        + 'and a dictionary with parameters.'),
]


def _get_plugin_path():
    plugin_folder = str(getattr(ontask.settings, 'PLUGIN_DIRECTORY'))

    if os.path.isabs(plugin_folder):
        return plugin_folder

    return os.path.join(settings.BASE_DIR, plugin_folder)


def _verify_plugin(pinobj: models.Plugin) -> List[Tuple[str, str]]:
    """Verify that plugin complies with certain tests.

    Run some tests in the plugin instance to make sure it complies with the
    requirements. There is probably a much better way to do this, but it'll
    have to do it by now. The tests are:

    1. Class inherits from OnTaskPluginAbstract

    2. Class has a non empty __doc__

    3. Presence of string field "name"

    4. Presence of string field "description_text

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

    8. Class has a method with name run that receives a data frame and a
       dictionary.

    :param pinobj: Plugin instance

    :return: List of Booleans with the result of the tests
    """
    diag = ['Unchecked'] * len(_checks)
    check_idx = 0
    try:
        # Verify that the class inherits from OnTaskPluginAbstract
        if issubclass(type(pinobj), OnTaskPluginAbstract):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect parent class')
            return list(zip(diag, _checks))
        check_idx += 1

        # Verify that the class has a non empty documentation string
        if pinobj.__doc__ and isinstance(pinobj.__doc__, str):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Class is not documented')
        check_idx += 1

        # Verify that all the fields and methods are present in the instance
        diag[check_idx] = _('Not found')
        if pinobj.name and isinstance(pinobj.name, str):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect type')
        check_idx += 1

        diag[check_idx] = _('Not found')
        if pinobj.description_text and isinstance(pinobj.description_text, str):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect type')
        check_idx += 1

        diag[check_idx] = _('Not found')
        if pinobj.input_column_names is not None and isinstance(
            pinobj.input_column_names, list
        ) and all(
            isinstance(colname, str)
            for colname in pinobj.input_column_names
        ):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect type')
        check_idx += 1

        diag[check_idx] = _('Not found')
        if pinobj.output_column_names is not None and isinstance(
            pinobj.output_column_names, list
        ) and all(
            isinstance(cname, str)
            for cname in pinobj.output_column_names
        ):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect type/value')
        check_idx += 1

        diag[check_idx] = _('Not found')
        if pinobj.parameters is None or not isinstance(pinobj.parameters, list):
            diag[check_idx] = _('Incorrect type')
            return list(zip(diag, _checks))

        # Loop over all the parameters to check it s format
        for key, ptype, pallow, pinit, phelp in pinobj.parameters:
            if not isinstance(key, str):
                # The type should be a string
                diag[check_idx] = _('Key values should be strings')
                return list(zip(diag, _checks))

            if not isinstance(ptype, str):
                # The type should be a string
                diag[check_idx] = _(
                    'First tuple element should be as string')
                return list(zip(diag, _checks))

            t_func = type_function.get(ptype)
            if not t_func:
                # This is an incorrect data type
                diag[check_idx] = _(
                    'Incorrect type "{0}" in parameter').format(ptype)
                return list(zip(diag, _checks))

            # If the column is of type datetime, the list of allowed values
            # should be empty
            if ptype == 'datetime' and pallow:
                diag[check_idx] = _(
                    'Parameter of type datetime cannot have '
                    + 'list of allowed values')
                return list(zip(diag, _checks))

            # Translate all values to the right type
            diag[check_idx] = _('Incorrect list of allowed value')
            list(map(t_func, pallow))

            # And translate the initial value to the right type
            diag[check_idx] = _('Incorrect initial value')
            if pinit:
                if t_func(pinit) is None:
                    return list(zip(diag, _checks))

            if phelp and not isinstance(phelp, str):
                diag[check_idx] = _('Help text must be as string')
                # Help text must be a string
                return list(zip(diag, _checks))

        diag[check_idx] = 'Ok'
        check_idx += 1

        # Test the method run
        run_method = getattr(pinobj, 'run', None)
        if callable(run_method) and (
            inspect.signature(OnTaskPluginAbstract.run)
            == inspect.signature(pinobj.__class__.run)
        ):
            diag[check_idx] = _('Ok')
        else:
            diag[check_idx] = _('Incorrect run method')
        check_idx += 1

    except Exception:
        return list(zip(diag, _checks))

    return list(zip(diag, _checks))


def _load_plugin_info(plugin_folder, plugin_rego=None):
    """Load the plugin and populate the Plugin table.

    :param plugin_folder: Folder to load the information from.

    :param plugin_rego: Plugin record in the table (none if it needs to
                        be created)

    :return: Record in the DB is updated and returned.
    """
    # Load the given module
    plugin_instance, _ = load_plugin(plugin_folder)

    # If there is no instance given of the registry, create a new one
    if not plugin_rego:
        plugin_rego = models.Plugin()
        plugin_rego.filename = plugin_folder

    if plugin_instance:
        plugin_rego.name = plugin_instance.name
        plugin_rego.description_text = plugin_instance.description_text
        try:
            plugin_rego.is_model = plugin_instance.get_is_model()
        except Exception:
            plugin_rego.is_model = False

    plugin_rego.is_verified = plugin_instance is not None
    if not plugin_rego.is_verified:
        plugin_rego.is_enabled = False

    # All went good
    plugin_rego.save()

    return plugin_rego


def load_plugin(foldername):
    """Load the plugin given in the filename.

    :param foldername: folder where the plugin code is installed. Only the
                       folder name

    :return: A pair (instance of the plugin or None,
                     List of [diagnostic msg, test description])
    """
    try:
        ctx_handler = __import__(foldername)  # noqa Z421

        class_name = getattr(ctx_handler, 'class_name')
        if not class_name:
            class_name = getattr(ctx_handler, ontask_plugin.class_name)
        plugin_class = getattr(ctx_handler, class_name)
        # Get an instance of this class
        plugin_instance = plugin_class()

        # Run some additional checks in the instance and if it does not
        # comply with them, bail out.
        tests = _verify_plugin(plugin_instance)
        if not all(test_result == 'Ok' for test_result, __ in tests):
            return None, tests
    except AttributeError as exc:
        raise OnTasDataopsPluginInstantiationError(
            message=_('Error while instantiating the plugin class'))
    except Exception as exc:
        raise OnTasDataopsPluginInstantiationError(
            message=_('Error while instantiating the plugin class'))

    return plugin_instance, tests


def refresh_plugin_data(request, workflow = None):
    """Refresh the plugin data in the system.

    Function to traverse the directory where the plugins live and check if
    the folders in there are reflected in the Plugin model.

    :return: Reflect the changes in the database
    """
    plugin_folder = _get_plugin_path()

    pfolders = [
        folder for folder in os.listdir(plugin_folder)
        if os.path.isdir(os.path.join(plugin_folder, folder))
    ]

    # Get the objects from the DB
    reg_plugins = models.Plugin.objects.all()

    # Traverse the list of registered plugins and detect changes
    for rpin in reg_plugins:
        i_file = os.path.join(plugin_folder, rpin.filename, '__init__.py')
        if rpin.filename not in pfolders or not os.path.exists(i_file):
            # A plugin has vanished. Delete
            rpin.log(request.user, models.Log.PLUGIN_DELETE)
            rpin.delete()
            continue

        if os.stat(i_file).st_mtime > time.mktime(rpin.modified.timetuple()):
            # A plugin has changed
            _load_plugin_info(rpin.filename, rpin)
            rpin.log(request.user, models.Log.PLUGIN_UPDATE)

        pfolders.remove(rpin.filename)

    # The remaining folders are new plugins
    for fname in pfolders:
        if not os.path.exists(os.path.join(
            plugin_folder,
            fname,
            '__init__.py'),
        ):
            # Skip folders that do not have a __init__.py file
            continue

        # Load the plugin info in a new record.
        rpin = _load_plugin_info(fname)
        if not rpin:
            messages.error(
                request,
                _('Unable to load plugin in folder "{0}".').format(fname))
            continue
        rpin.log(request.user, models.Log.PLUGIN_CREATE)


def run_plugin(
    workflow,
    plugin_info,
    input_column_names,
    output_column_names,
    output_suffix,
    merge_key,
    plugin_params,
):
    """
    Execute the run method in the plugin.

    Execute the run method in a plugin with the dataframe from the given
    workflow

    :param workflow: Workflow object being processed
    :param plugin_info: PluginReistry object being processed
    :param input_column_names: List of input column names
    :param output_column_names: List of output column names
    :param output_suffix: Suffix that is added to the output column names
    :param merge_key: Key column to use in the merge
    :param plugin_params: Dictionary with the parameters to execute the plug in
    :return: Nothing, the result is stored in the log with log_id
    """
    try:
        plugin_instance, msgs = load_plugin(plugin_info.filename)
    except OnTaskServiceException as exc:
        raise Exception(
            ugettext('Unable to instantiate plugin "{0}"').format(
                plugin_info.name),
        )

    # Check that the list of given inputs is consistent: if plugin has a list
    # of inputs, it has to have the same length as the given list.
    if (
        plugin_instance.get_input_column_names()
        and len(plugin_instance.get_input_column_names())
        != len(input_column_names)
    ):
        raise Exception(
            ugettext(
                'Inconsistent number of inputs when invoking plugin "{0}"',
            ).format(plugin_info.name),
        )

    # Check that the list of given outputs has the same length as the list of
    # outputs proposed by the plugin
    if (
        plugin_instance.get_output_column_names()
        and len(plugin_instance.get_output_column_names())
        != len(output_column_names)
    ):
        raise Exception(
            ugettext(
                'Inconsistent number of outputs when invoking plugin "{0}"',
            ).format(plugin_info.name),
        )

    # Get the data frame from the workflow
    try:
        df = load_table(workflow.get_data_frame_table_name())
    except Exception as exc:
        raise Exception(
            ugettext(
                'Exception when retrieving the data frame from workflow: {0}',
            ).format(str(exc)),
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
    except Exception as exc:
        raise Exception(ugettext(
                'Error when creating data frame for plugin: {0}'
        ).format(str(exc)))

    # Try the execution and catch any exception
    try:
        new_df = plugin_instance.run(sub_df, parameters=plugin_params)
    except Exception as exc:
        raise Exception(
            ugettext('Error while executing plugin: {0}').format(str(exc)),
        )

    # If plugin does not return a data frame, flag as error
    if not isinstance(new_df, pd.DataFrame):
        raise Exception(
            ugettext(
                'Plugin executed but did not return a pandas data frame.'),
        )

    # Execution is DONE. Now we have to perform various additional checks

    # Result has to have the exact same number of rows
    if new_df.shape[0] != df.shape[0]:
        raise Exception(
            ugettext(
                'Incorrect number of rows ({0}) in result data frame.',
            ).format(new_df.shape[0]),
        )

    # Merge key name cannot be part of the output df
    if merge_key in new_df.columns:
        raise Exception(
            ugettext(
                'Column name {0} cannot be in the result data frame.'.format(
                    merge_key)),
        )

    # Result column names are consistent
    if set(new_df.columns) != set(plugin_instance.get_output_column_names()):
        raise Exception(ugettext('Incorrect columns in result data frame.'))

    # Add the merge column to the result df
    new_df[merge_key] = df[merge_key]

    # Proceed with the merge
    try:
        new_frame = perform_dataframe_upload_merge(
            workflow,
            df,
            new_df,
            {
                'how_merge': 'inner',
                'dst_selected_key': merge_key,
                'src_selected_key': merge_key,
                'initial_column_names': list(new_df.columns),
                'rename_column_names': list(new_df.columns),
                'columns_to_upload': [True] * len(list(new_df.columns)),
            },
        )
    except Exception as exc:
        raise Exception(
            ugettext('Error while merging result: {0}.').format(str(exc)),
        )

    if isinstance(new_frame, str):
        raise Exception(
            ugettext('Error while merging result: {0}.').format(new_frame))

    # Update execution time in the plugin
    plugin_info.executed = datetime.now(
        pytz.timezone(settings.TIME_ZONE),
    )
    plugin_info.save()

    return True
