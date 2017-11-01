# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from ontask.permissions import IsOwner, UserIsInstructor
from .models import Workflow
from .serializers import WorkflowSerializer


class WorkflowAPIListCreate(UserIsInstructor, generics.ListCreateAPIView):
    """
    Get a list of the available workflows and allow creation
    """

    queryset = None  # Needs to be overwritten
    serializer_class = WorkflowSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsOwner)

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


class WorkflowAPIRetrieveUpdateDestroy(UserIsInstructor,
                                       generics.RetrieveUpdateDestroyAPIView):
    queryset = None  # Needs to be overwritten
    serializer_class = WorkflowSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsOwner)

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
