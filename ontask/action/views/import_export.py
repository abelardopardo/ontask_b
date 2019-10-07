# -*- coding: utf-8 -*-

"""Views for import/export."""

import datetime
import gzip
from io import BytesIO
from typing import List, Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from ontask.action.forms import ActionImportForm
from ontask.action.serializers import ActionSelfcontainedSerializer
from ontask.core.decorators import get_action, get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Action, Log, Workflow


def do_import_action(
    user,
    workflow: Workflow,
    file_item,
) -> List[Action]:
    """Import action.

    Receives a name and a file item (submitted through a form) and creates
    the structure of action with conditions and columns

    :param user: User record to use for the import (own all created items)
    :param workflow: Workflow object to attach the action
    :param file_item: File item obtained through a form
    :return: List of actions. Reflect in DB
    """
    try:
        data_in = gzip.GzipFile(fileobj=file_item)
        parsed_data = JSONParser().parse(data_in)
    except IOError:
        raise Exception(
            _('Incorrect file. Expecting a GZIP file (exported workflow).'),
        )

    # Serialize content
    action_data = ActionSelfcontainedSerializer(
        data=parsed_data,
        many=True,
        context={
            'user': user,
            'workflow': workflow},
    )

    # If anything goes wrong, return a string to show in the page.
    if not action_data.is_valid():
        raise Exception(
            _('Unable to import action: {0}').format(action_data.errors),
        )
    # Save the new action
    actions = action_data.save(user=user)

    # Success, log the event
    for action in actions:
        action.log(user, Log.ACTION_IMPORT)

    return actions


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_import(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Import one action given in a gz file.

    :param request: Http request

    :return: HTTP response
    """
    form = ActionImportForm(request.POST or None, request.FILES or None)

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
                actions = do_import_action(
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
    request: HttpRequest,
    pklist: str,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Export the actions given as comma separated list of ids.

    :param request:
    :param pklist: comma separated list of action ids as strs
    :param workflow: Set by the decorators (current workflow)
    :return: HTTP response
    """

    try:
        action_ids = [int(a_idx) for a_idx in pklist.split(',')]
    except ValueError:
        return redirect('home')

    # Serialize the content and return data
    serializer = ActionSelfcontainedSerializer(
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
    response = HttpResponse(compressed_content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = (
        'attachment; filename="ontask_actions_{0}.gz"'.format(
            datetime.datetime.now().strftime('%y%m%d_%H%M%S')))
    response['Content-Length'] = str(len(compressed_content))

    return response
