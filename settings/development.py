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

if ONTASK_TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    FIXTURE_DIRS = [os.path.join(BASE_DIR, 'test', 'initial_workflow')]
    EXECUTE_ACTION_JSON_TRANSFER = False
else:
    # Show emails to console in DEBUG mode
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

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

# Reset logging
# (see http://www.caktusgroup.com/blog/2015/01/27/Django-Logging-Configuration-logging_config-default-settings-logger/)
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
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_log_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ontask': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'scripts': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'celery_execution': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.security.DisallowedHost': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ontask.django_auth_lti.backends': {
            'handlers': ['ontask_log_file'],
            'level': 'DEBUG',
        },
        'ontask.django_auth_lti.middleware_patched': {
            'handlers': ['ontask_log_file'],
            'level': 'DEBUG',
        },
    }
}

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

dump_config()
