# -*- coding: utf-8 -*-

"""Basic functions and classes to check for permissions."""

from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import permissions

group_names = [
    'student',
    'instructor']


class IsOwner(permissions.BasePermission):
    """Custom permission to only allow owners of an object to access it."""

    def has_object_permission(self, request, view, obj):
        """Check if obj.user and request user are the same."""
        # Access only allowed to the "user" field of the object.
        return obj.user == request.user


def is_instructor(user):
    """Check if the user is authenticated and belongs to the instructor group.

    @DynamicAttrs

    :param user: User object

    :return: Boolean stating if user belongs to the group
    """
    return (
        user.is_authenticated
        and (
            user.groups.filter(name='instructor').exists()
            or user.is_superuser
        )
    )


def is_admin(user):
    """Check if the user is authenticated and is supergroup.

    @DynamicAttrs

    :param user: User object

    :return: Boolean stating if user is admin
    """
    return user.is_authenticated and user.is_superuser


def has_access(user, workflow):
    """Calculate if user has access to workflow.

    :param user: User object

    :param workflow: Workflow object

    :return: True if it is owner or in the shared list
    """
    return workflow.user == user or user in workflow.shared.all()


class UserIsInstructor(UserPassesTestMixin, permissions.BasePermission):
    """Use in views to allow only instructors to access.

    @DynamicAttrs
    """

    def test_func(self):
        """Overwrite the user passes test mixing function."""
        return is_instructor(self.request.user)

    def has_permission(self, request, view):
        """Equivalent to has permission."""
        return is_instructor(request.user)

    def has_object_permission(self, request, view, obj_param):
        """Simply check if it is instructor."""
        del view, obj_param
        return is_instructor(request.user)
