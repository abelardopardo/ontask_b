"""Factory to edit the different action types."""
from typing import Dict

from django import http
from django.shortcuts import redirect
from django.views import generic

from ontask import models, core
from ontask.condition import forms as condition_forms
from ontask.visualizations.plotly import PlotlyHandler


class ActionEditFactory(core.FactoryBase):
    """Factory to manage Edit actions."""

    def process_request(
        self,
        request: http.HttpRequest,
        action_type: int,
        **kwargs
    ) -> http.HttpResponse:
        """Execute function to process an edit request.

        :param request: Http Request received (get or post)
        :param action_type: Type of action being manipulated
        :param kwargs: Dictionary with action
        :return: HttpResponse
        """
        try:
            edit_view = self._get_producer(action_type)
        except ValueError:
            return redirect('home')

        return edit_view(request, **kwargs)


ACTION_EDIT_FACTORY = ActionEditFactory()


class ActionEditProducerBase(generic.UpdateView):
    """Base class for edit view for the actions."""

    model = models.Action

    workflow = None

    action = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.workflow = kwargs.get('workflow', None)
        self.action = kwargs.get('action', None)

    def get_object(self, queryset=None):
        """Bypass the method and simply return the action."""
        return self.action

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # Workflow elements
            'attribute_names': [
                attr for attr in list(self.workflow.attributes.keys())
            ],
            'columns': self.workflow.columns.all(),
            'has_data': self.workflow.has_data_frame,
            'total_rows': self.workflow.nrows,
            'views': self.workflow.views.filter(
                filter__isnull=False).exclude(
                filter=self.action.filter),

            # Action Elements
            'action': self.action,
            'filter_condition': self.action.filter,
            'selected_rows':
                self.action.filter.selected_count
                if self.action.filter else -1,
            'is_email_report':
                self.action.action_type == models.Action.EMAIL_REPORT,
            'is_report': (
                self.action.action_type == models.Action.EMAIL_REPORT
                or self.action.action_type == models.Action.JSON_REPORT),
            'is_personalized_text': (
                self.action.action_type == models.Action.PERSONALIZED_TEXT),
            'is_rubric': self.action.action_type == models.Action.RUBRIC_TEXT,
            'is_survey': self.action.action_type == models.Action.SURVEY,
            'all_false_conditions': any(
                cond.selected_count == 0
                for cond in self.action.conditions.all()),
            'rows_all_false': self.action.get_row_all_false_count(),

            'query_builder_ops': self.workflow.get_query_builder_ops(),
            'vis_scripts': PlotlyHandler.get_engine_scripts()})
        return context

    def add_conditions_to_clone(self, context: Dict):
        """Add conditions clone to the context

        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['conditions_to_clone'] = self.workflow.conditions.exclude(
            action=self.action)

    def add_columns_show_stats(self, context: Dict):
        """Add conditions to show stats to the context

        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['columns_show_stat'] = self.workflow.columns.filter(
            is_key=False)

    def add_conditions(self, context: Dict):
        """Add conditions to the context

        :param context: Context to modify
        :return: Nothing, the context is modified in place
        """
        context['conditions'] = self.action.conditions.all()


class ActionOutEditProducerBase(ActionEditProducerBase):
    """Class to provide edit methods for the actions out."""

    def get_context_data(self, **kwargs) -> Dict:
        """Add the form_filter to the context"""
        context = super().get_context_data(**kwargs)
        context.update({
            'form_filter': condition_forms.FilterForm(
                self.request.POST or None,
                instance=self.action.filter)})
        return context

    def form_valid(self, form):
        form_filter = condition_forms.FilterForm(
            self.request.POST or None,
            instance=self.action.filter)
        if not form_filter.is_valid():
            # Second part of the form is not valid, reload.
            return self.get(self.request)

        # Text is good. Update the content of the action
        self.action.set_text_content(form.cleaned_data['text_content'])
        if 'target_url' in form.cleaned_data:
            self.action.target_url = form.cleaned_data['target_url']
            self.action.save(update_fields=['target_url'])

        # Log the event
        self.action.log(self.request.user, models.Log.ACTION_UPDATE)

        if self.request.POST['Submit'] == 'Submit':
            return redirect(self.request.get_full_path())

        return redirect('action:index')
