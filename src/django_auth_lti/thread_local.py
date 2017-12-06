"""
Allow for setting/getting of the current request in thread local
"""
import threading


_thread_local = threading.local()


def set_current_request(request):
    setattr(_thread_local, 'request', request)


def get_current_request():
    return getattr(_thread_local, 'request', None)
