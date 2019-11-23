# -*- coding: utf-8 -*-

"""Functions to support the display of a view."""
import copy

from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template.loader import render_to_string

from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables

from ontask.core import OperationsColumn
from ontask.models import View, Workflow, Log
from ontask.table.forms import ViewAddForm


class ViewTable(tables.Table):
    """Table to display the set of views handled in a workflow."""

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(
        empty_values=[],
        verbose_name=_('Description'))

    operations = OperationsColumn(
        verbose_name='',
        template_file='table/includes/partial_view_operations.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render the name of the action as a link."""
        return format_html(
            """<a href="#" class="js-view-edit"
                  data-toggle="tooltip" data-url="{0}"
                  title="{1}">{2}</a>""",
            reverse('table:view_edit', kwargs={'pk': record['id']}),
            _('Change the columns present in the view'),
            record['name'],
        )

    class Meta(object):
        """Select the model and specify fields, sequence and attributes."""

        model = View

        fields = ('name', 'description_text', 'operations')

        sequence = ('name', 'description_text', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'view-table',
        }


def do_clone_view(
    view: View,
    new_workflow: Workflow = None,
    new_name: str = None,
) -> View:
    """Clone a view.

    :param view: Object to clone

    :param new_workflow: Non empty if it has to point to a new workflow

    :param new_name: Non empty if it has to be renamed.

    :result: New clone object
    """
    # Proceed to clone the view
    if new_name is None:
        new_name = view.name
    if new_workflow is None:
        new_workflow = view.workflow

    new_view = View(
        name=new_name,
        description_text=view.description_text,
        workflow=new_workflow,
        formula=copy.deepcopy(view.formula),
    )
    new_view.save()

    try:
        # Update the many to many field.
        new_view.columns.set(list(view.columns.all()))
    except Exception as exc:
        new_view.delete()
        raise exc

    return new_view


def save_view_form(
    request: HttpRequest,
    form: ViewAddForm,
    template_name: str,
) -> JsonResponse:
    """Save the data attached to a view as provided in a form.

    :param request: HTTP request

    :param form: Form object with the collected information

    :param template_name: To render the response

    :return: AJAX Response
    """
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        # Correct POST submission
        view = form.save(commit=False)
        view.workflow = form.workflow
        view.save()
        form.save_m2m()  # Needed to propagate the save effect to M2M relations
        view.log(
            request.user,
            Log.VIEW_EDIT if form.instance.id else Log.VIEW_CREATE)

        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id},
            request=request),
    })
