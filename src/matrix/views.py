# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, reverse, render
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes


from dataops import panda_db
from workflow.models import Workflow
from .serializers import MatrixCellSerializer


# @api_view(['POST'])
@csrf_exempt
def getpost_cell(request, pk):
    # Method to GET (read) or POST (update) a cell in the workflow

    # Get the corresponding workflow
    workflow = get_object_or_404(Workflow, pk=pk)

    # Get the data travelling with the request
    serializer = MatrixCellSerializer(data=JSONParser().parse(request))
    if serializer.is_valid():

        # The matrix cell specification
        mcell = serializer.validated_data

        # The given unique_name must be a unique key
        column_names = json.loads(workflow.column_names)
        column_unique = json.loads(workflow.column_unique)
        unique_col_names = [n for x, n in enumerate(column_names)
                            if column_unique[x]]

        if mcell['uni_triplet']['name'] not in unique_col_names:
            return JsonResponse(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        result = panda_db.get_matrix_cell(pk, mcell)

        if result is not None:
            serializer.instance.cell_value = result
            return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)

    # Return error
    return JsonResponse(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
