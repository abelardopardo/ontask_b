# -*- coding: utf-8 -*-

"""Methods to implement the API entry points."""
from django.db.models import Q
from rest_framework import generics

from ontask import models
from ontask.core.permissions import UserIsInstructor
from ontask.scheduler.serializers import (
    ScheduledEmailSerializer, ScheduledJSONSerializer,
)


class ScheduledOperationAPIListCreate(generics.ListCreateAPIView):
    """Class to operate through the list of actions scheduled for a user.

    get: Return the list of scheduled actions

    post: Create a new scheduled action with the given parameters
    """

    queryset = None
    permission_classes = (UserIsInstructor,)

    def get_queryset(self):
        """Filter the Scheduled operations only for the current user."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.ScheduledOperation.objects.all()

        return models.ScheduledOperation.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """Create the operation."""
        if self.request.user.is_superuser:
            # Superuser is allowed to create ScheduledOperations for any user
            serializer.save()
        else:
            serializer.save(user=self.request.user)


class ScheduledOperationAPIRetrieveUpdateDestroy(
    generics.RetrieveUpdateDestroyAPIView
):
    """Retrieve and update existing scheduled operations

    get: Returns the information for one of the scheduled actions

    put: Modifies the scheduled action with the information included in the request
    (all fields are overwritten)

    delete: Delete the scheduled action.
    """

    queryset = None  # Needs to be overwritten
    permission_classes = (UserIsInstructor,)

    def perform_create(self, serializer):
        """Create operation."""
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(
                Q(user=self.request.user) | Q(shared=self.request.user)
            )


class ScheduledOperationEmailAPIListCreate(ScheduledOperationAPIListCreate):
    """
    get: Return the list of scheduled actions

    post: Create a new scheduled action with the given parameters
    """

    serializer_class = ScheduledEmailSerializer

    def get_queryset(self):
        """Filter the workflows only for the current user."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.ScheduledOperation.objects.filter(
                action__action_type=models.Action.PERSONALIZED_TEXT
            )

        return models.ScheduledOperation.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=models.Action.PERSONALIZED_TEXT
        ).distinct()


class ScheduledOperationJSONAPIListCreate(ScheduledOperationAPIListCreate):
    """
    get: Return the list of scheduled actions

    post: Create a new scheduled action with the given parameters
    """

    serializer_class = ScheduledJSONSerializer

    def get_queryset(self):
        """Filter the workflows only for the current user."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.ScheduledOperation.objects.filter(
                action__action_type=models.Action.PERSONALIZED_JSON
            )

        return models.ScheduledOperation.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=models.Action.PERSONALIZED_JSON
        ).distinct()


class ScheduledEmailAPIRetrieveUpdateDestroy(
    ScheduledOperationAPIRetrieveUpdateDestroy
):
    """
    get:
    Returns the information for one of the scheduled actions

    put:
    Modifies the scheduled action with the information included in the request
    (all fields are overwritten)

    delete:
    Delete the scheduling
    """

    serializer_class = ScheduledEmailSerializer

    def get_queryset(self):
        """Filter the operations only for the current user."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.ScheduledOperation.objects.filter(
                action__action_type=models.Action.PERSONALIZED_TEXT
            )

        return models.ScheduledOperation.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=models.Action.PERSONALIZED_TEXT
        ).distinct()


class ScheduledJSONAPIRetrieveUpdateDestroy(
    ScheduledOperationAPIRetrieveUpdateDestroy
):
    """
    get:
    Returns the information for one of the scheduled actions

    put:
    Modifies the scheduled action with the information included in the request
    (all fields are overwritten)

    delete:
    Delete the scheduling
    """

    serializer_class = ScheduledJSONSerializer

    def get_queryset(self):
        """Filter the requested operations."""
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.ScheduledOperation.objects.filter(
                action__action_type=models.Action.PERSONALIZED_JSON
            )

        return models.ScheduledOperation.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=models.Action.PERSONALIZED_JSON
        ).distinct()
