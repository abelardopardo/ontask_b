# -*- coding: utf-8 -*-
"""
File with auxiliary operations needed to handle OAuth2 authentication for Canvas
"""
from __future__ import unicode_literals, print_function


class RefreshCanvasTokenException(Exception):
    pass

class CanvasOAuthMiddleware(object):
    """
    Class to catch exceptions when a call to the API does not have a valid
    token and deal with it by requesting a refresh token
    """

    def process_exception(self, request, exception):
        if isinstance(exception, RefreshCanvasTokenException):
            return refresh_token(request)
        raise exception


def refresh_token(request):
    pass
