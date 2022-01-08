# -*- coding: utf-8 -*-

"""Views for create/update columns that are criteria in a rubric."""

from django import http
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ontask import OnTaskServiceException, models
from ontask.column import forms, services
from ontask.core import (
    ActionView, ColumnConditionView, JSONFormResponseMixin,
    SingleColumnConditionMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView):
    """Add a new criteria to an action.

    If it is the first criteria, the form simply asks for a question with a
    non-empty category field.

    If it is not the first criteria, then the criteria are fixed by the
    previous elements in the rubric.
    """

    http_method_names = ['get', 'post']
    form_class = forms.CriterionForm
    template_name = 'workflow/includes/partial_criterion_addedit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['other_criterion'] = self.action.column_condition_pair.first()
        kwargs['workflow'] = self.action.workflow
        return kwargs

    def get(self, request, *args, **kwargs):
        if self.action.action_type != models.Action.RUBRIC_TEXT:
            messages.error(
                request,
                _('Operation only valid or Rubric actions'),
            )
            return http.JsonResponse({'html_redirect': ''})

        if self.action.workflow.nrows == 0:
            messages.error(
                request,
                _('Cannot add criteria to a workflow without data'),
            )
            return http.JsonResponse({'html_redirect': ''})

        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                self.request.user,
                self.workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_RUBRIC_CRITERION_ADD,
                self.action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionEditView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ColumnConditionView,
    generic.FormView,
):
    """Edit a criterion in a rubric."""

    http_method_names = ['get', 'post']
    form_class = forms.CriterionForm
    template_name = 'workflow/includes/partial_criterion_addedit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        action = self.cc_tuple.action
        column = self.cc_tuple.column

        kwargs['workflow'] = action.workflow
        kwargs['other_criterion'] = action.column_condition_pair.exclude(
            column=column.id).first()
        kwargs['instance'] = column
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        column = form.save(commit=False)
        services.update_column(
            self.request.user,
            self.workflow,
            column,
            form.old_name,
            form.old_position,
            self.cc_tuple,
            models.Log.ACTION_RUBRIC_CRITERION_EDIT)
        form.save_m2m()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleColumnConditionMixin,
    ColumnConditionView,
    generic.DeleteView,
):
    """Delete a criterion in a rubric."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_criterion_delete.html'

    def delete(self, request, *args, **kwargs):
        self.cc_tuple.log(
            request.user,
            models.Log.ACTION_RUBRIC_CRITERION_DELETE)
        self.cc_tuple.delete()
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ColumnCriterionInsertView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Add an existing column as rubric criteria."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)

        criteria = self.action.column_condition_pair.all()
        column = self.workflow.columns.filter(pk=kwargs['cpk']).first()
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
            action=self.action,
            column=column,
            condition=None)

        acc.log(request.user, models.Log.ACTION_RUBRIC_CRITERION_ADD)

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})


# @user_passes_test(is_instructor)
# @csrf_exempt
# @ajax_required
# @require_POST
# @get_action(pf_related=['columns', 'actions'])
# def criterion_insert(
#     request: http.HttpRequest,
#     pk: int,
#     cpk: int,
#     workflow: Optional[models.Workflow] = None,
#     action: Optional[models.Action] = None,
# ) -> http.JsonResponse:
#     """Operation to add a criterion to a rubric.
#
#     :param request: Request object
#     :param pk: Action PK
#     :param cpk: column PK.
#     :param workflow: Workflow being manipulated
#     :param action: Action object where the criterion is inserted
#     :return: JSON response
#     """
#     # If the request has the 'action_content', update the action
#     action_content = request.POST.get('action_content')
#     if action_content:
#         action.set_text_content(action_content)
#
#     criteria = action.column_condition_pair.filter(action_id=pk)
#     column = workflow.columns.filter(pk=cpk).first()
#     if not column or criteria.filter(column=column).exists():
#         messages.error(
#             request,
#             _('Incorrect invocation of criterion insert operation.'),
#         )
#         return http.JsonResponse({'html_redirect': ''})
#
#     if (
#         criteria
#         and set(column.categories) != set(criteria[0].column.categories)
#     ):
#         messages.error(
#             request,
#             _('Criterion does not have the correct levels of attainment'),
#         )
#         return http.JsonResponse({'html_redirect': ''})
#
#     if not criteria and len(column.categories) == 0:
#         messages.error(
#             request,
#             _('The column needs to have a fixed set of possible values'),
#         )
#         return http.JsonResponse({'html_redirect': ''})
#
#     acc = models.ActionColumnConditionTuple.objects.create(
#         action=action,
#         column=column,
#         condition=None)
#
#     acc.log(request.user, models.Log.ACTION_RUBRIC_CRITERION_ADD)
#
#     # Refresh the page to show the column in the list.
#     return http.JsonResponse({'html_redirect': ''})
