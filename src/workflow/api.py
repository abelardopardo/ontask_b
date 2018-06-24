# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from ontask.permissions import UserIsInstructor
from .models import Workflow
from .ops import get_workflow
from .serializers import WorkflowListSerializer, WorkflowLockSerializer


class WorkflowAPIListCreate(generics.ListCreateAPIView):
    """
    get:
    Return a list of available workflows

    post:
    Create a new workflow given name, description and attributes
    """

    queryset = None  # Needs to be overwritten
    serializer_class = WorkflowListSerializer
    permission_classes = (UserIsInstructor,)

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return Workflow.objects.all()

        return Workflow.objects.filter(
            Q(user=self.request.user) | Q(shared=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(user=self.request.user)


class WorkflowAPIRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Returns the information stored for the workflow

    put:
    Modifies the workflow with the information included in the request (all
    fields are overwritten)

    patch:
    Update only the given fields in the workshop (the rest remain unchanged)

    delete:
    Delete the workflow
    """
    queryset = None  # Needs to be overwritten
    serializer_class = WorkflowListSerializer
    permission_classes = (UserIsInstructor,)

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return Workflow.objects.all()

        return Workflow.objects.filter(
            Q(user=self.request.user) | Q(shared=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(
                Q(user=self.request.user) | Q(shared=self.request.user)
            )


class WorkflowAPILock(APIView):
    """
    get:
    Returns the information stating if the workflow is locked

    post:
    Tries to lock the workflow

    delete:
    unlock the workflow
    """

    serializer_class = WorkflowLockSerializer
    permission_classes = (UserIsInstructor,)

    def get_object(self, pk):
        try:
            if self.request.user.is_superuser:
                workflow = Workflow.objects.get(pk=pk)
            else:
                workflow = Workflow.objects.filter(
                    Q(user=self.request.user) |
                    Q(shared__id=self.request.user.id)
                ).distinct().get(id=pk)
        except Workflow.DoesNotExist:
            raise APIException('Incorrect object')

        return workflow

    # Retrieve the value of the lock property in the workflow
    def get(self, request, pk, format=None):
        # Retrieve the workflow and return the serialized value of the boolean
        workflow = self.get_object(pk)
        serializer = self.serializer_class({'lock': workflow.is_locked()})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create: Try to set the value of the workflow
    def post(self, request, pk, format=None):
        workflow = get_workflow(request, pk)
        if not workflow:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    # Delete
    def delete(self, request, pk, format=None):
        workflow = self.get_object(pk)
        workflow.unlock()
        return Response(status=status.HTTP_200_OK)
