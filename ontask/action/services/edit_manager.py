# -*- coding: utf-8 -*-

"""Classes to edit actions  through the manager."""
from typing import Dict, Optional, Type

from django import forms, http
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from ontask import models
from ontask.condition import forms as condition_forms
from ontask.visualizations.plotly import PlotlyHandler


class ActionEditManager:
    """Base class to provide edit methods for the actions."""

    def __init__(self, *args, **kwargs):
        """Assign and initialize the main service parameters."""
        self.edit_form_class = kwargs.pop('edit_form_class', None)
        self.edit_template = kwargs.pop('edit_template', None)
        super().__init__(*args, **kwargs)

    @staticmethod
    def add_conditions(action: models.Action, context: Dict):
        """Add conditions to the context

        :param action: Action being processed
        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['conditions'] = action.conditions.all()

    @staticmethod
    def add_conditions_to_clone(action: models.Action, context: Dict):
        """Add conditions clone to the context

        :param action: Action being processed
        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['conditions_to_clone'] = action.workflow.conditions.exclude(
            action=action)

    @staticmethod
    def add_columns_show_stats(action: models.Action, context: Dict):
        """Add conditions to show stats to the context

        :param action: Action being processed
        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['columns_show_stat'] = action.workflow.columns.filter(
            is_key=False)

    def extend_edit_context(
        self,
        workflow: models.Workflow,
        action: models.Action,
        context: Dict,
    ):
        """Get the context dictionary to render the GET request.

        :param workflow: Workflow being used
        :param action: Action being used
        :param context: Initial dictionary to extend
        :return: Nothing.
        """
        del workflow, action, context

    @staticmethod
    def get_render_context(
        action: models.Action,
        form: Optional[Type[forms.ModelForm]] = None,
        form_filter: Optional[condition_forms.FilterForm] = None,
    ) -> Dict:
        """Get the initial context to render the response."""
        filter_condition = action.get_filter()
        return {
            # Workflow elements
            'attribute_names': [
                attr for attr in list(action.workflow.attributes.keys())
            ],
            'columns': action.workflow.columns.all(),
            'has_data': action.workflow.has_table(),
            'total_rows': action.workflow.nrows,
            'views': [
                view for view in action.workflow.views.all()
                if not view.has_empty_formula],

            # Action Elements
            'action': action,
            'form': form,
            'form_filter': form_filter,
            'filter_condition': filter_condition,
            'selected_rows':
                filter_condition.n_rows_selected
                if filter_condition else -1,
            'is_email_report':
                action.action_type == models.Action.EMAIL_REPORT,
            'is_report': (
                action.action_type == models.Action.EMAIL_REPORT
                or action.action_type == models.Action.JSON_REPORT),
            'is_personalized_text': (
                action.action_type == models.Action.PERSONALIZED_TEXT),
            'is_rubric': action.action_type == models.Action.RUBRIC_TEXT,
            'is_survey': action.action_type == models.Action.SURVEY,
            'all_false_conditions': any(
                cond.n_rows_selected == 0
                for cond in action.conditions.all()),
            'rows_all_false': action.get_row_all_false_count(),

            # Page elements
            'load_summernote': (
                action.action_type == models.Action.PERSONALIZED_TEXT
                or action.action_type == models.Action.EMAIL_REPORT
                or action.action_type == models.Action.RUBRIC_TEXT
            ),
            'query_builder_ops': action.workflow.get_query_builder_ops_as_str(),
            'vis_scripts': PlotlyHandler.get_engine_scripts()}


class ActionOutEditManager(ActionEditManager):
    """Class to provide edit methods for the actions out."""

    def process_edit_request(
        self,
        request: http.HttpRequest,
        workflow: models.Workflow,
        action: models.Action
    ) -> http.HttpResponse:
        """Process the action edit request."""
        form = self.edit_form_class(request.POST or None, instance=action)

        form_filter = condition_forms.FilterForm(
            request.POST or None,
            instance=action.get_filter(),
            action=action
        )

        # Processing the request after receiving the text from the editor
        if (
            request.method == 'POST'
            and form.is_valid()
            and form_filter.is_valid()
        ):
            # Log the event
            action.log(request.user, models.Log.ACTION_UPDATE)

            # Text is good. Update the content of the action
            action.set_text_content(form.cleaned_data['text_content'])
            if 'target_url' in form.cleaned_data:
                action.target_url = form.cleaned_data['target_url']
                action.save(update_fields=['target_url'])

            if request.POST['Submit'] == 'Submit':
                return redirect(request.get_full_path())

            return redirect('action:index')

        # This is a GET request or a faulty POST request
        context = self.get_render_context(action, form, form_filter)
        try:
            self.extend_edit_context(workflow, action, context)
        except Exception as exc:
            messages.error(request, str(exc))
            return redirect(reverse('action:index'))

        # Return the same form in the same page
        return render(request, self.edit_template, context=context)
