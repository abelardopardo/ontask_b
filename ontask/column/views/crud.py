# -*- coding: utf-8 -*-

"""Views for create/rename/update/delete columns."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import OnTaskServiceException, models
from ontask.column import forms, services
from ontask.core import (
    ajax_required, get_action, get_column, get_workflow, is_instructor)
from ontask.dataops.formula import evaluation

# These are the column operands offered through the GUI. They have immediate
# translations onto Pandas operators over dataframes.
# Each tuple has:
# - Pandas operation name
# - Textual description
# - List of data types that are allowed (for data type checking)
_formula_column_operands = [
    ('sum', _('sum: Sum selected columns'), ['integer', 'double']),
    (
        'prod',
        _('prod: Product of the selected columns'),
        ['integer', 'double']),
    ('max', _('max: Maximum of the selected columns'), ['integer', 'double']),
    ('min', _('min: Minimum of the selected columns'), ['integer', 'double']),
    ('mean', _('mean: Mean of the selected columns'), ['integer', 'double']),
    (
        'median',
        _('median: Median of the selected columns'),
        ['integer', 'double']),
    (
        'std',
        _('std: Standard deviation over the selected columns'),
        ['integer', 'double']),
    (
        'all',
        _('all: True when all elements in selected columns are true'),
        ['boolean']),
    (
        'any',
        _('any: True when any element in selected columns is true'),
        ['boolean']),
]


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related=['actions', 'columns'])
def create(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Add a column.

    :param request: Http Request
    :param workflow: Workflow to add the column
    :return: JSON response
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add column to a workflow without data'),
        )
        return http.JsonResponse({'html_redirect': ''})

    form = forms.ColumnAddForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                request.user,
                workflow,
                column,
                form.initial_valid_value)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_addedit.html',
            {
                'form': form,
                'is_question': False,
                'add': True},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def question_add(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Add a column to a survey action

    :param request: Http Request
    :param pk: Action ID where to add the question
    :param workflow: Workflow being manipulated
    :param action: Action being manipulated
    :return: JSON response
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add question to a workflow without data'),
        )
        return http.JsonResponse({'html_redirect': ''})

    form = forms.QuestionForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                request.user,
                workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_QUESTION_ADD,
                action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_question_addedit.html',
            {
                'form': form,
                'action_id': action.id,
                'add': True},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def todoitem_add(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Add an item to the todo list

    :param request: Http Request
    :param pk: Action ID where to add the question
    :param workflow: Workflow being manipulated
    :return: JSON response
    """
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add todo items to a workflow without data'),
        )
        return http.JsonResponse({'html_redirect': ''})

    form = forms.TODOItemForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                request.user,
                workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_TODOITEM_ADD,
                action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_todoitem_addedit.html',
            {
                'form': form,
                'action_id': action.id,
                'add': True},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='columns')
def formula_column_add(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Add a formula column.

    :param request: http.HttpRequest
    :param workflow: Workflow being manipulated
    :return: http.JsonResponse
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add column to a workflow without data'))
        return http.JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = forms.FormulaColumnAddForm(
        form_data=request.POST or None,
        operands=_formula_column_operands,
        columns=workflow.columns.all(),
    )

    if request.method == 'POST' and form.is_valid():
        column = form.save(commit=False)
        try:
            services.add_formula_column(
                request.user,
                workflow,
                column,
                form.cleaned_data['op_type'],
                form.selected_columns)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_formula_add.html',
            {'form': form},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='columns')
def random_column_add(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Create a column with random values (Modal).

    :param request: Http request
    :param workflow: Workflow being manipulated
    :return: Json Response
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add column to a workflow without data'))
        return http.JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = forms.RandomColumnAddForm(
        data=request.POST or None,
        workflow=workflow,
        allow_interval_as_initial=True)

    if request.method == 'POST' and form.is_valid():
        column = form.save(commit=False)
        column.workflow = workflow
        column.is_key = False
        column.save()

        try:
            services.add_random_column(
                request.user,
                workflow,
                column,
                form.data_frame)
            form.save_m2m()
        except services.OnTaskColumnIntegerLowerThanOneError as exc:
            form.add_error(exc.field_name, str(exc))
            return http.JsonResponse({
                'html_form': render_to_string(
                    'column/includes/partial_random_add.html',
                    {'form': form},
                    request=request),
            })
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()
        except Exception as exc:
            messages.error(
                request,
                _('Unable to add random column: {0}').format(str(exc)))

        # The form has been successfully processed
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_random_add.html',
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related=['columns', 'views', 'actions'])
def column_edit(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.JsonResponse:
    """Edit a column.

    :param request: Http Request received
    :param pk: Column primary key for lookup
    :param workflow: Workflow being processed
    :param column: Column to edit (set by the decorator)
    :return:
    """
    # Detect if this operation is to edit a new column or a new question (in
    # the edit in page)
    is_question = 'question_edit' in request.path_info
    # Form to read/process data
    if is_question:
        form = forms.QuestionForm(
            request.POST or None,
            workflow=workflow,
            instance=column)
    else:
        form = forms.ColumnRenameForm(
            request.POST or None,
            workflow=workflow,
            instance=column)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        column = form.save(commit=False)
        services.update_column(
            request.user,
            workflow,
            column,
            form.old_name,
            form.old_position)
        form.save_m2m()

        # Done processing the correct POST request
        return http.JsonResponse({'html_redirect': ''})

    if is_question:
        template = 'column/includes/partial_question_addedit.html'
    else:
        template = 'column/includes/partial_addedit.html'
    return http.JsonResponse({
        'html_form': render_to_string(
            template,
            {'form': form,
             'cname': column.name,
             'pk': pk},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related=['columns', 'actions'])
def delete(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.JsonResponse:
    """Delete a column in the table attached to a workflow.

    :param request: HTTP request
    :param pk: ID of the column to delete.
    :param workflow: Workflow being processed
    :param column: Column to delete (set by the decorator)
    :return: Render the delete column form
    """
    # Get the workflow element
    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    unique_column = workflow.get_column_unique()
    if column.is_key and len([col for col in unique_column if col]) == 1:
        # This is the only key column
        messages.error(request, _('You cannot delete the only key column'))
        return http.JsonResponse({'html_redirect': reverse('column:index')})

    # Get the name of the column to delete
    context = {'pk': pk, 'cname': column.name}

    # Get the conditions/actions attached to this workflow
    cond_to_delete = [
        col for col in models.Condition.objects.filter(
            action__workflow=workflow)
        if evaluation.has_variable(col.formula, column.name)]
    # Put it in the context because it is shown to the user before confirming
    # the deletion
    context['cond_to_delete'] = cond_to_delete

    if request.method == 'POST':
        services.delete_column(request.user, workflow, column, cond_to_delete)

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            return http.JsonResponse({'html_redirect': reverse('table:display')})

        return http.JsonResponse({'html_redirect': reverse('column:index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'column/includes/partial_delete.html',
            context,
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def column_clone(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    column: Optional[models.Column] = None,
) -> http.JsonResponse:
    """Clone a column in the table attached to a workflow.

    :param request: HTTP request
    :param pk: ID of the column to clone.
    :param workflow: Workflow being processed
    :param column: Column to clone (set by the decorator)
    :return: Render the clone column form
    """
    del workflow
    # Get the name of the column to clone
    context = {'pk': pk, 'cname': column.name}

    if request.method == 'GET':
        return http.JsonResponse({
            'html_form': render_to_string(
                'column/includes/partial_clone.html',
                context,
                request=request),
        })

    # Proceed to clone the column
    try:
        services.clone_column(request.user, column)
    except Exception as exc:
        messages.error(
            request,
            _('Unable to clone column: {0}').format(str(exc)))
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({'html_redirect': ''})
