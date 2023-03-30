# -*- coding: utf-8 -*-

import logging.config

from settings.base import *  # NOQA

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
if "celery" in sys.argv[0]:
    DEBUG = False
else:
    print('Forcing synchronous execution in Celery')
    CELERY_TASK_ALWAYS_EAGER = True

# Django Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    TEMPLATES[0]['OPTIONS']['debug'] = True

if ONTASK_TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    ONTASK_FIXTURE_DIR = os.path.join(BASE_DIR, 'ontask', 'tests', 'fixtures')
    FIXTURE_DIRS = [
        os.path.join(BASE_DIR, 'ontask', 'tests', 'initial_workflow'),
        ONTASK_FIXTURE_DIR]
    EXECUTE_ACTION_JSON_TRANSFER = False
else:
    # Show emails to console in DEBUG mode
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda r: True,  # enables it
        # '...
    }

# Additional middleware introduced by debug toolbar
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Show thumbnail generation errors
THUMBNAIL_DEBUG = True

# Allow internal IPs for debugging
INTERNAL_IPS = ['127.0.0.1', '0.0.0.1', 'localhost']

LOGGING['loggers'] = {
    'django': {
        'handlers': ['django_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'ontask': {
        'handlers': ['django_log_file'],
        'level': 'DEBUG',
    },
    'scripts': {
        'handlers': ['script_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'celery_execution': {
        'handlers': ['celery_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'django.security.DisallowedHost': {
        'handlers': ['django_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'ontask.django_auth_lti.backends': {
        'handlers': ['django_log_file'],
        'propagate': False,
        'level': 'DEBUG',
    },
    'ontask.django_auth_lti.middleware_patched': {
        'handlers': ['django_log_file'],
        'propagate': False,
        'level': 'DEBUG'}}

logging.config.dictConfig(LOGGING)

GRAPH_MODELS = {
    'group_models': True,
    'all_applications': True,
    'output': 'data_model.png',
    'exclude_models': [
        'TaskResult',
        'SQLConnection',
        'Plugin',
        'Site',
        'ThumbnailDimensions',
        'Thumbnail',
        'Source',
        'File',
        'Preference',
        'PeriodicTask',
        'PeriodicTasks',
        'IntervalSchedule',
        'CrontabSchedule',
        'SolarSchedule',
        'Attachment',
        'AbstractAttachment',
        'Session',
        'AbstractBaseSession',
        'Profile',
        'BaseProfile',
        'Token',
        'LogEntry',
        'Group',
        'Permission',
        'ContentType'
    ]
}

show_configuration()
