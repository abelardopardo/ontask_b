# -*- coding: utf-8 -*-

"""Django settings for ontask project."""
import json
import os
from os.path import dirname, exists, join
import sys

from celery.schedules import crontab
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import environ

# import ldap
# from django_auth_ldap.config import (
#     LDAPSearch,
#     GroupOfNamesType,
#     LDAPGroupQuery
# )

# Variables required to process configuration
BASE_DIR = environ.Path(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONTASK_TESTING = sys.argv[1:2] == ['test']

# Use 12factor inspired environment variables. Copy the variables from the os
# environment with a default value
env = environ.Env(
    ALLOWED_HOSTS=(list, os.environ.get('ALLOWED_HOSTS', ['*'])),

    AWS_ACCESS_KEY_ID=(str, os.environ.get('AWS_ACCESS_KEY_ID', '')),
    AWS_LOCATION=(str, os.environ.get('AWS_LOCATION', 'static')),
    AWS_SECRET_ACCESS_KEY=(str, os.environ.get('AWS_SECRET_ACCESS_KEY', '')),
    AWS_STORAGE_BUCKET_NAME=(
        str,
        os.environ.get('AWS_STORAGE_BUCKET_NAME', '')),

    BASE_URL=(str, os.environ.get('BASE_URL', '')),

    CANVAS_INFO_DICT=(str, os.environ.get('CANVAS_INFO_DICT', '{}')),
    CANVAS_TOKEN_EXPIRY_SLACK=(
        int,
        os.environ.get('CANVAS_TOKEN_EXPIRY_SLACK', 600)),

    DATABASE_URL=(str, os.environ.get('DATABASE_URL', '')),

    DATAOPS_MAX_UPLOAD_SIZE=(
        int,
        os.environ.get('DATAOPS_MAX_UPLOAD_SIZE', 209715200)),
    DATAOPS_PLUGIN_DIRECTORY=(
        str,
        os.environ.get(
            'DATAOPS_PLUGIN_DIRECTORY',
            join(BASE_DIR(), 'lib', 'plugins'))),

    DEBUG=(bool, os.environ.get('DEBUG', False)),

    EMAIL_BURST=(int, os.environ.get('EMAIL_BURST', 0)),
    EMAIL_BURST_PAUSE=(int, os.environ.get('EMAIL_BURST_PAUSE', 0)),
    EMAIL_HOST=(str, os.environ.get('EMAIL_HOST', '')),
    EMAIL_HOST_USER=(str, os.environ.get('EMAIL_HOST_USER', '')),
    EMAIL_HOST_PASSWORD=(str, os.environ.get('EMAIL_HOST_PASSWORD', '')),
    EMAIL_HTML_ONLY=(bool, os.environ.get('EMAIL_HTML_ONLY', True)),
    EMAIL_OVERRIDE_FROM=(str, os.environ.get('EMAIL_OVERRIDE_FROM', '')),
    EMAIL_PORT=(int, os.environ.get('EMAIL_PORT', None)),
    EMAIL_USE_SSL=(bool, os.environ.get('EMAIL_USE_SSL', False)),
    EMAIL_USE_TLS=(bool, os.environ.get('EMAIL_USE_TLS', False)),
    EMAIL_ACTION_NOTIFICATION_SENDER=(
        str,
        os.environ.get('EMAIL_ACTION_NOTIFICATION_SENDER', '')),

    EXECUTE_ACTION_JSON_TRANSFER=(
        bool,
        os.environ.get('EXECUTE_ACTION_JSON_TRANSFER', False)),

    ENV_FILENAME=(str, os.environ.get('ENV_FILENAME', 'local.env')),

    LANGUAGE_CODE=(str, os.environ.get('LANGUAGE_CODE', 'en-us')),

    LOG_FOLDER=(str, os.environ.get('LOG_FOLDER', 'logs')),

    LDAP_AUTH_SERVER_URI=(str, os.environ.get('LDAP_AUTH_SERVER_URI', '')),
    LDAP_AUTH_BIND_PASSWORD=(
        str,
        os.environ.get('LDAP_AUTH_BIND_PASSWORD', '')),

    LTI_OAUTH_CREDENTIALS=(
        dict,
        os.environ.get('LTI_OAUTH_CREDENTIALS', {})),
    LTI_INSTRUCTOR_GROUP_ROLES=(
        list,
        os.environ.get('LTI_INSTRUCTOR_GROUP_ROLES', ['Instructor'])),

    MEDIA_LOCATION=(str, os.environ.get('MEDIA_LOCATION', '/media/')),

    REDIS_URL=(
        str,
        os.environ.get(
            'REDIS_URL',
            'redis://localhost:6379/'
            + '?client_class=django_redis.client.DefaultClient'
            + '&timeout=1000'
            + '&key_prefix=ontask')),

    SECRET_KEY=(str, os.environ.get('SECRET_KEY', '')),

    SESSION_CLEANUP_CRONTAB=(
        str,
        os.environ.get('SESSION_CLEANUP_CRONTAB', '05 5 6 * *')),

    SHOW_HOME_FOOTER_IMAGE=(
        bool,
        os.environ.get('SHOW_HOME_FOOTER_IMAGE', False)),

    STATIC_URL_SUFFIX=(str, os.environ.get('STATIC_URL_SUFFIX', 'static')),

    TIME_ZONE=(str, os.environ.get('TIME_ZONE', 'UTC')),

    USE_SSL=(bool, os.environ.get('USE_SSL', False)))

# Load the values in the env file if it exists
if env('ENV_FILENAME'):
    env_file = join(dirname(__file__), env('ENV_FILENAME'))
    if exists(env_file):
        print('Loading environment file {0} through {1}'.format(
            env('ENV_FILENAME'),
            os.environ['DJANGO_SETTINGS_MODULE']))
        environ.Env.read_env(str(env_file))
    else:
        print('ERROR: File {0} not found.'.format(env_file))
        sys.exit(1)

if not env('SECRET_KEY'):
    print('The configuration variable "SECRET_KEY" cannot be empty.')
    print('Create a value executing the following python code snippet:')
    print("""python3 -c 'import random; import string; print("".join([random.SystemRandom().choice(string.digits + string.ascii_letters + string.punctuation) for i in range(100)]))'""")
    print("And assigining the resulting value to SECRET_KEY")
    sys.exit()


if not env('DATABASE_URL'):
    print('The coniguration variable "DATABASE_URL" cannot be empty.')
    print('The value must have the format "postgres://username:password@host:port/database"')
    sys.exit()


if not env('EMAIL_ACTION_NOTIFICATION_SENDER'):
    print('The configuration variable "EMAIL_ACTION_NOTIFICATION_SENDER"')
    print('cannot be empty. Must contain a valid email address')
    sys.exit()


def show_configuration() -> None:
    """Print the configuration in the console."""
    print('# Calculated variables')
    print('# --------------------')
    print('BASE_DIR:', BASE_DIR())
    print('ONTASK_TESTING:', ONTASK_TESTING)

    print('# Configuration Variables')
    print('# -----------------------')
    print('AWS_ACCESS_KEY_ID:', AWS_ACCESS_KEY_ID)
    print('AWS_LOCATION:', AWS_LOCATION)
    print('AWS_SECRET_ACCESS_KEY:', AWS_SECRET_ACCESS_KEY)
    print('AWS_STORAGE_BUCKET_NAME:', AWS_STORAGE_BUCKET_NAME)
    print('BASE_URL:', BASE_URL)
    print('DATABASE_URL:', DATABASE_URL)
    print('ENV_FILENAME:', env('ENV_FILENAME'))
    print('MEDIA_LOCATION:', MEDIA_LOCATION)
    print('REDIS_URL:', REDIS_URL)
    print('SESSION_CLEANUP_CRONTAB:', env('SESSION_CLEANUP_CRONTAB'))
    print('STATIC_URL_SUFFIX:', STATIC_URL_SUFFIX)
    print('USE_SSL:', USE_SSL)
    print()
    print('# Django - CORE')
    print('# -------------')
    print('ALLOWED_HOSTS (conf):', ALLOWED_HOSTS)
    print('CACHE_TTL:', CACHE_TTL)
    print('CACHES:', CACHES)
    print('DATABASES:', DATABASES)
    print('DATA_UPLOAD_MAX_NUMBER_FIELDS:', DATA_UPLOAD_MAX_NUMBER_FIELDS)
    print('DEBUG (conf):', DEBUG)
    print('EMAIL_HOST (conf):', EMAIL_HOST)
    print('EMAIL_HOST_USER (conf):', EMAIL_HOST_USER)
    print('EMAIL_HOST_PASSWORD (conf):', EMAIL_HOST_PASSWORD)
    print('EMAIL_PORT (conf):', EMAIL_PORT)
    print('EMAIL_USE_TLS (conf):', EMAIL_USE_TLS)
    print('EMAIL_USE_SSL (conf):', EMAIL_USE_SSL)
    print('INSTALLED_APPS:', INSTALLED_APPS)
    print('LANGUAGE_CODE (conf):', LANGUAGE_CODE)
    # print('LANGUAGES:', LANGUAGES)
    print('LOCALE_PATHS:', LOCALE_PATHS)
    print('LOGGING_CONFIG:', LOGGING_CONFIG)
    print('LOGGING:', LOGGING)
    print('MEDIA_ROOT:', MEDIA_ROOT)
    print('MEDIA_URL:', MEDIA_URL)
    print('MIDDLEWARE:', MIDDLEWARE)
    print('ROOT_URLCONF:', ROOT_URLCONF)
    print('SECRET_KEY (conf):', SECRET_KEY)
    print('SHORT_DATETIME_FORMAT:', SHORT_DATETIME_FORMAT)
    print('TEMPLATES:', TEMPLATES)
    print('TIME_ZONE (conf):', TIME_ZONE)
    print('USE_I18N:', USE_I18N)
    print('USE_L10N:', USE_L10N)
    print('USE_TZ:', USE_TZ)
    print('WSGI_APPLICATION:', WSGI_APPLICATION)
    print('X_FRAME_OPTIONS:', X_FRAME_OPTIONS)

    print('# Django - Auth')
    print('# -------------')
    print('AUTHENTICATION_BACKENDS:', AUTHENTICATION_BACKENDS)
    print('AUTH_USER_MODEL:', AUTH_USER_MODEL)
    # print('LOGIN_REDIRECT_URL:', LOGIN_REDIRECT_URL)
    # print('LOGIN_URL:', LOGIN_URL)
    print('PASSWORD_HASHERS:', PASSWORD_HASHERS)

    print('# Django - Messages')
    print('# -----------------')
    print('MESSAGE_LEVEL:', MESSAGE_LEVEL)
    print('MESSAGE_STORE:', MESSAGE_STORE)
    print('MESSAGE_TAGS:', MESSAGE_TAGS)

    print('# Django - Sessions')
    print('# -----------------')
    print('SESSION_CACHE_ALIAS:', SESSION_CACHE_ALIAS)
    print('SESSION_COOKIE_AGE:', SESSION_COOKIE_AGE)
    print('SESSION_ENGINE:', SESSION_ENGINE)
    print('SESSION_EXPIRE_AT_BROWSER_CLOSE:', SESSION_EXPIRE_AT_BROWSER_CLOSE)
    print('SESSION_SAVE_EVERY_REQUEST:', SESSION_SAVE_EVERY_REQUEST)

    print('# Django - Sites')
    print('# --------------')
    print('SITE_ID:', SITE_ID)

    print('# Django - Static Files')
    print('# ---------------------')
    print('STATIC_ROOT:', STATIC_ROOT)
    print('STATIC_URL:', STATIC_URL)
    print('STATICFILES_DIRS:', ', '.join(STATICFILES_DIRS))

    print('# Django-crispy-forms')
    print('# -------------------')
    print('CRISPY_TEMPLATE_PACK:', CRISPY_TEMPLATE_PACK)

    print('# Django-import-export')
    print('# --------------------')
    print('IMPORT_EXPORT_USE_TRANSACTIONS:', IMPORT_EXPORT_USE_TRANSACTIONS)

    print('# Canvas')
    print('# ------')
    print('CANVAS_INFO_DICT (conf):', CANVAS_INFO_DICT)
    print('CANVAS_TOKEN_EXPIRY_SLACK (conf):', CANVAS_TOKEN_EXPIRY_SLACK)

    print('# Celery')
    print('# ------')
    print('CELERY_ACCEPT_CONTENT:', CELERY_ACCEPT_CONTENT)
    print('CELERY_BEAT_SCHEDULE:', CELERY_BEAT_SCHEDULE)
    print('CELERY_BROKER_URL:', CELERY_BROKER_URL)
    print('CELERY_RESULT_BACKEND:', CELERY_RESULT_BACKEND)
    print('CELERY_RESULT_SERIALIZER:', CELERY_RESULT_SERIALIZER)
    print('CELERY_SESSION_CLEANUP_CRONTAB:', CELERY_SESSION_CLEANUP_CRONTAB)
    print('CELERY_TASK_ALWAYS_EAGER:', CELERY_TASK_ALWAYS_EAGER)
    print('CELERY_TASK_SERIALIZER:', CELERY_TASK_SERIALIZER)
    print('CELERY_TIMEZONE:', CELERY_TIMEZONE)

    print('# Easy-thumbnails')
    print('# ---------------')
    print('THUMBNAIL_EXTENSION:', THUMBNAIL_EXTENSION)

    print('# OnTask')
    print('# ------')
    print('DATAOPS_CONTENT_TYPES:', DATAOPS_CONTENT_TYPES)
    print('DATAOPS_MAX_UPLOAD_SIZE (conf):', DATAOPS_MAX_UPLOAD_SIZE)
    print('DATAOPS_PLUGIN_DIRECTORY (conf):', DATAOPS_PLUGIN_DIRECTORY)
    print('DISABLED_ACTIONS:', DISABLED_ACTIONS)
    print(
        'EMAIL_ACTION_NOTIFICATION_SENDER:',
        EMAIL_ACTION_NOTIFICATION_SENDER)
    # print(
    #     'EMAIL_ACTION_NOTIFICATION_SUBJECT:',
    #     EMAIL_ACTION_NOTIFICATION_SUBJECT)
    print(
        'EMAIL_ACTION_NOTIFICATION_TEMPLATE:',
        EMAIL_ACTION_NOTIFICATION_TEMPLATE)
    print('EMAIL_ACTION_PIXEL:', EMAIL_ACTION_PIXEL)
    print('EMAIL_BURST (conf):', EMAIL_BURST)
    print('EMAIL_BURST_PAUSE (conf):', EMAIL_BURST_PAUSE)
    print('EMAIL_HTML_ONLY (conf):', EMAIL_HTML_ONLY)
    print('EMAIL_OVERRIDE_FROM (conf):', EMAIL_OVERRIDE_FROM)
    print('EXECUTE_ACTION_JSON_TRANSFER (conf):', EXECUTE_ACTION_JSON_TRANSFER)
    print('LOG_FOLDER (conf):', env('LOG_FOLDER'))
    print('LOGS_MAX_LIST_SIZE:', LOGS_MAX_LIST_SIZE)
    print('ONTASK_HELP_URL:', ONTASK_HELP_URL)
    print('SHOW_HOME_FOOTER_IMAGE (conf):', SHOW_HOME_FOOTER_IMAGE)

    print('# LTI Authentication')
    print('# ------------------')
    print('LTI_OAUTH_CREDENTIALS (conf):', LTI_OAUTH_CREDENTIALS)
    print('LTI_INSTRUCTOR_GROUP_ROLES: (conf)', LTI_INSTRUCTOR_GROUP_ROLES)

    print('# Django REST Framework and drf-yasg')
    print('# ----------------------------------')
    print('REST_FRAMEWORK:', REST_FRAMEWORK)
    print('SWAGGER_SETTINGS:', SWAGGER_SETTINGS)

    print('# Summernote')
    print('# ----------')
    print('SUMMERNOTE_THEME:', SUMMERNOTE_THEME)
    print('SUMMERNOTE_CONFIG:', SUMMERNOTE_CONFIG)


# CONFIGURATION VARIABLES
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_LOCATION = env('AWS_LOCATION')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

BASE_URL = env('BASE_URL')

DATABASE_URL = env.db()

LOG_FOLDER = env('LOG_FOLDER')

MEDIA_LOCATION = env('MEDIA_LOCATION')

REDIS_URL = env.cache('REDIS_URL')

# Frequency to run the clear session command
SESSION_CLEANUP_CRONTAB = env('SESSION_CLEANUP_CRONTAB')

STATIC_URL_SUFFIX = env('STATIC_URL_SUFFIX')

USE_SSL = env.bool('USE_SSL', default=False)

# Django Core
# -----------------------------------------------------------------------------
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

CACHE_TTL = 60 * 30
CACHES = {"default": REDIS_URL}

DATABASES = {'default': DATABASE_URL, }

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

DEBUG = env.bool('DEBUG', default=False)

EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env('EMAIL_PORT', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)

INSTALLED_APPS = [
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_celery_beat',
    'django_celery_results',
    'bootstrap_datepicker_plus',
    'drf_yasg',
    # 'corsheaders',

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

    'ontask.apps.OnTaskConfig',
    'ontask.django_auth_lti',
]
if AWS_ACCESS_KEY_ID:
    INSTALLED_APPS += ['storages']

LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
LANGUAGES = [
    ('en-us', _('English')),
    ('es-es', _('Spanish')),
    ('zh-cn', _('Chinese')),
    ('fi', _('Finnish')),
    ('ru', _('Russian'))]
LOCALE_PATHS = [join(BASE_DIR(), 'locale')]

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s] %(levelname)s '
                + '[%(pathname)s:%(lineno)s] %(message)s'),
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
}

MEDIA_ROOT = join(BASE_DIR(), 'media')
if AWS_ACCESS_KEY_ID:
    MEDIA_URL = 'https://%s.s3.amazonaws.com/%s/' % (
        AWS_STORAGE_BUCKET_NAME,
        MEDIA_LOCATION)
else:
    MEDIA_URL = BASE_URL + MEDIA_LOCATION

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ontask.django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'urls'

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not defined
SECRET_KEY = env('SECRET_KEY')

SHORT_DATETIME_FORMAT = 'r'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [join(BASE_DIR(), 'ontask', 'templates')],
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
            'ontask.core.context_processors.conf_to_context',
        ],
        'libraries': {
            'ontask_tags': 'ontask.templatetags.ontask_tags',
            'vis_include':
                'ontask.visualizations.templatetags.vis_include'}}}]

TIME_ZONE = env('TIME_ZONE')

USE_I18N = True
USE_L10N = True
USE_TZ = True

WSGI_APPLICATION = 'wsgi.application'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Django Auth
# -----------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'ontask.django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend']
AUTH_USER_MODEL = 'authtools.User'
LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGIN_URL = reverse_lazy('accounts:login')
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# Django Messages
# -----------------------------------------------------------------------------
MESSAGE_LEVEL = message_constants.DEBUG
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {messages.ERROR: 'danger'}

# Django Sessions
# -----------------------------------------------------------------------------
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1800  # set just 30 mins
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True  # Needed to make sure timeout above works

# Django Site
# -----------------------------------------------------------------------------
SITE_ID = 1

# Django Static Files
# -----------------------------------------------------------------------------
STATIC_ROOT = join(BASE_DIR(), 'site', 'static')
if AWS_ACCESS_KEY_ID:
    STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (
        AWS_STORAGE_BUCKET_NAME,
        AWS_LOCATION)
    STATICFILES_DIRS = [join(BASE_DIR(), AWS_LOCATION)]
else:
    STATIC_URL = BASE_URL + '/' + STATIC_URL_SUFFIX + '/'
    STATICFILES_DIRS = [join(BASE_DIR(), STATIC_URL_SUFFIX)]

# Django-crispy-forms
# -----------------------------------------------------------------------------
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Django-import-export
# -----------------------------------------------------------------------------
IMPORT_EXPORT_USE_TRANSACTIONS = True

# Canvas
# -----------------------------------------------------------------------------
###############################################################################
#
# CANVAS API ENTRY POINTS
#
# The  variable must contain a dictionary with the following elements:
#
#   "Server name or domain descriptor (shown to the user": {
#      domain_port: VALUE,
#      client_id: VALUE,
#      client_secret: VALUE ,
#      authorize_url: VALUE (format {0} for domain_port),
#      access_token_url: VALUE (format {0} for domain_port),
#      conversation_URL: VALUE (format {0} for domain_port),
#      aux_params: DICT with additional parameters)
#    }
#  For example:
#
# CANVAS_INFO_DICT={
#     "Server one": {
#         "domain_port": "yourcanvasdomain.edu",
#         "client_id": "10000000000001",
#         "client_secret":
#             "YZnGjbkopt9MpSq2fujUOgbeVZ8NdkdCeGF2ufhWZdBKAZvNCuuTOWXHotsWMu6X",
#         "authorize_url": "http://{0}/login/oauth2/auth",
#         "access_token_url": "http://{0}/login/oauth2/token",
#         "conversation_url": "http://{0}/api/v1/conversations",
#         "aux_params": {"burst": 10, "pause": 5}
#     }
# }
# ------------------------------------------------------------------------------
CANVAS_INFO_DICT = json.loads(env.str('CANVAS_INFO_DICT'))
# Number of seconds left in the token validity to refresh
CANVAS_TOKEN_EXPIRY_SLACK = env.int('CANVAS_TOKEN_EXPIRY_SLACK')

# Celery
# -----------------------------------------------------------------------------
CELERY_ACCEPT_CONTENT = ['application/json', 'pickle']
CELERY_SESSION_CLEANUP_CRONTAB = SESSION_CLEANUP_CRONTAB.split()
CELERY_BEAT_SCHEDULE = {
    'ontask_scheduler': {
        'task': 'ontask.tasks.session_cleanup.session_cleanup',
        'schedule': crontab(
            minute=CELERY_SESSION_CLEANUP_CRONTAB[0],
            hour=CELERY_SESSION_CLEANUP_CRONTAB[1],
            day_of_week=CELERY_SESSION_CLEANUP_CRONTAB[2],
            day_of_month=CELERY_SESSION_CLEANUP_CRONTAB[3],
            month_of_year=CELERY_SESSION_CLEANUP_CRONTAB[4]),
        #     'args': (DEBUG,),
        'name': '__ONTASK_CLEANUP_SESSION_TASK',
    },
}
CELERY_BROKER_URL = REDIS_URL['LOCATION']
CELERY_RESULT_BACKEND = REDIS_URL['LOCATION']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = ONTASK_TESTING
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Easy-thumbnails
# -----------------------------------------------------------------------------
THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails

# OnTask Configuration
# -----------------------------------------------------------------------------
DATAOPS_CONTENT_TYPES = '["text/csv", "application/json", ' \
                        '"application/gzip", "application/x-gzip", ' \
                        '"application/vnd.ms-excel"]'
DATAOPS_MAX_UPLOAD_SIZE = env.int('DATAOPS_MAX_UPLOAD_SIZE', default=209715200)
DATAOPS_PLUGIN_DIRECTORY = env(
    'DATAOPS_PLUGIN_DIRECTORY',
    env,
    join(BASE_DIR(), 'lib', 'plugins'))

DISABLED_ACTIONS = [
    # 'models.Action.PERSONALIZED_TEXT',
    # 'models.Action.PERSONALIZED_JSON',
    # 'models.Action.PERSONALIZED_CANVAS_EMAIL',
    # 'models.Action.EMAIL_REPORT',
    # 'models.Action.JSON_REPORT',
    # 'models.Action.SURVEY',
    'models.Action.TODO_LIST']

EMAIL_ACTION_NOTIFICATION_SENDER = env(
    'EMAIL_ACTION_NOTIFICATION_SENDER',
    default='')
EMAIL_ACTION_NOTIFICATION_SUBJECT = _('OnTask: Action executed')
EMAIL_ACTION_NOTIFICATION_TEMPLATE = """
<html>
<head/>
<body>
<p>Dear {{ user.name }}</p>

<p>This message is to inform you that on {{ email_sent_datetime }}
{{ num_messages }} email{% if num_messages > 1 %}s{% endif %} were sent
resulting from the execution of the action with name "{{ action.name }}".</p>

{% if filter_present %}
<p>The action had a filter that reduced the number of messages from
{{ num_rows }} to {{ num_selected }}.</p>
{% else %}
<p>All the data rows stored in the workflow table were used.</p>
{% endif %}

Regards.
The OnTask Support Team
</body></html>"""
EMAIL_ACTION_PIXEL = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC' \
                     '0lEQVR4nGP6zwAAAgcBApocMXEAAAAASUVORK5CYII='
# Number of emails to send out in a burst (before pausing)
EMAIL_BURST = env.int('EMAIL_BURST', default=0)
# Pause between bursts (in seconds)
EMAIL_BURST_PAUSE = env.int('EMAIL_BURST_PAUSE', default=0)
# Include HTML only email or HTML and text
EMAIL_HTML_ONLY = env.bool('EMAIL_HTML_ONLY', default=True)
# Email address to override the From in emails (if empty, use user email)
EMAIL_OVERRIDE_FROM = env('EMAIL_OVERRIDE_FROM')

EXECUTE_ACTION_JSON_TRANSFER = env.bool('EXECUTE_ACTION_JSON_TRANSFER')

LOGS_MAX_LIST_SIZE = 200

ONTASK_HELP_URL = "html/index.html"

SHOW_HOME_FOOTER_IMAGE = env.bool('SHOW_HOME_FOOTER_IMAGE', default=False)

# LTI Configuration
# -----------------------------------------------------------------------------
LTI_OAUTH_CREDENTIALS = env.dict('LTI_OAUTH_CREDENTIALS', default={})
LTI_INSTRUCTOR_GROUP_ROLES = env.list(
    'LTI_INSTRUCTOR_GROUP_ROLES',
    default=['Instructor'])

# Django REST Framework and drf-yasg
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'],
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    # ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # )
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_RATES': {'anon': '100/minute', 'user': '1000/minute'}}
SWAGGER_SETTINGS = {'SECURITY_DEFINITIONS': {'basic': {'type': 'basic'}}}

# django-summernote
# ------------------------------------------------------------------------------
CANVAS_INFO_DICT = json.loads(env.str('CANVAS_INFO_DICT', default='{}'))
# Number of seconds left in the token validity to refresh
CANVAS_TOKEN_EXPIRY_SLACK = env.int('CANVAS_TOKEN_EXPIRY_SLACK', default=600)
SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'iframe': False,
    'summernote': {
        'width': '100%',
        'height': '400px',
        'disableDragAndDrop': True},
    'css': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/'
        + 'theme/base16-dark.min.css',),
    'css_for_inplace': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/'
        + 'theme/base16-dark.min.css',),
    'codemirror': {
        'theme': 'base16-dark',
        'mode': 'htmlmixed',
        'lineNumbers': True,
        'lineWrapping': True},
    # Disable attachment feature so all images are inlined
    'disable_attachment': True,
    'lazy': True}

# django-cors-headers
# ------------------------------------------------------------------------------
# CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = []
# CORS_ORIGIN_REGEX_WHITELIST = []

# LDAP AUTHENTICATION
# ------------------------------------------------------------------------------
# Variables taken from local.env
# LDAP_AUTH_SERVER_URI = get_from_os_or_env('LDAP_AUTH_SERVER_URI', env)
# LDAP_AUTH_BIND_PASSWORD = get_from_os_or_env('LDAP_AUTH_BIND_PASSWORD', env)

# Additional configuration variables (read django-auth-ldap documentation)
# AUTH_LDAP_CONNECTION_OPTIONS = {
# }
# AUTH_LDAP_BIND_DN = "cn=admin,dc=bogus,dc=com"
# AUTH_LDAP_USER_SEARCH = LDAPSearch(
#     "ou=people,dc=bogus,dc=com",
#     ldap.SCOPE_SUBTREE,
#     "(uid=%(user)s)")
# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=bogus,dc=com"
# AUTH_LDAP_START_TLS = True
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=com",
#     ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
# )
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
# AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=groups,dc=example,dc=com"
# AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=groups,dc=example,dc=com"
# AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "cn=active,ou=groups,dc=example,dc=com",
#     "is_staff": (
#         LDAPGroupQuery("cn=staff,ou=groups,dc=example,dc=com") |
#         LDAPGroupQuery("cn=admin,ou=groups,dc=example,dc=com")
#     ),
#     "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
# }
# AUTH_LDAP_ALWAYS_UPDATE_USER = True
# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_CACHE_GROUPS = True
# AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300
