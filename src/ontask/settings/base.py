"""
Django settings for ontask project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import environ
import os

from django.core.urlresolvers import reverse_lazy
from os.path import dirname, join, exists
from django.contrib import messages

# Build paths inside the project like this: join(BASE_DIR, "directory")
BASE_DIR = dirname(dirname(dirname(__file__)))
STATICFILES_DIRS = [join(BASE_DIR, 'static')]
MEDIA_ROOT = join(BASE_DIR, 'media')
MEDIA_URL = "/media/"
ONTASK_HELP_URL = "html/index.html"

# Project root folder
PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
            # insert more TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'ontask.context_processors.conf_to_context',
            ],
            'libraries': {
                'settings': 'ontask.templatetags.settings',
            }
        },
    },
]

# Use 12factor inspired environment variables or from a file
env = environ.Env(LTI_OAUTH_CREDENTIALS=(dict, {}))

# Ideally move env file should be outside the git repo
# i.e. BASE_DIR.parent.parent
env_file = join(dirname(__file__), 'local.env')
if exists(env_file):
    environ.Env.read_env(str(env_file))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django_extensions',
    'django.contrib.auth',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'authtools',
    'crispy_forms',
    'easy_thumbnails',
    'widget_tweaks',
    'formtools',
    'siteprefs',
    'django_tables2',
    'import_export',
    'rest_framework',
    'rest_framework.authtoken',
    'django_summernote',
    'jquery',
    'django_auth_lti',
    'datetimewidget',

    'core.apps.CoreConfig',
    'profiles.apps.ProfileConfig',
    'accounts',
    'workflow.apps.WorkflowConfig',
    'dataops.apps.DataopsConfig',
    'table.apps.TableConfig',
    'action.apps.ActionConfig',
    'logs.apps.LogsConfig',
    'scheduler.apps.SchedulerConfig',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware'
)

AUTHENTICATION_BACKENDS = [
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend'
]

LTI_OAUTH_CREDENTIALS = env('LTI_OAUTH_CREDENTIALS')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": 1800,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "ontask"
    }
}
# Cache time to live is 15 minutes
CACHE_TTL = 60 * 30
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800  # set just 30 mins
SESSION_SAVE_EVERY_REQUEST = True  # Needed to make sure timeout above works
X_FRAME_OPTIONS = 'SAMEORIGIN'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    # ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # )
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

ROOT_URLCONF = 'ontask.urls'

WSGI_APPLICATION = 'ontask.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in
    # os.environ
    'default': env.db(),
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('TIME_ZONE')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

# Crispy Form Theme - Bootstrap 3
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# For Bootstrap 3, change error alert to 'danger'
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'
LOGIN_REDIRECT_URL = reverse_lazy("profiles:show_self")
LOGIN_URL = reverse_lazy("accounts:login")

THUMBNAIL_EXTENSION = 'png'     # Or any extn for your thumbnails

IMPORT_EXPORT_USE_TRANSACTIONS = True

SITE_ID = 1

SUMMERNOTE_CONFIG = {
    'width': '100%',
    'height': '400px',
    'css': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/base16-dark.min.css',
    ),
    'css_for_inplace': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/base16-dark.min.css',
    ),
    'codemirror': {
        'theme': 'base16-dark',
        'mode': 'htmlmixed',
        'lineNumbers': 'true',
        'lineWrapping': 'true',
    },
    'lazy': True,
}

# Extra configuration options
DATAOPS_CONTENT_TYPES = '["text/csv", "application/json", "application/gzip", "application/x-gzip"]'
DATAOPS_MAX_UPLOAD_SIZE = 209715200  # 200 MB

# Email configuration
EMAIL_ACTION_EMAIL_HOST = ''
EMAIL_ACTION_EMAIL_PORT = ''
EMAIL_ACTION_EMAIL_HOST_USER = ''
EMAIL_ACTION_EMAIL_HOST_PASSWORD = ''
EMAIL_ACTION_EMAIL_USE_TLS = ''
EMAIL_ACTION_EMAIL_USE_SSL = ''
EMAIL_ACTION_NOTIFICATION_TEMPLATE = """
<html>
<head/>
<body>
<p>Dear {{ user.name }}</p>

<p>This message is to inform you that on {{ email_sent_datetime }} a total of 
{{ num_messages }} emails were sent after the user {{ user.email }} executed 
the action with name  "{{ action.name }}".</p> 

{% if filter_present %}
<p>The action had a filter that reduced the number of messages from 
{{ num_rows }} to {{ num_selected }}.</p> 
{% else %}
<p>All the data rows stored in the workflow were used.</p>
{% endif %}

Regards.
The OnTask Support Team
</body>
</html>
"""
EMAIL_ACTION_NOTIFICATION_SUBJECT = "OnTask: Action executed"
EMAIL_ACTION_NOTIFICATION_SENDER = 'ontask@ontasklearning.org'
EMAIL_ACTION_PIXEL = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGP6zwAAAgcBApocMXEAAAAASUVORK5CYII='

LOGS_MAX_LIST_SIZE = 200

SHORT_DATETIME_FORMAT = 'r'
