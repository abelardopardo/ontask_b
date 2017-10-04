# -*- coding: UTF-8 -*-#
from __future__ import print_function

from rest_framework import serializers

from .models import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ('pk', 'user', 'name', 'description_text')

# from workflow.models import Workflow
# from workflow.serializers import WorkflowSerializer, WorkflowSerializerM
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# from django.utils.six import BytesIO
#
# w1 = Workflow.objects.all()[0]
# w2 = Workflow.objects.all()[1]
# s1 = WorkflowSerializer(w1)
# s2 = WorkflowSerializer(w2)
# s3 = WorkflowSerializer([w1, w2], many=True)