# -*- coding: utf-8 -*-

from rest_framework import generics, status

from django.db.models import Q
from ontask.permissions import UserIsInstructor
from scheduler.models import ScheduledAction
from scheduler.serializers import ScheduledEmailSerializer, \
    ScheduledJSONSerializer

from action.models import Action


class ScheduledActionAPIListCreate(generics.ListCreateAPIView):
    """
    get:
    Return the list of scheduled actions

    post:
    Create a new scheduled action with the given parameters
    """

    queryset = None
    permission_classes = (UserIsInstructor,)

    # Filter the Scheduled actions only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return ScheduledAction.objects.all()

        return ScheduledAction.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # Superuser is allowed to create ScheduledActions for any user
            serializer.save()
        else:
            serializer.save(user=self.request.user)


class ScheduledActionAPIRetrieveUpdateDestroy(
    generics.RetrieveUpdateDestroyAPIView
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

    queryset = None  # Needs to be overwritten
    permission_classes = (UserIsInstructor,)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # Superuser is allowed to create workflows for any user
            serializer.save()
        else:
            serializer.save(
                Q(user=self.request.user) | Q(shared=self.request.user)
            )


class ScheduledActionEmailAPIListCreate(ScheduledActionAPIListCreate):
    """
    get:
    Return the list of scheduled actions

    post:
    Create a new scheduled action with the given parameters
    """

    serializer_class = ScheduledEmailSerializer

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return ScheduledAction.objects.filter(
                action__action_type=Action.PERSONALIZED_TEXT
            )

        return ScheduledAction.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=Action.PERSONALIZED_TEXT
        ).distinct()


class ScheduledActionJSONAPIListCreate(ScheduledActionAPIListCreate):
    """
    get:
    Return the list of scheduled actions

    post:
    Create a new scheduled action with the given parameters
    """

    serializer_class = ScheduledJSONSerializer

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return ScheduledAction.objects.filter(
                action__action_type=Action.PERSONALIZED_JSON
            )

        return ScheduledAction.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=Action.PERSONALIZED_JSON
        ).distinct()


class ScheduledEmailAPIRetrieveUpdateDestroy(
    ScheduledActionAPIRetrieveUpdateDestroy
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

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return ScheduledAction.objects.filter(
                action__action_type=Action.PERSONALIZED_TEXT
            )

        return ScheduledAction.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=Action.PERSONALIZED_TEXT
        ).distinct()


class ScheduledJSONAPIRetrieveUpdateDestroy(
    ScheduledActionAPIRetrieveUpdateDestroy
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

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return ScheduledAction.objects.filter(
                action__action_type=Action.PERSONALIZED_JSON
            )

        return ScheduledAction.objects.filter(
            Q(user=self.request.user) |
            Q(action__workflow__shared=self.request.user)
        ).filter(
            action__action_type=Action.PERSONALIZED_JSON
        ).distinct()
