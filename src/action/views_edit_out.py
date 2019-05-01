# -*- coding: utf-8 -*-

"""Views to edit actions."""

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from action.evaluate_template import render_template
from action.form_edit import EditActionOutForm
from action.forms import ActionDescriptionForm, FilterForm
from action.models import Action, Condition
from action.views_edit_in import edit_action_in
from logs.models import Log
from ontask.permissions import is_instructor
from visualizations.plotly import PlotlyHandler
from workflow.models import Workflow
from workflow.ops import get_workflow


@user_passes_test(is_instructor)
def edit_description(request: HttpRequest, pk: int) -> JsonResponse:
    """Edit the description attached to an action.

    :param request: AJAX request
    :param pk: Action ID
    :return: AJAX response
    """
    # Try to get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('home')})

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('action:index')})

    # Initial result. In principle, re-render page
    resp_data = {'form_is_valid': False}

    # Create the form
    form = ActionDescriptionForm(
        request.POST or None,
        instance=action)

    if request.method == 'GET' or not form.is_valid():
        resp_data['html_form'] = render_to_string(
            'action/includes/partial_action_edit_description.html',
            {'form': form, 'action': action},
            request=request)

        return JsonResponse(resp_data)

    # Process the POST
    # Save item in the DB
    action.save()

    # Log the event
    Log.objects.register(
        request.user,
        Log.ACTION_UPDATE,
        action.workflow,
        {'id': action.id,
         'name': action.name,
         'workflow_id': workflow.id,
         'workflow_name': workflow.name})

    # Request is correct
    resp_data['form_is_valid'] = True
    resp_data['html_redirect'] = ''

    # Enough said. Respond.
    return JsonResponse(resp_data)


def check_text(
    text_content: str,
    action: Action,
    form: EditActionOutForm,
) -> bool:
    """Check that the text content renders correctly as a template.

    :param text_content: String with the text
    :param action: Action to obtain the context
    :param form: Form to report errors.
    :return: Boolean
    """
    # Render the content as a template and catch potential problems.
    # This seems to be only possible if dealing directly with Jinja2
    # instead of Django.
    try:
        render_error = False
        render_template(text_content, {}, action)
    except Exception as exc:
        # Pass the django exception to the form (fingers crossed)
        form.add_error(None, exc)
        render_error = True

    return render_error


@user_passes_test(is_instructor)
@csrf_exempt
def action_out_save_content(request: HttpRequest, pk: int) -> JsonResponse:
    """Save content of the action out.

    :param request: HTTP request (POST)
    :param pk: Action ID
    :return: Nothing, changes reflected in the DB
    """
    # Try to get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('home')})

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not filter:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('home')})

    # Wrong type of action.
    if action.is_in:
        return JsonResponse(
            {'form_is_valid': True,
             'html_redirect': reverse('home')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    return JsonResponse({'form_is_valid': True, 'html_redirect': ''})


@user_passes_test(is_instructor)
def edit_action(request: HttpRequest, pk: int) -> HttpResponse:
    """Invoke the specific edit view.

    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """
    # Try to get the workflow first
    workflow = get_workflow(
        request,
        prefetch_related=['actions', 'columns'])
    if not workflow:
        return redirect('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        messages.error(request, _('Incorrect action request'))
        return redirect('action:index')

    if action.action_type == Action.todo_list:
        return redirect(reverse('under_construction'), {})

    distributor = {
        Action.personalized_text: edit_action_out,
        Action.personalized_canvas_email: edit_action_out,
        Action.personalized_json: edit_action_out,
        Action.survey: edit_action_in,
    }
    return distributor[action.action_type](request, workflow, action)


def edit_action_out(
    request: HttpRequest,
    workflow: Workflow,
    action: Action,
) -> HttpResponse:
    """Edit action out.

    :param request: Request object
    :param workflow: The workflow with the action
    :param action: Action
    :return: HTML response
    """
    # Create the form
    form = EditActionOutForm(request.POST or None, instance=action)

    form_filter = FilterForm(
        request.POST or None,
        instance=action.get_filter())

    # Processing the request after receiving the text from the editor
    if request.method == 'POST' and form.is_valid() and form_filter.is_valid():
        # Get content
        text_content = form.cleaned_data.get('text_content', None)

        # Render the content as a template and catch potential problems.
        if not check_text(text_content, action, form):
            # Log the event
            Log.objects.register(
                request.user,
                Log.ACTION_UPDATE,
                action.workflow,
                {'id': action.id,
                 'name': action.name,
                 'workflow_id': workflow.id,
                 'workflow_name': workflow.name,
                 'content': text_content})

            # Text is good. Update the content of the action
            action.set_text_content(text_content)

            if action.action_type == Action.personalized_json:
                # Update the target_url field
                action.target_url = form.cleaned_data['target_url']

            action.save()

            if request.POST['Submit'] == 'Submit':
                return redirect(request.get_full_path())

            return redirect('action:index')

    # This is a GET request or a faulty POST request

    # Get the filter or None
    filter_condition = action.get_filter()

    # Context to render the form
    context = {
        'filter_condition': filter_condition,
        'action': action,
        'load_summernote': action.action_type == Action.personalized_text,
        'conditions': action.conditions.filter(is_filter=False),
        'other_conditions': Condition.objects.filter(
            action__workflow=workflow, is_filter=False,
        ).exclude(action=action),
        'query_builder_ops': workflow.get_query_builder_ops_as_str(),
        'attribute_names': [
            attr for attr in list(workflow.attributes.keys())
        ],
        'columns': workflow.columns.filter(is_key=False),
        'selected_rows':
            filter_condition.n_rows_selected
            if filter_condition else -1,
        'has_data': action.workflow.has_table(),
        'all_false_conditions': any(
            cond.n_rows_selected == 0
            for cond in action.conditions.all()),
        'rows_all_false': action.get_row_all_false_count(),
        'total_rows': workflow.nrows,
        'form': form,
        'form_filter': form_filter,
        'vis_scripts': PlotlyHandler.get_engine_scripts(),
    }

    # Return the same form in the same page
    return render(request, 'action/edit_out.html', context=context)
