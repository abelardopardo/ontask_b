# -*- coding: utf-8 -*-

"""Functions to perform the import/export operations."""
from datetime import datetime
import gzip
from io import BytesIO
from typing import Dict, List, Optional

from django import http
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from ontask import models
from ontask.core.checks import check_workflow
from ontask.workflow import services
from ontask.action import services as action_services
from ontask.workflow.serializers import (
    WorkflowExportSerializer, WorkflowImportSerializer,
)


def _run_compatibility_patches(json_data: Dict) -> Dict:
    """Patch the incoming JSON to make it compatible.

    Over time the structure of the JSON information used to dump a workflow
    has changed. These patches are to guarantee that an old workflow is
    compliant with the new structure. The patches applied are:

    :param json_data: Json object to process
    :return: Modified json_data
    """

    # Various changes in the actions
    json_data['actions'] = action_services.run_compatibility_patches(
        json_data['actions'])

    # Change the formula field in the view
    for view in json_data.get('views', []):
        if '_formula' in view:
            continue
        view['_formula'] = view.pop('formula')

    return json_data


def do_import_workflow_parse(
    user,
    name: str,
    file_item,
) -> models.Workflow:
    """Read gzip file, create serializer and parse the data.

    Check for validity and create the workflow

    :param user: User used for the operation
    :param name: Workflow name
    :param file_item: File item previously opened
    :return: workflow object or raise exception
    """
    try:
        data_in = gzip.GzipFile(fileobj=file_item)
        json_data = JSONParser().parse(data_in)
    except IOError:
        raise Exception(
            _('Incorrect file. Expecting a GZIP file (exported workflow).'),
        )

    _run_compatibility_patches(json_data)

    # Serialize content
    workflow_data = WorkflowImportSerializer(
        data=json_data,
        context={'user': user, 'name': name})

    # If anything went wrong, return the string to show to the form.
    if not workflow_data.is_valid():
        raise serializers.ValidationError(workflow_data.errors)

    # Save the new workflow
    workflow = workflow_data.save()

    try:
        check_workflow(workflow)
    except AssertionError:
        # Something went wrong.
        if workflow:
            workflow.delete()
        raise

    return workflow


def do_import_workflow(
    user,
    name: Optional[str],
    file_item,
):
    """Create a new structure of workflow stored in the file item.

    Receives a name and a file item (submitted through a form) and creates
    the structure of workflow, conditions, actions and data table.

    :param user: User record to use for the import (own all created items)
    :param name: Workflow name (it has been checked that it does not exist)
    :param file_item: File item obtained through a form
    :return:
    """
    try:
        workflow = do_import_workflow_parse(user, name, file_item)
    except IOError:
        raise services.OnTaskWorkflowImportError(
            _('Incorrect file. Expecting a GZIP file (exported workflow).'))
    except (TypeError, NotImplementedError) as exc:
        raise services.OnTaskWorkflowImportError(
            _('Unable to import workflow. Exception: {0}').format(exc))
    except serializers.ValidationError as exc:
        raise services.OnTaskWorkflowImportError(
            _('Unable to import workflow. Validation error: {0}').format(
                exc))
    except AssertionError:
        # Something went wrong.
        raise services.OnTaskWorkflowImportError(
            _('Workflow data with incorrect structure.'))
    except Exception as exc:
        raise services.OnTaskWorkflowImportError(
            _('Unable to import workflow: {0}').format(exc))

    workflow.log(user, models.Log.WORKFLOW_IMPORT)


def do_export_workflow_parse(
    workflow: models.Workflow,
    selected_actions: Optional[List[int]] = None,
) -> BytesIO:
    """Serialize the workflow and attach its content to a BytesIO object.

    :param workflow: Workflow to serialize
    :param selected_actions: Subset of actions
    :return: BytesIO
    """
    # Get the info to send from the serializer
    serializer = WorkflowExportSerializer(
        workflow,
        context={'selected_actions': selected_actions},
    )
    to_send = JSONRenderer().render(serializer.data)

    # Get the in-memory file to compress
    zbuf = BytesIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(to_send)
    zfile.close()

    return zbuf


def do_export_workflow(
    workflow: models.Workflow,
    selected_actions: Optional[List[int]] = None,
) -> http.HttpResponse:
    """Proceed with the workflow export.

    :param workflow: Workflow record to export be included.
    :param selected_actions: A subset of actions to export
    :return: Page that shows a confirmation message and starts the download
    """
    # Get the in-memory compressed file
    zbuf = do_export_workflow_parse(workflow, selected_actions)

    suffix = datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = zbuf.getvalue()
    response = http.HttpResponse(compressed_content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = (
        'attachment; filename="ontask_workflow_{0}.gz"'.format(suffix)
    )
    response['Content-Length'] = str(len(compressed_content))

    return response
