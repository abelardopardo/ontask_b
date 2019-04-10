# -*- coding: utf-8 -*-


from rest_framework import generics

from ontask.permissions import UserIsInstructor
from .models import Log
from .serializers import LogSerializer


class LogAPIList(generics.ListAPIView):
    """
    Get a list of the available workflows and allow creation
    """

    queryset = None  # Needs to be overwritten
    serializer_class = LogSerializer
    permission_classes = (UserIsInstructor,)

    # Filter the workflows only for the current user.
    def get_queryset(self):
        # Admin get to see all of them
        if self.request.user.is_superuser:
            return Log.objects.all()

        return Log.objects.filter(user=self.request.user)
