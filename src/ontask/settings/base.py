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
            ],
            'libraries': {
                'settings': 'ontask.templatetags.settings',
            }
        },
    },
]

# Use 12factor inspired environment variables or from a file
env = environ.Env()

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
    'django_summernote',
    'jquery',

    'profiles.apps.ProfileConfig',
    'accounts',
    'workflow.apps.WorkflowConfig',
    'dataops.apps.DataopsConfig',
    'matrix.apps.MatrixConfig',
    'action.apps.ActionConfig',
    'email_action.apps.EmailActionConfig',
    'logs.apps.LogsConfig',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend'
]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800  # set just 30 mins
SESSION_SAVE_EVERY_REQUEST = True  # Needed to make sure timeout above works

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    # ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # )
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

# PANDAS_RENDERERS = [
#     "rest_pandas.renderers.PandasJSONRenderer",
#     "rest_pandas.renderers.PandasCSVRenderer",
#     "rest_pandas.renderers.PandasTextRenderer",
#     "rest_pandas.renderers.PandasExcelRenderer",
#     "rest_pandas.renderers.PandasOldExcelRenderer",
#     "rest_pandas.renderers.PandasPNGRenderer",
#     "rest_pandas.renderers.PandasSVGRenderer",
# ]

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

#
# Auxiliary variables
#
if DATABASES['default']['ENGINE'].find('postgresql') != -1:
    DATABASE_TYPE = 'postgresql'
elif DATABASES['default']['ENGINE'].find('sqlite') != -1:
    DATABASE_TYPE = 'sqlite'

# SUMMERNOTE_CONFIG = {
#     # Using SummernoteWidget - iframe mode
#     'iframe': False,  # or set False to use SummernoteInplaceWidget - no iframe
#     # mode
#
#     # Using Summernote Air-mode
#     'airMode': False,
#
#     # Use native HTML tags (`<b>`, `<i>`, ...) instead of style attributes
#     # (Firefox, Chrome only)
#     'styleWithTags': True,
#
#     # Set text direction : 'left to right' is default.
#     'direction': 'ltr',
#
#     # Change editor size
#     # 'width': '100%',
#     # 'height': '480',
#
#     # Use proper language setting automatically (default)
#     'lang': None,
#
#     # Customize toolbar buttons
#     # 'toolbar': [
#     #     ['style', ['style']],
#     #     ['style', ['bold', 'italic', 'underline', 'clear']],
#     #     ['para', ['ul', 'ol', 'height']],
#     #     ['insert', ['link']],
#     # ],
#
#     # Need authentication while uploading attachments.
#     'attachment_require_authentication': True,
#
#     # Set `upload_to` function for attachments.
#     # 'attachment_upload_to': my_custom_upload_to_func(),
#
#     # Set custom storage class for attachments.
#     # attachment_storage_class': 'my.custom.storage.class.name',
#
#     # Set custom model for attachments (default: 'django_summernote.Attachment')
#     # 'attachment_model': 'my.custom.attachment.model', # must inherit
#                                 # 'django_summernote.AbstractAttachment'
#
#     # Set common css/js media files
#     # 'base_css': (
#     #     '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
#     # ),
#     # 'base_js': (
#     #     '//code.jquery.com/jquery-1.9.1.min.js',
#     #     '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
#     # ),
#     'default_css': (
#         os.path.join(STATIC_URL, 'django_summernote/summernote.css'),
#         os.path.join(STATIC_URL, 'django_summernote/django_summernote.css'),
#     ),
#     'default_js': (
#         os.path.join(STATIC_URL,
#                      'django_summernote/jquery.ui.widget.js'),
#         os.path.join(STATIC_URL,
#                      'django_summernote/jquery.iframe-transport.js'),
#         os.path.join(STATIC_URL,
#                      'django_summernote/jquery.fileupload.js'),
#         os.path.join(STATIC_URL,
#                      'django_summernote/summernote.min.js'),
#     ),
#
#     # You can also add custom css/js for SummernoteInplaceWidget.
#     # !!! Be sure to put {{ form.media }} in template before initiate
#     # summernote.
#     'css_for_inplace': (
#     ),
#     'js_for_inplace': (
#     ),
#
#     # You can disable file upload feature.
#     'disable_upload': False,
#
#     # Codemirror as codeview
#     # If any codemirror settings are defined, it will include codemirror files
#     # automatically.
#     'css': {
#         '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css',
#     },
#     'codemirror': {
#         'mode': 'htmlmixed',
#         'lineNumbers': 'true',
#
#         # You have to include theme file in 'css' or 'css_for_inplace' before
#         # using it.
#         'theme': 'monokai',
#     },
#
#     # Lazy initialize
#     # If you want to initialize summernote at the bottom of page, set this as
#     # True and call `initSummernote()` on your page.
#     'lazy': True,
#
#     # To use external plugins,
#     # Include them within `css` and `js`.
#     # 'js': {
#     #     '/some_static_folder/summernote-ext-print.js',
#     #     '//somewhere_in_internet/summernote-plugin-name.js',
#     # },
#     # # You can also add custom settings in `summernote` section.
#     # 'summernote': {
#     #     'print': {
#     #         'stylesheetUrl': '/some_static_folder/printable.css',
#     #     },
#     # }
# }

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

LOGS_MAX_LIST_SIZE = 200

SHORT_DATETIME_FORMAT = 'r'
