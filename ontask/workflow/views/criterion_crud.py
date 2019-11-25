# -*- coding: utf-8 -*-

"""Views for create/update columns that are criteria in a rubric."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ontask import OnTaskServiceException, models
from ontask.core import ajax_required, get_action, get_workflow, is_instructor
from ontask.workflow import services
from ontask.workflow.forms import CriterionForm


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def criterion_create(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Add a new criteria to an action.

    If it is the first criteria, the form simply asks for a question with a
    non-empty category field.

    If it is not the first criteria, then the criteria are fixed by the
    previous elements in the rubric.

    :param request: Http Request
    :param pk: Action ID where to add the question
    :param workflow: Workflow being used.
    :param action: Action in which the criteria (column) is being created)
    :return: JSON response
    """
    if action.action_type != models.Action.RUBRIC_TEXT:
        messages.error(
            request,
            _('Operation only valid or Rubric actions'),
        )
        return http.JsonResponse({'html_redirect': ''})

    if action.workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add criteria to a workflow without data'),
        )
        return http.JsonResponse({'html_redirect': ''})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    # Form to read/process data
    form = CriterionForm(
        request.POST or None,
        other_criterion=models.ActionColumnConditionTuple.objects.filter(
            action=action).first(),
        workflow=action.workflow)

    if request.method == 'POST' and form.is_valid():
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                request.user,
                workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_RUBRIC_CRITERION_ADD,
                action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
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
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Edit a criterion in a rubric.

    :param request:
    :param pk: For the Action/Column/condition triplet
    :param workflow: Workflow being used.
    :return: JSON Response
    """
    triplet = models.ActionColumnConditionTuple.objects.filter(pk=pk).first()
    if not triplet:
        messages.error(
            request,
            _('Incorrect invocation of criterion edit function'),
        )
        return http.JsonResponse({'html_redirect': ''})

    action = triplet.action
    column = triplet.column
    form = CriterionForm(
        request.POST or None,
        workflow=workflow,
        other_criterion=models.ActionColumnConditionTuple.objects.filter(
            action=action,
        ).exclude(column=column.id).first(),
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
            form.old_position,
            triplet,
            models.Log.ACTION_RUBRIC_CRITERION_EDIT)
        form.save_m2m()

        # Done processing the correct POST request
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
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
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """Remove the criterion from the rubric. Does not remove the column.

    :param request:

    :param pk: For the Action/Column/condition triplet

    :return: JSON Response
    """
    triplet = models.ActionColumnConditionTuple.objects.filter(pk=pk).first()
    if not triplet:
        messages.error(
            request,
            _('Incorrect invocation of criterion delete function'),
        )
        return http.JsonResponse({'html_redirect': ''})

    if request.method == 'POST':
        triplet.log(request.user, models.Log.ACTION_RUBRIC_CRITERION_DELETE)
        triplet.delete()
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
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
    request: http.HttpRequest,
    pk: int,
    cpk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Operation to add a criterion to a rubric.

    :param request: Request object
    :param pk: Action PK
    :param cpk: column PK.
    :param workflow: Workflow being manipulated
    :param action: Action object where the criterion is inserted
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
            _('Incorrect invocation of criterion insert operation.'),
        )
        return http.JsonResponse({'html_redirect': ''})

    if (
        criteria
        and set(column.categories) != set(criteria[0].column.categories)
    ):
        messages.error(
            request,
            _('Criterion does not have the correct levels of attainment'),
        )
        return http.JsonResponse({'html_redirect': ''})

    if not criteria and len(column.categories) == 0:
        messages.error(
            request,
            _('The column needs to have a fixed set of possible values'),
        )
        return http.JsonResponse({'html_redirect': ''})

    acc = models.ActionColumnConditionTuple.objects.create(
        action=action,
        column=column,
        condition=None)

    acc.log(request.user, models.Log.ACTION_RUBRIC_CRITERION_ADD)

    # Refresh the page to show the column in the list.
    return http.JsonResponse({'html_redirect': ''})
