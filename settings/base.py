"""Django settings for OnTask project."""
import json
import os
import sys
from os.path import dirname, exists, join

import environ
from celery.schedules import crontab
from django.contrib import messages
from django.contrib.messages import constants as message_constants
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# import ldap
# from django_auth_ldap.config import (
#     LDAPSearch,
#     GroupOfNamesType,
#     LDAPGroupQuery
# )

# Variables required to process configuration
BASE_DIR = environ.Path(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONTASK_TESTING = 'test' in sys.argv or 'shell_plus' in sys.argv

# Use 12factor inspired environment variables.
env = environ.Env()

# Load the values in the env file if it exists
ENV_FILENAME = join(
    dirname(__file__),
    env('ENV_FILENAME', default='local.env'))

print('SYS.ARGV:', sys.argv)
print('SYS.VERSION:', sys.version)
print('BASE_DIR:', BASE_DIR)
print('ENV_FILENAME:', ENV_FILENAME)
print('DJANGO_SETTINGS_MODULE:', env('DJANGO_SETTINGS_MODULE'))

if exists(ENV_FILENAME):
    environ.Env.read_env(str(ENV_FILENAME))

# CONFIGURATION VARIABLES
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_LOCATION = env('AWS_LOCATION', default='static')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')

BASE_URL = env('BASE_URL', default='')

CANVAS_INFO_DICT = json.loads(env('CANVAS_INFO_DICT', default='{}'))
CANVAS_TOKEN_EXPIRY_SLACK = env.int('CANVAS_TOKEN_EXPIRY_SLACK', default=600)

DATABASE_URL = env.db()

DATAOPS_CONTENT_TYPES = env(
    'DATAOPS_CONTENT_TYPES',
    default='["text/csv", "application/json", '
            + '"application/gzip", "application/x-gzip", '
            + '"application/vnd.ms-excel"]')
DATAOPS_MAX_UPLOAD_SIZE = env.int('DATAOPS_MAX_UPLOAD_SIZE', default=209715200)
DATAOPS_PLUGIN_DIRECTORY = env(
    'DATAOPS_PLUGIN_DIRECTORY',
    default=join(BASE_DIR(), 'lib', 'plugins'))

DEBUG = env.bool('DEBUG', default=False)

DEBUG_TOOLBAR = env('DEBUG_TOOLBAR', default=DEBUG)

EMAIL_ACTION_NOTIFICATION_SENDER = env('EMAIL_ACTION_NOTIFICATION_SENDER')
EMAIL_ACTION_NOTIFICATION_SUBJECT = env(
    'EMAIL_ACTION_NOTIFICATION_SUBJECT',
    default='OnTask: Action executed')
EMAIL_ACTION_NOTIFICATION_TEMPLATE = env(
    'EMAIL_ACTION_NOTIFICATION_TEMPLATE',
    default="""<html>
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
</body></html>""")

EMAIL_BURST = env.int('EMAIL_BURST', default=0)
EMAIL_BURST_PAUSE = env.int('EMAIL_BURST_PAUSE', default=0)
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_HTML_ONLY = env.bool('EMAIL_HTML_ONLY', default=True)
EMAIL_OVERRIDE_FROM = env('EMAIL_OVERRIDE_FROM', default='')
EMAIL_PORT = env('EMAIL_PORT', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default='')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default='')

EXECUTE_ACTION_JSON_TRANSFER = env.bool(
    'EXECUTE_ACTION_JSON_TRANSFER',
    default=True)

LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')

LDAP_AUTH_SERVER_URI = env('LDAP_AUTH_SERVER_URI', default='')
LDAP_AUTH_BIND_PASSWORD = env('LDAP_AUTH_BIND_PASSWORD', default='')

LOG_FOLDER = env('LOG_FOLDER', default=join(BASE_DIR(), 'logs'))

LOGS_MAX_LIST_SIZE = env.int('LOGS_MAX_LIST_SIZE', default=200)

LTI_OAUTH_CREDENTIALS = env.dict('LTI_OAUTH_CREDENTIALS', default={})
LTI_INSTRUCTOR_GROUP_ROLES = env.list(
    'LTI_INSTRUCTOR_GROUP_ROLES',
    default=['Instructor'])

MEDIA_LOCATION = env('MEDIA_LOCATION', default='media/')

ONTASK_HELP_URL = env('ONTASK_HELP_URL', default='html/index.html')

PROFILE_CPROFILE = env('PROFILE_CPROFILE', default=False)

PROFILE_SILK = env('PROFILE_SILK', default=False)

REDIS_URL = env.cache('REDIS_URL')

SECRET_KEY = env('SECRET_KEY')

# Set to ('HTTP_X_FORWARDED_PROTO', 'https') if behind a proxy
SECURE_PROXY_SSL_HEADER = env('SECURE_PROXY_SSL_HEADER', default=None)

SESSION_CLEANUP_CRONTAB = env('SESSION_CLEANUP_CRONTAB', default='05 5 6 * *')

SHOW_HOME_FOOTER_IMAGE = env.bool('SHOW_HOME_FOOTER_IMAGE', default=False)

STATIC_URL_SUFFIX = env('STATIC_URL_SUFFIX', default='static')

TIME_ZONE = env('TIME_ZONE', default='UTC')

USE_SSL = env.bool('USE_SSL', default=False)

# True if behind a proxy and need to read the X-Forwarded-Host header
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=False)

# -----------------------------------------------------------------------------
# Configuration below this line at your own risk
# -----------------------------------------------------------------------------

# Django Core
# -----------------------------------------------------------------------------
CACHE_TTL = 60 * 30
# CACHES = {"default": REDIS_URL} # TODO: Fix REDIS configuration in Django 4
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 1000,
        'KEY_PREFIX': 'ontask',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
# This configuration does not work due to the Backend class
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient'
#         },
#         'KEY_PREFIX': 'ontask'
#     }
# }

DATABASES = {'default': DATABASE_URL}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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
    'bootstrap5',
    'bootstrap_datepicker_plus',
    'drf_yasg',
    # 'corsheaders',

    'crispy_forms',
    'crispy_bootstrap5',
    'sorl.thumbnail',
    'widget_tweaks',
    'formtools',
    'siteprefs',
    'django_tables2',
    'import_export',
    'rest_framework',
    'rest_framework.authtoken',
    'jquery',
    'tinymce',

    'ontask.apps.OnTaskConfig',
    'ontask.django_auth_lti',
]
if AWS_ACCESS_KEY_ID:
    INSTALLED_APPS += ['storages']

LANGUAGES = [('en-us', _('English')), ('es-es', _('Spanish'))]

# No longer actively maintained
# ('zh-cn', _('Chinese')),
# ('fi', _('Finnish')),
# ('ru', _('Russian'))]

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
        'simple': {'format': '%(levelname)s %(message)s'},
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
    MEDIA_URL = 'https://%s.s3.amazonaws.com/%s' % (
        AWS_STORAGE_BUCKET_NAME,
        MEDIA_LOCATION)
    DEFAULT_FILE_STORAGE = 'ontask.core.storage_backends.PrivateMediaStorage'
else:
    MEDIA_URL = BASE_URL + '/' + MEDIA_LOCATION

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

SHORT_DATETIME_FORMAT = 'r'

SITEPREFS_EXPOSE_MODEL_TO_ADMIN = True
SITEPREFS_DISABLE_AUTODISCOVER = not (
    'manage' not in sys.argv[0]
    or (len(sys.argv) > 1)
    and sys.argv[1] in
    ['runserver', 'runserver_plus', 'run_gnunicorn', 'celeryd'])
SITEPREFS_MODULE_NAME = 'settings'

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
        ],
        'libraries': {
            'ontask_tags': 'ontask.templatetags.ontask_tags',
            'vis_include':
                'ontask.visualizations.templatetags.vis_include'}}}]

USE_I18N = True
USE_TZ = True

WSGI_APPLICATION = 'wsgi.application'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Django Auth
# -----------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'ontask.django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    # 'django_auth_ldap.backend.LDAPBackend',
    'ontask.accounts.backends.CaseInsensitiveUsernameFieldModelBackend']
AUTH_USER_MODEL = 'ontask.User'
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
SESSION_COOKIE_AGE = 1800  # Seconds: 30 minutes
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
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    STATIC_URL = BASE_URL + '/' + STATIC_URL_SUFFIX + '/'
    STATICFILES_DIRS = [join(BASE_DIR(), STATIC_URL_SUFFIX)]

# Django-Tables2
# -----------------------------------------------------------------------------
DJANGO_TABLES2_TABLE_TEMPLATE = 'django_tables2/bootstrap5-responsive.html'

# Django-crispy-forms
# -----------------------------------------------------------------------------
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

# Django-import-export
# -----------------------------------------------------------------------------
IMPORT_EXPORT_USE_TRANSACTIONS = True

# Django-stores
# -----------------------------------------------------------------------------
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
# AWS_QUERYSTRING_AUTH = False

# Celery
# -----------------------------------------------------------------------------
CELERY_ACCEPT_CONTENT = ['application/json', 'pickle']
CELERY_SESSION_CLEANUP_CRONTAB = SESSION_CLEANUP_CRONTAB.split()
CELERY_BEAT_SCHEDULE = {
    '__ONTASK_CLEANUP_SESSION_TASK': {
        'task': 'ontask.tasks.session_cleanup.session_cleanup',
        'schedule': crontab(
            minute=CELERY_SESSION_CLEANUP_CRONTAB[0],
            hour=CELERY_SESSION_CLEANUP_CRONTAB[1],
            day_of_week=CELERY_SESSION_CLEANUP_CRONTAB[2],
            day_of_month=CELERY_SESSION_CLEANUP_CRONTAB[3],
            month_of_year=CELERY_SESSION_CLEANUP_CRONTAB[4]),
        #     'args': (DEBUG,),
    },
}
CELERY_BROKER_URL = REDIS_URL['LOCATION']
CELERY_RESULT_BACKEND = REDIS_URL['LOCATION']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = ONTASK_TESTING
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# OnTask Configuration
# -----------------------------------------------------------------------------
DISABLED_ACTIONS = [
    # 'models.Action.PERSONALIZED_TEXT',
    # 'models.Action.PERSONALIZED_JSON',
    # 'models.Action.PERSONALIZED_CANVAS_EMAIL',
    # 'models.Action.EMAIL_REPORT',
    # 'models.Action.JSON_REPORT',
    # 'models.Action.SURVEY',
    'models.Action.TODO_LIST']

EMAIL_ACTION_PIXEL = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC' \
                     '0lEQVR4nGP6zwAAAgcBApocMXEAAAAASUVORK5CYII='

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


# django-tinymce
# ------------------------------------------------------------------------------
TINYMCE_JS_URL = os.path.join(STATIC_URL, 'js', 'tinymce/tinymce.min.js')
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": "file edit view insert format tools table help",

    "plugins": "advlist,autolink,lists,link,image,charmap,print,preview,"
               "anchor,searchreplace,visualblocks,code,fullscreen,"
               "insertdatetime,media,table,paste,code,help,wordcount,"
               "emoticons,imagetools",

    "toolbar": "undo redo | fontselect fontsizeselect formatselect | "
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "forecolor backcolor | image removeformat | link unlink openlink | "
    "searchreplace | fullscreen | emoticons | help",

    "toolbar_mode": "sliding",
}
TINYMCE_COMPRESSOR = False

# django-cors-headers
# ------------------------------------------------------------------------------
# CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = []
# CORS_ORIGIN_REGEX_WHITELIST = []

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


def show_configuration() -> None:
    """Print the configuration in the console."""
    print('# Calculated variables')
    print('# --------------------')
    print('BASE_DIR:', BASE_DIR())
    print('ONTASK_TESTING:', ONTASK_TESTING)
    print()
    print('# Configuration Variables')
    print('# -----------------------')
    print('AWS_ACCESS_KEY_ID:', AWS_ACCESS_KEY_ID)
    print('AWS_LOCATION:', AWS_LOCATION)
    print(
        'AWS_SECRET_ACCESS_KEY:',
        'GIVEN' if AWS_SECRET_ACCESS_KEY else 'None')
    print('AWS_STORAGE_BUCKET_NAME:', AWS_STORAGE_BUCKET_NAME)
    print('BASE_URL:', BASE_URL)
    print('DATABASE_URL:', DATABASE_URL)
    print('ENV_FILENAME:', ENV_FILENAME)
    print('MEDIA_LOCATION:', MEDIA_LOCATION)
    print('REDIS_URL:', REDIS_URL)
    print('SESSION_CLEANUP_CRONTAB:', SESSION_CLEANUP_CRONTAB)
    print('STATIC_URL_SUFFIX:', STATIC_URL_SUFFIX)
    print('USE_SSL:', USE_SSL)
    print()
    print('# Canvas')
    print('# ------')
    print('CANVAS_INFO_DICT (conf):', CANVAS_INFO_DICT)
    print('CANVAS_TOKEN_EXPIRY_SLACK (conf):', CANVAS_TOKEN_EXPIRY_SLACK)
    print()
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
    print()
    print('# Django - CORE')
    print('# -------------')
    print('ALLOWED_HOSTS (conf):', ALLOWED_HOSTS)
    print('CACHE_TTL:', CACHE_TTL)
    print('CACHES:', CACHES)
    print('DATABASES:', DATABASES)
    print('DATA_UPLOAD_MAX_NUMBER_FIELDS:', DATA_UPLOAD_MAX_NUMBER_FIELDS)
    print('DEBUG (conf):', DEBUG)
    print('DEBUG_TOOLBAR (conf):', DEBUG_TOOLBAR)
    print('EMAIL_HOST (conf):', EMAIL_HOST)
    print('EMAIL_HOST_USER (conf):', EMAIL_HOST_USER)
    print(
        'EMAIL_HOST_PASSWORD (conf):',
        'Given' if EMAIL_HOST_PASSWORD else 'None')
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
    print('PROFILE_CPROFILE (conf):', PROFILE_CPROFILE)
    print('PROFILE_SILK (conf):', PROFILE_SILK)
    print('ROOT_URLCONF:', ROOT_URLCONF)
    print('SHORT_DATETIME_FORMAT:', SHORT_DATETIME_FORMAT)
    print('SECURE_PROXY_SSL_HEADER:', SECURE_PROXY_SSL_HEADER)
    print('TEMPLATES:', TEMPLATES)
    print('TIME_ZONE (conf):', TIME_ZONE)
    print('USE_I18N:', USE_I18N)
    print('USE_TZ:', USE_TZ)
    print('USE_X_FORWARDED_HOST:', USE_X_FORWARDED_HOST)
    print('WSGI_APPLICATION:', WSGI_APPLICATION)
    print('X_FRAME_OPTIONS:', X_FRAME_OPTIONS)
    print()
    print('# Django - Auth')
    print('# -------------')
    print('AUTHENTICATION_BACKENDS:', AUTHENTICATION_BACKENDS)
    print('AUTH_USER_MODEL:', AUTH_USER_MODEL)
    # print('LOGIN_REDIRECT_URL:', LOGIN_REDIRECT_URL)
    # print('LOGIN_URL:', LOGIN_URL)
    print('PASSWORD_HASHERS:', PASSWORD_HASHERS)
    print()
    print('# Django - Messages')
    print('# -----------------')
    print('MESSAGE_LEVEL:', MESSAGE_LEVEL)
    print('MESSAGE_STORE:', MESSAGE_STORE)
    print('MESSAGE_TAGS:', MESSAGE_TAGS)
    print()
    print('# Django REST Framework and drf-yasg')
    print('# ----------------------------------')
    print('REST_FRAMEWORK:', REST_FRAMEWORK)
    print('SWAGGER_SETTINGS:', SWAGGER_SETTINGS)
    print()
    print('# Django - Sessions')
    print('# -----------------')
    print('SESSION_CACHE_ALIAS:', SESSION_CACHE_ALIAS)
    print('SESSION_COOKIE_AGE:', SESSION_COOKIE_AGE)
    print('SESSION_ENGINE:', SESSION_ENGINE)
    print('SESSION_EXPIRE_AT_BROWSER_CLOSE:', SESSION_EXPIRE_AT_BROWSER_CLOSE)
    print('SESSION_SAVE_EVERY_REQUEST:', SESSION_SAVE_EVERY_REQUEST)
    print()
    print('# Django - Sites')
    print('# --------------')
    print('SITE_ID:', SITE_ID)
    print()
    print('# Django - Static Files')
    print('# ---------------------')
    print('STATIC_ROOT:', STATIC_ROOT)
    print('STATIC_URL:', STATIC_URL)
    print('STATICFILES_DIRS:', ', '.join(STATICFILES_DIRS))
    print()
    print('# Django-crispy-forms')
    print('# -------------------')
    print('CRISPY_TEMPLATE_PACK:', CRISPY_TEMPLATE_PACK)
    print()
    print('# Django-import-export')
    print('# --------------------')
    print('IMPORT_EXPORT_USE_TRANSACTIONS:', IMPORT_EXPORT_USE_TRANSACTIONS)
    print()
    print('# LTI Authentication')
    print('# ------------------')
    print('LTI_OAUTH_CREDENTIALS (conf):', LTI_OAUTH_CREDENTIALS)
    print('LTI_INSTRUCTOR_GROUP_ROLES: (conf)', LTI_INSTRUCTOR_GROUP_ROLES)
    print()
    print('# OnTask')
    print('# --------')
    print('DATAOPS_CONTENT_TYPES:', DATAOPS_CONTENT_TYPES)
    print('DATAOPS_MAX_UPLOAD_SIZE (conf):', DATAOPS_MAX_UPLOAD_SIZE)
    print('DATAOPS_PLUGIN_DIRECTORY (conf):', DATAOPS_PLUGIN_DIRECTORY)
    print('DISABLED_ACTIONS:', DISABLED_ACTIONS)
    print(
        'EMAIL_ACTION_NOTIFICATION_SENDER:',
        EMAIL_ACTION_NOTIFICATION_SENDER)
    print(
        'EMAIL_ACTION_NOTIFICATION_SUBJECT:',
        EMAIL_ACTION_NOTIFICATION_SUBJECT)
    print(
        'EMAIL_ACTION_NOTIFICATION_TEMPLATE:',
        EMAIL_ACTION_NOTIFICATION_TEMPLATE)
    print('EMAIL_ACTION_PIXEL:', EMAIL_ACTION_PIXEL)
    print('EMAIL_BURST (conf):', EMAIL_BURST)
    print('EMAIL_BURST_PAUSE (conf):', EMAIL_BURST_PAUSE)
    print('EMAIL_HTML_ONLY (conf):', EMAIL_HTML_ONLY)
    print('EMAIL_OVERRIDE_FROM (conf):', EMAIL_OVERRIDE_FROM)
    print('EXECUTE_ACTION_JSON_TRANSFER (conf):', EXECUTE_ACTION_JSON_TRANSFER)
    print('LOG_FOLDER (conf):', LOG_FOLDER)
    print('LOGS_MAX_LIST_SIZE:', LOGS_MAX_LIST_SIZE)
    print('ONTASK_HELP_URL:', ONTASK_HELP_URL)
    print('SHOW_HOME_FOOTER_IMAGE (conf):', SHOW_HOME_FOOTER_IMAGE)
    print()
    print('# TinyMCE')
    print('# ----------')
    print('TINYMCE_JS_URL:', TINYMCE_JS_URL)
    print('TINYMCE_DEFAULT_CONFIG:', TINYMCE_DEFAULT_CONFIG)
    print('TINYMCE_COMPRESSOR:', TINYMCE_COMPRESSOR)
