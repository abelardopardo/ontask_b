"""Configuration for production."""
import logging.config

from settings.base import *  # NOQA

# Security features
# -----------------------------------------------------------------------------
MIDDLEWARE += ['django.middleware.security.SecurityMiddleware']
if USE_SSL:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_BROWSER_XSS_FILTER = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader'])]

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

LOGGING['loggers'] = {
    'django': {
        'handlers': ['django_log_file'],
        'propagate': False,
        'level': 'ERROR',
    },
    'ontask': {
        'handlers': ['ontask_log_file'],
        'propagate': False,
        'level': 'ERROR',
    },
    'scripts': {
        'handlers': ['script_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'celery_execution': {
        'handlers': ['celery_log_file'],
        'propagate': False,
        'level': 'ERROR',
    },
    'django.security.DisallowedHost': {
        'handlers': ['ontask_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'ontask.django_auth_lti.backends': {
        'handlers': ['ontask_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'ontask.django_auth_lti.middleware_patched': {
        'handlers': ['ontask_log_file'],
        'propagate': False,
        'level': 'DEBUG'}}

logging.config.dictConfig(LOGGING)
