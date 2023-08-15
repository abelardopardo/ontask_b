"""View to edit rubric actions."""

from django import http
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import models
from ontask.action import forms
from ontask.core import (
    ActionView, JSONFormResponseMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ActionEditRubricCellView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView,
):
    """Edit a cell in a rubric."""
    http_method_names = ['get', 'post']
    form_class = forms.RubricCellForm
    template_name = 'action/includes/partial_rubric_cell_edit.html'
    object = None

    def setup(self, request, *args, **kwargs):
        """Set the object as attribute."""
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()
        return

    def get_form_kwargs(self):
        """Add the criteria to the context for the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object.rubric_cells.filter(
            column=self.kwargs['cid'],
            loa_position=self.kwargs['loa_pos']).first()
        return kwargs

    def form_valid(self, form) -> http.JsonResponse:
        action_content = self.request.POST.get('action_content')
        if action_content:
            self.object.set_text_content(action_content)
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        cell = form.save(commit=False)
        if cell.id is None:
            # New cell in the rubric
            cell.action = self.object
            cell.column = self.object.workflow.columns.get(
                pk=self.kwargs['cid'])
            cell.loa_position = self.kwargs['loa_pos']
        cell.save()
        cell.log(self.request.user, models.Log.ACTION_RUBRIC_CELL_EDIT)
        return http.JsonResponse({'html_redirect': ''})
