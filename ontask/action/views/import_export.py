# -*- coding: utf-8 -*-

"""Views for import/export."""
import datetime
import gzip
from io import BytesIO
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from rest_framework.renderers import JSONRenderer

from ontask import models
from ontask.action import forms, serializers, services
from ontask.core import get_workflow, is_instructor


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_import(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Import one action given in a gz file.

    :param request: Http request
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: HTTP response
    """
    form = forms.ActionImportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        # Process the reception of the file
        if not form.is_multipart():
            form.add_error(
                None,
                _('Incorrect form (it does not have a file attached)'))
            return render(request, 'action/import.html', {'form': form})

        # UPLOAD THE FILE!
        try:
            with transaction.atomic():
                actions = services.do_import_action(
                    request.user,
                    workflow,
                    request.FILES['upload_file'])
        except KeyError as exc:
            # Attach the exception to the request
            messages.error(
                request,
                _('Unable to import file. Incorrect fields.').format(str(exc)),
            )
            return redirect('action:index')
        except Exception as exc:
            # Attach the exception to the request
            messages.error(
                request,
                _('Unable to import file: {0}').format(str(exc)),
            )
            return redirect('action:index')

        messages.success(
            request,
            _('Actions imported: {0}'.format(', '.join(
                [action.name for action in actions]
            )))
        )
        # Go back to the list of actions
        return redirect('action:index')

    return render(request, 'action/import.html', {'form': form})


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def export(
    request: http.HttpRequest,
    pklist: str,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Export the actions given as comma separated list of ids.

    :param request:
    :param pklist: comma separated list of action ids as strs
    :param workflow: Set by the decorators (current workflow)
    :return: HTTP response
    """
    del request
    try:
        action_ids = [int(a_idx) for a_idx in pklist.split(',')]
    except ValueError:
        return redirect('home')

    # Serialize the content and return data
    serializer = serializers.ActionSelfcontainedSerializer(
        instance=workflow.actions.filter(id__in=action_ids),
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
