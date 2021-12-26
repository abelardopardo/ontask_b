# -*- coding: utf-8 -*-

"""Decorator to require an LTI role."""
from functools import wraps
from typing import Callable, List, Optional

from django.shortcuts import redirect
from django.urls import reverse_lazy

from ontask.django_auth_lti.verification import is_allowed


def lti_role_required(
    allowed_roles: List[str],
    redirect_url: str = reverse_lazy('not_authorized'),
    raise_exception: Optional[bool] = False,
) -> Callable:
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if is_allowed(request, allowed_roles, raise_exception):
                return view_func(request, *args, **kwargs)

            return redirect(redirect_url)

        return _wrapped_view

    return decorator
