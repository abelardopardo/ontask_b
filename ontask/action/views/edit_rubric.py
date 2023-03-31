# -*- coding: utf-8 -*-

"""View to edit rubric actions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.action import forms
from ontask.core import ajax_required, get_action, is_instructor


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def edit_rubric_cell(
    request: http.HttpRequest,
    pk: int,
    cid: int,
    loa_pos: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Edit a cell in a rubric.

    :param request:
    :param pk: Action ID
    :param cid: Column id
    :param loa_pos: Level of attainment position in the column categories
    :param workflow: Workflow being manipulated (set by the decorator)
    :param action: Action being edited (set by the decorators)
    :return: JSON Response
    """
    del workflow
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    form = forms.RubricCellForm(
        request.POST or None,
        instance=action.rubric_cells.filter(
            column=cid,
            loa_position=loa_pos).first())

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        cell = form.save(commit=False)
        if cell.id is None:
            # New cell in the rubric
            cell.action = action
            cell.column = action.workflow.columns.get(pk=cid)
            cell.loa_position = loa_pos
        cell.save()
        cell.log(request.user, models.Log.ACTION_RUBRIC_CELL_EDIT)
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_rubriccell_edit.html',
            {'form': form,
             'pk': pk,
             'cid': cid,
             'loa_pos': loa_pos},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
@get_action(pf_related=['columns'])
def edit_rubric_loas(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Edit a cell in a rubric.

    :param request:
    :param pk: Action ID
    :param workflow: Workflow being manipulated (set by the decorators)
    :param action: Action being edited (set by the decorators)
    :return: JSON Response
    """
    del workflow
    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    form = forms.RubricLOAForm(
        request.POST or None,
        criteria=[acc.column for acc in action.column_condition_pair.all()])

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        loas = [
            loa.strip()
            for loa in form.cleaned_data['levels_of_attainment'].split(',')]

        # Update all columns
        try:
            with transaction.atomic():
                for acc in action.column_condition_pair.all():
                    acc.column.set_categories(loas, validate=True)
        except Exception as exc:
            messages.error(
                request,
                _('Incorrect level of attainment values ({0}).').format(
                    str(exc)))

        # Log the event
        action.log(
            request.user,
            models.Log.ACTION_RUBRIC_LOA_EDIT,
            new_loas=loas)

        # Done processing the correct POST request
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_rubric_loas_edit.html',
            {'form': form, 'pk': pk},
            request=request)})
