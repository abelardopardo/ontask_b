# -*- coding: utf-8 -*-

"""Service for action import."""
import gzip
from typing import List

from django.utils.translation import ugettext_lazy as _
from rest_framework.parsers import JSONParser

from ontask import models
from ontask.action import serializers


def run_compatibility_patches(json_data: List) -> List:
    """Patch list of actions to make it compatible.

    1. Change action.target_url from None to ''

    2. Extract filters from the conditions array and put it in its own array

    3. Remove spurious "filter": {} in the action object

    :param json_data: List of actions to process
    :return: Modified json_data
    """
    for action_obj in json_data:
        # Target_url field in actions should be present an empty by default
        if action_obj.get('target_url') is None:
            action_obj['target_url'] = ''

        # If filter is None, should be empty
        f_obj = action_obj.get('filter', None)
        if f_obj == {} or f_obj == []:
            action_obj.pop('filter')
            f_obj = None

        # If it is a single element list, replace by single element
        if isinstance(f_obj, List):
            action_obj['filter'] = f_obj[0]

        # Remove columns field
        action_obj.pop('columns', None)

        action_type = action_obj.get('action_type')
        is_out = action_obj.pop('is_out', True)
        if not action_type:
            if is_out:
                action_type = models.Action.PERSONALIZED_TEXT
            else:
                action_type = models.Action.SURVEY
            action_obj['action_type'] = action_type

        # Replace content field (if it exists, with text_content)
        action_obj['text_content'] = action_obj.get(
            'content',
            action_obj.get('text_content'))

    # move filter condition to its own list
    for action_obj in json_data:
        conditions = action_obj.get('conditions')
        if not conditions:
            continue

        action_obj['conditions'] = [
            cond for cond in conditions if not cond.get('is_filter', False)]

        filter_obj = [
            cond for cond in conditions if cond.get('is_filter', False)]
        if not filter_obj:
            continue

        action_obj['filter'] = filter_obj[0]

    # move filter condition to its own list
    for action_obj in json_data:
        conditions = action_obj.get('conditions')
        for cond in conditions:
            if '_formula' not in cond:
                cond['_formula'] = cond.pop('formula')
            if '_formula_text' not in cond:
                cond['_formula_text'] = cond.pop('formula_text', None)

        filter_obj = action_obj.get('filter')
        if filter_obj and '_formula' not in filter_obj:
            filter_obj['_formula'] = filter_obj.pop('formula')

    return json_data


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
            _('Incorrect file. Expecting a GZIP file (exported action).'),
        )

    run_compatibility_patches(parsed_data)

    # Serialize content
    action_data = serializers.ActionSelfcontainedSerializer(
        data=parsed_data,
        many=True,
        context={'user': user, 'workflow': workflow})

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
