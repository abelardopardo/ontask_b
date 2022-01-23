# -*- coding: utf-8 -*-

"""Views for import/export."""
import datetime
import gzip
from io import BytesIO

from django import http
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import generic
from rest_framework.renderers import JSONRenderer

from ontask.action import forms, serializers, services
from ontask.core import UserIsInstructor, WorkflowView


class ActionImportView(UserIsInstructor, WorkflowView, generic.FormView):
    """Import one action given in a gz file."""

    http_method_names = ['get', 'post']
    form_class = forms.ActionImportForm
    template_name = 'action/import.html'

    def form_valid(self, form) -> http.JsonResponse:
        # Process the reception of the file
        if not form.is_multipart():
            form.add_error(
                None,
                _('Incorrect form (it does not have a file attached)'))
            return render(self.request, 'action/import.html', {'form': form})

        # UPLOAD THE FILE!
        try:
            with transaction.atomic():
                actions = services.do_import_action(
                    self.request.user,
                    self.workflow,
                    self.request.FILES['upload_file'])
        except KeyError as exc:
            # Attach the exception to the request
            messages.error(
                self.request,
                _('Unable to import file. Incorrect fields.').format(str(exc)),
            )
            return redirect('action:index')
        except Exception as exc:
            # Attach the exception to the request
            messages.error(
                self.request,
                _('Unable to import file: {0}').format(str(exc)),
            )
            return redirect('action:index')

        messages.success(
            self.request,
            _('Actions imported: {0}'.format(', '.join(
                [action.name for action in actions]))))
        # Go back to the list of actions
        return redirect('action:index')


class ActionExportView(UserIsInstructor, WorkflowView):
    """Export the actions given as comma separated list of ids."""

    http_method_names = ['get', 'post']
    wf_pf_related = 'actions'

    def get(self, request, *args, **kwargs):
        try:
            action_ids = [
                int(a_idx) for a_idx in kwargs.get('pklist').split(',')]
        except ValueError:
            return redirect('home')

        # All ids have to correspond to an action
        actions = self.workflow.actions.filter(id__in=action_ids)
        if actions.count() != len(action_ids):
            return redirect('home')

        # Serialize the content and return data
        serializer = serializers.ActionSelfcontainedSerializer(
            instance=actions,
            many=True,
            required=True)

        # Get the in-memory file to compress
        zbuf = BytesIO()
        zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        zfile.write(JSONRenderer().render(serializer.data))
        zfile.close()

        # Attach the compressed value to the response and send
        compressed_content = zbuf.getvalue()
        response = http.HttpResponse(compressed_content)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = (
            'attachment; filename="ontask_actions_{0}.gz"'.format(
                datetime.datetime.now().strftime('%y%m%d_%H%M%S')))
        response['Content-Length'] = str(len(compressed_content))

        return response
