"""API classes to manipulate workflows."""
from typing import Optional

from django import http
from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ontask import models
from ontask.core import UserIsInstructor, get_workflow
from ontask.workflow.serializers import (
    WorkflowListSerializer, WorkflowLockSerializer,
)


class WorkflowAPIListCreate(generics.ListCreateAPIView):
    """Access the workflow.

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
        """Access the required workflow."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.Workflow.objects.all()

        return models.Workflow.objects.filter(
            Q(user=self.request.user) | Q(shared=self.request.user),
        ).distinct()

    def perform_create(self, serializer):
        """Create the new workflow."""
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(user=self.request.user)


class WorkflowAPIRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """API to manage workflow operations.

    get: Returns the information stored for the workflow

    put: Modifies the workflow with the information included in the request
    (all fields are overwritten)

    patch: Update only the given fields in the workshop (the rest remain
    unchanged)

    delete:
    Delete the workflow
    """

    queryset = None  # Needs to be overwritten

    serializer_class = WorkflowListSerializer

    permission_classes = (UserIsInstructor,)

    # Filter the workflows only for the current user.
    def get_queryset(self):
        """Access the relevant workflow."""
        if self.request.user.is_superuser:
            return models.Workflow.objects.all()

        return models.Workflow.objects.filter(
            Q(user=self.request.user) | Q(shared=self.request.user),
        ).distinct()

    def perform_create(self, serializer):
        """Create the workflow element."""
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(
                Q(user=self.request.user) | Q(shared=self.request.user),
            )


class WorkflowAPILock(APIView):
    """Information stating if the workflow is locked.

    get: return information about the workflow

    post: Tries to lock the workflow

    delete: unlock the workflow
    """

    serializer_class = WorkflowLockSerializer

    permission_classes = (UserIsInstructor,)

    @method_decorator(get_workflow(pf_related='columns'))
    def get(
        self,
        request: http.HttpRequest,
        pk: int,
        format=None,    # noqa: 132
        workflow: Optional[models.Workflow] = None,
    ) -> http.HttpResponse:
        """Return the serialized value of the lock property in the wflow."""
        del request, pk, format
        serializer = self.serializer_class({'lock': workflow.is_locked()})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(get_workflow(pf_related='columns'))
    def post(
        self,
        request: http.HttpRequest,
        pk: int,
        format=None,    # noqa: 132
        workflow: Optional[models.Workflow] = None,
    ) -> http.HttpResponse:
        """Set the lock for a workflow."""
        del request, pk, format, workflow
        return Response(status=status.HTTP_201_CREATED)

    @method_decorator(get_workflow(pf_related='columns'))
    def delete(
        self,
        request: http.HttpRequest,
        pk: int,
        format=None,  # noqa: 132
        workflow: Optional[models.Workflow] = None,
    ) -> http.HttpResponse:
        """Remove the lock in a workflow."""
        del request, pk, format
        workflow.unlock()
        return Response(status=status.HTTP_200_OK)
