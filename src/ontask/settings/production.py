# -*- coding: utf-8 -*-

import logging.config

from ontask.settings.base import *  # NOQA

# Show emails to console
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

################################################################################
#
# Security features
#
################################################################################
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
        'django.template.loaders.app_directories.Loader',
    ]),
]

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

# Reset logging
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOG_FOLDER, 'django.log'),
            'formatter': 'verbose'
        },
        'ontask_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOG_FOLDER, 'ontask.log'),
            'formatter': 'verbose'
        },
        'script_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOG_FOLDER, 'script.log'),
            'formatter': 'verbose'
        },
        'celery_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOG_FOLDER, 'celery.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_log_file'],
            'propagate': True,
            'level': 'ERROR',
        },
        'ontask': {
            'handlers': ['ontask_log_file'],
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['proj_log_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'scripts': {
            'handlers': ['script_log_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'celery_execution': {
            'handlers': ['celery_log_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.security.DisallowedHost': {
            'handlers': ['proj_log_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django_auth_lti.backends': {
            'handlers': ['proj_log_file'],
            'level': 'DEBUG',
        },
        'django_auth_lti.middleware_patched': {
            'handlers': ['proj_log_file'],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(LOGGING)
