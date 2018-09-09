# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import permissions

group_names = ['student',
               'instructor']

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Access only allowed to the "user" field of the object.
        return obj.user == request.user


def is_instructor(user):
    """
    @DynamicAttrs
    Check if the user is authenticated and belongs to the instructor group
    :param user: User object
    :return: Boolean stating if user belongs to the group
    """
    return user.is_authenticated and \
           (user.groups.filter(name='instructor').exists() or user.is_superuser)


def is_admin(user):
    """
    @DynamicAttrs
    Check if the user is authenticated and is supergroup
    :param user: User object
    :return: Boolean stating if user is admin
    """
    return user.is_authenticated and user.is_superuser


class UserIsInstructor(UserPassesTestMixin, permissions.BasePermission):
    """
    @DynamicAttrs
    Class to use in the Views so that only users that are instructors are
    allowed to access
    """

    def test_func(self):
        return is_instructor(self.request.user)

    def has_permission(self, request, view):
        return is_instructor(request.user)

    def has_object_permission(self, request, view, obj):
        del view, obj
        return is_instructor(request.user)
