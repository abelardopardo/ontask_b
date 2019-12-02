# -*- coding: utf-8 -*-

"""API functions."""
from rest_framework import generics

from ontask import models
from ontask.core.permissions import UserIsInstructor
from ontask.logs.serializers import LogSerializer


class LogAPIList(generics.ListAPIView):
    """Get a list of the available workflows and allow creation."""

    queryset = None  # Needs to be overwritten

    serializer_class = LogSerializer

    permission_classes = (UserIsInstructor,)

    # Filter the workflows only for the current user.
    def get_queryset(self):
        """Get the queryset.

        :return:
        """
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return models.Log.objects.all()

        return models.Log.objects.filter(user=self.request.user)
