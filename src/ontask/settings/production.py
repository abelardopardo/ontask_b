# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging.config

from .base import *  # NOQA

# In production set the environment variable like this:
#    DJANGO_SETTINGS_MODULE=ontask.settings.production

# For security and performance reasons, DEBUG is turned off
DEBUG = False
TEMPLATE_DEBUG = False

# Must mention ALLOWED_HOSTS in production!
ALLOWED_HOSTS = [os.environ['DOMAIN_NAME']]

# Additional middleware introduced by debug toolbar
MIDDLEWARE_CLASSES += (
   'django.middleware.security.SecurityMiddleware',)

#
# Security features
#
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

#
# Folder to scan for plugins
#
DATAOPS_PLUGIN_DIRECTORY = os.path.join(PROJECT_PATH, 'plugins')

# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

# Define STATIC_ROOT for the collectstatic command
STATIC_ROOT = join(BASE_DIR(), '..', 'site', 'static')

# Log everything to the logs directory at the top
LOGFILE_ROOT = join(dirname(BASE_DIR()), 'logs')

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
        'proj_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOGFILE_ROOT, 'project.log'),
            'formatter': 'verbose'
        },
        'script_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOGFILE_ROOT, 'script.log'),
            'formatter': 'verbose'
        },
        'scheduler_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOGFILE_ROOT, 'scheduler.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'project': {
            'handlers': ['proj_log_file'],
            'level': 'DEBUG',
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
        'scripts.scheduler': {
            'handlers': ['scheduler_log_file'],
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
