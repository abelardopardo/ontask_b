# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from rest_framework import generics

from ontask.permissions import UserIsInstructor
from ontask.permissions import IsOwner, UserIsInstructor
from .models import Workflow
from .serializers import WorkflowSerializer


class WorkflowAPIListCreate(generics.ListCreateAPIView, UserIsInstructor):
    """
    get:
    Return a list of available workflows

    post:
    Create a new workflow given name, description and attributes
    """

    queryset = None  # Needs to be overwritten
    serializer_class = WorkflowSerializer

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return Workflow.objects.all()

        return Workflow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkflowAPIRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView,
                                       UserIsInstructor):
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
    serializer_class = WorkflowSerializer

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return Workflow.objects.all()

        return Workflow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(user=self.request.user)
