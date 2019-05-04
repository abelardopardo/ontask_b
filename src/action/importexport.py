# -*- coding: utf-8 -*-

"""Functions to import/export actions in a workflow."""

import datetime
import gzip
from io import BytesIO

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from action.models import Action
from action.serializers import ActionSelfcontainedSerializer
from logs.models import Log
from workflow.models import Workflow


def do_export_action(action: Action) -> HttpResponse:
    """Export action.

    :param action: Element to export.
    :return: Page that shows a confirmation message and starts the download
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
            'workflow': workflow,
            'columns': workflow.columns.all()},
    )

    # If anything goes wrong, return a string to show in the page.
    if not action_data.is_valid():
        raise Exception(
            _('Unable to import action: {0}').format(action_data.errors),
        )
    # Save the new workflow
    action = action_data.save(user=user, name=name)

    # Success, log the event
    Log.objects.register(
        user,
        Log.ACTION_IMPORT,
        workflow,
        {'id': action.id,
         'name': action.name})
