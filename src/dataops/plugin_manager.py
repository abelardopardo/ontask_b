# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

import pandas as pd
import time
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render

import dataops.ops
import dataops.pandas_db
import pandas_db
from logs import ops
from ontask.permissions import is_instructor
from workflow.ops import get_workflow
from . import plugin, settings
from .forms import SelectColumnForm
from .models import PluginRegistry


def get_plugin_path():
    plugin_folder = str(getattr(settings, 'PLUGIN_DIRECTORY'))

    if os.path.isabs(plugin_folder):
        return plugin_folder

    return os.path.join(django_settings.PROJECT_PATH,
                        plugin_folder)


def load_plugin(foldername):
    """
    Loads the plugin given in the filename
    :param foldername: folder where the plugin code is installed. Only the
                       folder name
    :return: An instance of the plugin or None
    """

    try:
        ctx_handler = __import__(foldername)
    except Exception:
        return None

    class_name = getattr(ctx_handler, 'class_name')
    if not class_name:
        class_name = getattr(ctx_handler, plugin.class_name)

    try:
        plugin_class = getattr(ctx_handler, class_name)
        # Get an instance of this class
        plugin_instance = plugin_class()
    except AttributeError:
        return None

    return plugin_instance


def load_plugin_info(plugin_folder, plugin_rego=None):
    """
    Load the plugin and transfer the information into the PluginRegistry
    table.
    :param plugin_folder: Folder to load the information from.
    :param plugin_rego: Plugin record in the table (none if it needs to
                        be created)
    :return: Record in the DB is updated and returned. None if error
    """

    # Load the given module
    plugin_instance = load_plugin(plugin_folder)
    if plugin_instance is None:
        return None

    # If there is no instance given of the registry, create a new one
    if not plugin_rego:
        plugin_rego = PluginRegistry()

    # Upload the fields.
    plugin_rego.filename = plugin_folder
    plugin_rego.name = plugin_instance.get_name()
    plugin_rego.description_txt = plugin_instance.get_description_txt()
    plugin_rego.num_column_input_from = \
        plugin_instance.get_num_column_input_from()
    plugin_rego.num_column_input_to = plugin_instance.get_num_column_input_to()
    plugin_rego.save()

    return plugin_rego


def refresh_plugin_data(request, workflow):
    """
    Function to traverse the directory where the plugins live and check if
    the folders in there are reflected in the PluginRegistry model.

    :return:
    """

    plugin_folder = get_plugin_path()

    pfolders = [f for f in os.listdir(plugin_folder)
                if os.path.isdir(os.path.join(plugin_folder, f))]

    reg_plugins = PluginRegistry.objects.all()
    for rpin in reg_plugins:
        if rpin.filename not in pfolders:
            # A plugin has vanised. Delete

            # Log the event
            ops.put(request.user,
                    'plugin_delete',
                    workflow,
                    {'id': rpin.id, 'name': rpin.filename})

            rpin.delete()
            continue

        if os.stat(os.path.join(plugin_folder, rpin.filename)).st_mtime > \
                time.mktime(rpin.modified.timetuple()):
            # A plugin has changed
            load_plugin_info(rpin.filename, rpin)

            # Log the event
            ops.put(request.user,
                    'plugin_update',
                    workflow,
                    {'id': rpin.id, 'name': rpin.filename})

        pfolders.remove(rpin.filename)

    # The remaining folders are new plugins
    for fname in pfolders:
        # Load the plugin info in a new record.
        rpin = load_plugin_info(fname)

        if not rpin:
            continue

        # Log the event
        ops.put(request.user, 'plugin_create', workflow,
                {'id': rpin.id, 'name': rpin.filename})


def run_plugin(plugin_info, param_df):
    """
    Execute the run method in a plugin with the given data frame
    :param plugin_info: Record with the plugin information
    :param param_df: data frame to be passed as parameter
    :return: (result, message) If messag is None, result is a valid data frame
    """

    # Load the plugin
    plugin_instance = load_plugin(plugin_info.filename)

    # Try the execution and catch any exception
    try:
        new_df = plugin_instance.run(param_df)
    except Exception, e:
        msg = e.message
        return None, msg

    # If plugin does not return a data frame, flag as error
    if not isinstance(new_df, pd.DataFrame):
        return None, 'Result is not a pandas data frame.'

    # Execution was correct. Proceed with some additional checks.
    return new_df, None


@user_passes_test(is_instructor)
def run(request, pk):
    """
    View provided as the first step to execute a plugin.
    :param request: HTTP request received
    :param pk: primary key of the plugin
    :return: Page offering to select the columns to invoke
    """

    # Get the workflow and the plugin information
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')
    try:
        plugin_info = PluginRegistry.objects.get(pk=pk)
    except PluginRegistry.DoesNotExist:
        return redirect('workflow:index')

    context = {
        'plugin_name': plugin_info.name,
        'min_col_num': plugin_info.num_column_input_from
    }

    # If there are not enough columns, render the page
    if workflow.ncols < plugin_info.num_column_input_from:
        return render(request, 'dataops/plugin_select_columns.html', context)

    # create the form to select the columns to process and insert it in the
    # context
    columns = workflow.get_columns()
    form = SelectColumnForm(request.POST or None,
                            columns=[c.is_key for c in columns])
    context['form'] = form

    # Prepare info to render the form. (name, unique, type, checked)
    checked = [request.POST.get('upload_%s' % i, '') == 'on'
               for i in range(len(columns))]

    form_info = zip(columns, checked)
    context['form_info'] = form_info

    if request.method == 'POST':
        if not form.is_valid():
            return render(request,
                          'dataops/plugin_select_columns.html',
                          context)

        # Check that the number of selected columns is within the limits
        # provided by the plugin
        col_selected = [form.cleaned_data['upload_%s' % i]
                        for i in range(len(columns))]
        ncol_selected = len([x for x in col_selected if x])

        # Number of columns in the proper limit
        if (plugin_info.num_column_input_from > 0 and
            ncol_selected < plugin_info.num_column_input_from) or \
                (0 < plugin_info.num_column_input_to < ncol_selected):
            form.add_error(None,
                           'The plugin needs between ' +
                           str(plugin_info.num_column_input_from) +
                           ' and ' + str(plugin_info.num_column_input_to) +
                           ' columns selected to execute.')
            return render(request,
                          'dataops/plugin_select_columns.html',
                          context)

        # POST is correct proceed with execution

        # Get the data frame and select the appropriate columns
        dst_df = None
        try:
            dst_df = dataops.pandas_db.load_from_db(workflow.id)
        except Exception:
            messages.error(request, 'Exception while retrieving the data frame')
            return render(request, 'error.html', {})

        selected_column_names = [c.name for x, c in enumerate(columns)
                                 if checked[x]]
        param_df = dst_df[selected_column_names]

        # Execute the plugin
        result_df, status = run_plugin(plugin_info, param_df)

        if status is not None:
            context['exec_status'] = status

            # Log the event
            ops.put(request.user,
                    'plugin_execute',
                    workflow,
                    {'id': plugin_info.id,
                     'name': plugin_info.name,
                     'status': status})

            return render(request,
                          'dataops/plugin_execution_report.html',
                          context)

        # Additional checks
        # Result has the same number of rows
        if result_df.shape[0] != dst_df.shape[0]:
            status = 'Incorrect number of rows in result data frame.'
            context['exec_status'] = status

            # Log the event
            ops.put(request.user,
                    'plugin_execute',
                    workflow,
                    {'id': plugin_info.id,
                     'name': plugin_info.name,
                     'status': status})

            return render(request,
                          'dataops/plugin_execution_report.html',
                          context)

        # Rename columns if needed
        dst_columns = list(dst_df)
        result_columns = list(result_df.columns)
        rename_dict = {}
        for idx, cname in enumerate(result_columns):
            if cname in dst_columns:
                i = 0
                while True:
                    i += 1
                    new_name = cname + '_{0}'.format(i)
                    if new_name not in dst_columns and \
                            new_name not in result_columns:
                        break
                rename_dict[cname] = new_name
        result_df.rename(columns=rename_dict, inplace=True)

        # Proceed with the append
        dst_df = pd.concat([dst_df, result_df], axis=1)

        # Dump in DB
        dataops.ops.store_dataframe_in_db(dst_df, workflow.id)

        result_columns = zip(
            list(result_df.columns),
            pandas_db.df_column_types_rename(result_df))
        context['result_columns'] = result_columns

        # Log the event
        ops.put(request.user,
                'plugin_execute',
                workflow,
                {'id': plugin_info.id,
                 'name': plugin_info.name,
                 'status': status,
                 'result_columns': result_columns})
        # Redirect to the notification page with the proper info
        return render(request, 'dataops/plugin_execution_report.html', context)

    return render(request, 'dataops/plugin_select_columns.html', context)
