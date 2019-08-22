# -*- coding: utf-8 -*-

"""Views for import/export."""

import datetime
import gzip
from io import BytesIO
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
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


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def export_ask(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Ask for confirmation before exporting an action.

    :param request: HTTP request

    :param pk: Action ID

    :param workflow: Workflow object (obtained by decorator)

    :param action: Action object (obtained by decorator)

    :return: HTTP response to the next page where the export is done
    """
    return render(
        request,
        'action/export_ask.html',
        {'action': action,
         'cnames': [
             cpair.column.name
             for cpair in action.column_condition_pair.all()]})


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def export_done(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Show page stating that export operation has finished.

    :param request:

    :param pk: Unique key of the action to export

    :return: HTTP response
    """
    return render(request, 'action/export_done.html', {'action': action})


@user_passes_test(is_instructor)
@get_action(pf_related='actions')
def export_download(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Export the action pointed by the pk.

    :param request:
    :param pk: Unique key of the action to export
    :return: HTTP response
    """
    # Get the info to send from the serializer
    serializer = ActionSelfcontainedSerializer(
        action,
        context={'workflow': action.workflow})

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
        'attachment; '
        + 'filename="ontask_action_{0}.gz"'.format(
            datetime.datetime.now().strftime('%y%m%d_%H%M%S'),
        )
    )
    response['Content-Length'] = str(len(compressed_content))

    return response


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
    form = ActionImportForm(
        request.POST or None,
        request.FILES or None,
        workflow=workflow,
        user=request.user)

    if request.method == 'POST' and form.is_valid():
        # Process the reception of the file
        if not form.is_multipart():
            form.add_error(
                None,
                _('Incorrect form (it does not have a file attached)'))
            return render(request, 'action/import.html', {'form': form})

        # UPLOAD THE FILE!
        try:
            do_import_action(
                request.user,
                workflow,
                form.cleaned_data['name'],
                request.FILES['upload_file'])
        except KeyError as exc:
            # Attach the exception to the request
            messages.error(
                request,
                _('Unable to import file. Incorrect fields.').format(str(exc)),
            )
        except Exception as exc:
            # Attach the exception to the request
            messages.error(
                request,
                _('Unable to import file: {0}').format(str(exc)),
            )

        # Go back to the list of actions
        return redirect('action:index')

    return render(request, 'action/import.html', {'form': form})


def do_import_action(
    user,
    workflow: Workflow,
    name: str,
    file_item,
):
    """Import action.

    Receives a name and a file item (submitted through a form) and creates
    the structure of action with conditions and columns

    :param user: User record to use for the import (own all created items)
    :param workflow: Workflow object to attach the action
    :param name: Workflow name (it has been checked that it does not exist)
    :param file_item: File item obtained through a form
    :return: Nothing. Reflect in DB
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
        context={
            'user': user,
            'name': name,
            'workflow': workflow},
    )

    # If anything goes wrong, return a string to show in the page.
    if not action_data.is_valid():
        raise Exception(
            _('Unable to import action: {0}').format(action_data.errors),
        )
    # Save the new action
    action = action_data.save(user=user, name=name)

    # Success, log the event
    Log.objects.register(
        user,
        Log.ACTION_IMPORT,
        workflow,
        {'id': action.id,
         'name': action.name})
