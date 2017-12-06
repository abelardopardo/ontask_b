"""
Monkey-patch django's reverse function to add resource_link_id to all URLs.
"""
from urlparse import urlparse, urlunparse, parse_qs
from urllib import urlencode

from django.core import urlresolvers

from .thread_local import get_current_request

django_reverse = None


def reverse(*args, **kwargs):
    """
    Call django's reverse function and append the current resource_link_id as a
    query parameter

    :param kwargs['exclude_resource_link_id']: Do not add the resource link id
    as a query parameter
    :returns Django named url
    """
    request = get_current_request()

    # Check for custom exclude_resource_link_id kwarg and remove it before
    # passing kwargs to django reverse
    exclude_resource_link_id = kwargs.pop('exclude_resource_link_id', False)

    url = django_reverse(*args, **kwargs)
    if not exclude_resource_link_id:
        # Append resource_link_id query param if exclude_resource_link_id kwarg
        # was not passed or is False
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'resource_link_id' not in query.keys():
            query['resource_link_id'] = request.LTI.get('resource_link_id')
            url = urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                 urlencode(query), parsed.fragment)
            )
    return url


def patch_reverse():
    """
    Monkey-patches the reverse function. Will not patch twice.
    """
    global django_reverse
    if urlresolvers.reverse is not reverse:
        django_reverse = urlresolvers.reverse
        urlresolvers.reverse = reverse

        # Django 1.10 moves url helper functions like `reverse` into a new urls
        # module, so we need to patch it as well.  In addition, the
        # django.shortcuts module now includes `reverse` directly, and the
        # module appears to be loaded before middleware so we need to
        # retroactively patch that `reverse` reference as well.
        try:
            from django import urls, shortcuts
            urls.reverse = reverse
            shortcuts.reverse = reverse
        except ImportError:
            pass


# patch_reverse()
