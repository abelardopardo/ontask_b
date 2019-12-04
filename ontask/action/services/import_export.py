# -*- coding: utf-8 -*-

"""Service for action import."""
import gzip
from typing import List

from django.utils.translation import ugettext_lazy as _
from rest_framework.parsers import JSONParser

from ontask import models
from ontask.action import serializers


def do_import_action(
    user,
    workflow: models.Workflow,
    file_item,
) -> List[models.Action]:
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
    action_data = serializers.ActionSelfcontainedSerializer(
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
        action.log(user, models.Log.ACTION_IMPORT)

    return actions
