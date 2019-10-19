# -*- coding: utf-8 -*-

"""Views for create/update columns that are criteria in a rubric."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask.core.decorators import ajax_required, get_action, get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.pandas import rename_df_column
from ontask.dataops.sql import add_column_to_db, db_rename_column
from ontask.models import Action, ActionColumnConditionTuple, Log, Workflow
from ontask.workflow.forms import CriterionForm


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def criterion_create(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Workflow] = None,
) -> JsonResponse:
    """Add a new criteria to an action.

    If it is the first criteria, the form simply asks for a question with a
    non-empty category field.

    If it is not the first criteria, then the criteria are fixed by the
    previous elements in the rubric.

    :param request: Http Request

    :param pk: Action ID where to add the question

    :return: JSON response
    """
    if action.action_type != Action.RUBRIC_TEXT:
        messages.error(
            request,
            _('Operation only valid or Rubric actions')
        )
        return JsonResponse({'html_redirect': ''})

    if action.workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add criteria to a workflow without data'),
        )
        return JsonResponse({'html_redirect': ''})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    # Form to read/process data
    form = CriterionForm(
        request.POST or None,
        other_criterion=ActionColumnConditionTuple.objects.filter(
            action=action).first(),
        workflow=action.workflow)

    if request.method == 'POST' and form.is_valid():
        # Processing now a valid POST request
        # Access the updated information
        column_initial_value = form.initial_valid_value

        # Save the column object attached to the form
        column = form.save(commit=False)

        # Catch the special case of integer type and no initial value. Pandas
        # encodes it as NaN but a cycle through the database transforms it into
        # a string. To avoid this case, integer + empty value => double
        if column.data_type == 'integer' and column_initial_value is None:
            column.data_type = 'double'

        # Fill in the remaining fields in the column
        column.workflow = workflow
        column.is_key = False

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)

        # Save column, refresh workflow, and increase number of columns
        column.save()
        form.save_m2m()
        workflow.refresh_from_db()
        workflow.ncols += 1
        workflow.set_query_builder_ops()
        workflow.save()

        # Add the new column to the DB
        try:
            add_column_to_db(
                workflow.get_data_frame_table_name(),
                column.name,
                column.data_type,
                initial=column_initial_value)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to add criterion: {0}').format(str(exc)))
            return JsonResponse({'html_redirect': ''})

        # Add the criterion to the action
        acc = ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=column,
            condition=None)

        # Log the event
        acc.log(request.user, Log.ACTION_RUBRIC_CRITERION_ADD)

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_criterion_addedit.html',
            {
                'form': form,
                'action_id': action.id,
                'add': True},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related=['columns'])
def criterion_edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Edit a criterion in a rubric.

    :param request:

    :param pk: For the Action/Column/condition triplet

    :return: JSON Response
    """
    triplet = ActionColumnConditionTuple.objects.filter(pk=pk).first()
    if not triplet:
        messages.error(
            request,
            _('Incorrect invocation of criterion edit function')
        )
        return JsonResponse({'html_redirect': ''})

    action = triplet.action
    column = triplet.column
    form = CriterionForm(
        request.POST or None,
        workflow=workflow,
        other_criterion=ActionColumnConditionTuple.objects.filter(
            action=action
        ).exclude(column=column.id).first(),
        instance=column)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        # Some field changed value, so save the result, but
        # no commit as we need to propagate the info to the df
        column = form.save(commit=False)

        # If there is a new name, rename the data frame columns
        if form.old_name != form.cleaned_data['name']:
            db_rename_column(
                workflow.get_data_frame_table_name(),
                form.old_name,
                column.name)
            rename_df_column(workflow, form.old_name, column.name)

        if form.old_position != form.cleaned_data['position']:
            # Update the positions of the appropriate columns
            workflow.reposition_columns(form.old_position, column.position)

        # Save the column information
        column.save()

        # Go back to the DB because the prefetch columns are not valid
        # any more
        workflow = Workflow.objects.prefetch_related('columns').get(
            id=workflow.id,
        )

        # Changes in column require rebuilding the query_builder_ops
        workflow.set_query_builder_ops()

        # Save the workflow
        workflow.save()

        # Log the event
        triplet.log(request.user, Log.ACTION_RUBRIC_CRITERION_EDIT)

        # Done processing the correct POST request
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_criterion_addedit.html',
            {'form': form,
             'cname': column.name,
             'pk': pk},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related=['columns'])
def criterion_remove(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Remove the criterion from the rubric. Does not remove the column.

    :param request:

    :param pk: For the Action/Column/condition triplet

    :return: JSON Response
    """
    triplet = ActionColumnConditionTuple.objects.filter(pk=pk).first()
    if not triplet:
        messages.error(
            request,
            _('Incorrect invocation of criterion delete function')
        )
        return JsonResponse({'html_redirect': ''})

    if request.method == 'POST':
        triplet.log(request.user, Log.ACTION_RUBRIC_CRITERION_DELETE)
        triplet.delete()
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_criterion_remove.html',
            {'pk': pk, 'cname': triplet.column.name},
            request=request)})

@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@require_http_methods(['POST'])
@get_action(pf_related=['columns', 'actions'])
def criterion_insert(
    request: HttpRequest,
    pk: int,
    cpk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Operation to add a criterion to a rubric.

    :param request: Request object

    :param pk: Action PK

    :param cpk: column PK.

    :param key: The columns is a key column

    :return: JSON response
    """
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    criteria = action.column_condition_pair.filter(action_id=pk)
    column = workflow.columns.filter(pk=cpk).first()
    if not column or criteria.filter(column=column).exists():
        messages.error(
            request,
            _('Incorrect invocation of criterion insert operation.')
        )
        return JsonResponse({'html_redirect': ''})

    if criteria and set(column.categories) != set(
        criteria[0].column.categories):
        messages.error(
            request,
            _('Criterion does not have the correct levels of attainment')
        )
        return JsonResponse({'html_redirect': ''})

    if not criteria and len(column.categories) == 0:
        messages.error(
            request,
            _('The column needs to have a fixed set of possible values')
        )
        return JsonResponse({'html_redirect': ''})

    acc = ActionColumnConditionTuple.objects.create(
        action=action,
        column=column,
        condition=None)

    acc.log(request.user, Log.ACTION_RUBRIC_CRITERION_ADD)

    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})
