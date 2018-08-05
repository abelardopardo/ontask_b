# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from django.conf import settings
from django.db import models

from workflow.models import Workflow


class Log(models.Model):
    """
    @DynamicAttrs

    Model to encode logs in OnTask
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Type of event logged see above
    name = models.CharField(max_length=256, blank=False)

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 on_delete=models.CASCADE,
                                 null=True)

    # JSON element with additional information
    # TODO: Change the model to include directly a JSON object, not this
    payload = models.CharField(max_length=65536,
                               default='',
                               null=False,
                               blank=False)

    def get_payload(self):
        """
        Function to access the payload information. If using a DB that
        supports JSON this function should be rewritten (to be transparent).
        :return: The JSON structure with the payload
        """

        if self.payload == '':
            return {}

        return json.loads(self.payload)

    def set_payload(self, payload):
        """
        Save the payload structure as text. If using a DB that supports JSON,
        this function should be rewritten.
        :return: Nothing.
        """

        self.payload = json.dumps(payload)

    def __unicode__(self):
        return '%s %s %s %s' % (self.user,
                                self.created,
                                self.name,
                                self.payload)

    @property
    def log_useremail(self):
        return self.user.email
