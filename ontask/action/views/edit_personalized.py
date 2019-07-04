# -*- coding: utf-8 -*-

"""Views to edit actions."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from ontask.action.evaluate import render_action_template
from ontask.action.forms import EditActionOutForm, EnableURLForm, FilterForm
from ontask.action.models import Action, Condition
from ontask.core.decorators import ajax_required, get_action
from ontask.core.permissions import is_instructor
from ontask.logs.models import Log
from ontask.visualizations.plotly import PlotlyHandler
from ontask.workflow.models import Workflow


def text_renders_correctly(
    text_content: str,
    action: Action,
    form: EditActionOutForm,
) -> bool:
    """Check that the text content renders correctly as a template.

    :param text_content: String with the text

    :param action: Action to obtain the context

    :param form: Form to report errors.

    :return: Boolean stating correctness
    """
    # Render the content as a template and catch potential problems.
    # This seems to be only possible if dealing directly with Jinja2
    # instead of Django.
    try:
        render_action_template(text_content, {}, action)
    except Exception as exc:
        # Pass the django exception to the form (fingers crossed)
        form.add_error(None, str(exc))
        return False

    return True


@user_passes_test(is_instructor)
@csrf_exempt
@ajax_required
@get_action(pf_related='actions')
def action_out_save_content(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Save content of the action out.

    :param request: HTTP request (POST)
    :param pk: Action ID
    :return: Nothing, changes reflected in the DB
    """
    # Wrong type of action.
    if action.is_in:
        return JsonResponse({'html_redirect': reverse('home')})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)
        action.save()

    return JsonResponse({'html_redirect': ''})


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
        instance=action.get_filter(),
        action=action
    )

    # Processing the request after receiving the text from the editor
    if request.method == 'POST' and form.is_valid() and form_filter.is_valid():
        # Get content
        text_content = form.cleaned_data.get('text_content')

        # Render the content as a template and catch potential problems.
        if text_renders_correctly(text_content, action, form):
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
        'columns': workflow.columns.all(),
        'stat_columns': workflow.columns.filter(is_key=False),
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


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def showurl(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Create page to show URL to access action.

    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.

    :param request: Json request

    :param pk: Primary key of the action to show the URL

    :return: Json response with the content to show in the screen
    """
    form = EnableURLForm(request.POST or None, instance=action)

    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            Log.objects.register(
                request.user,
                Log.ACTION_SERVE_TOGGLED,
                action.workflow,
                {'id': action.id,
                 'name': action.name,
                 'serve_enabled': action.serve_enabled})
            return JsonResponse({'html_redirect': reverse('action:index')})

        return JsonResponse({'html_redirect': None})

    # Create the text for the action
    url_text = reverse('action:serve', kwargs={'action_id': action.id})

    # Render the page with the abolute URI
    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_showurl.html',
            {'url_text': request.build_absolute_uri(url_text),
             'form': form,
             'action': action},
            request=request),
    })
