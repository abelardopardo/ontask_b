from functools import wraps
from django.utils.decorators import available_attrs
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django_auth_lti.verification import is_allowed


def lti_role_required(allowed_roles,
                      redirect_url=reverse_lazy('not_authorized'),
                      raise_exception=False):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if is_allowed(request, allowed_roles, raise_exception):
                return view_func(request, *args, **kwargs)
            
            return redirect(redirect_url)
        return _wrapped_view
    return decorator
