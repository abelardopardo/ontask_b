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

# Use 12factor inspired environment variables or from a file and define defaults
env = environ.Env()
env_file_name = os.environ.get('ENV_FILENAME', 'local.env')
env_file = join(dirname(__file__), env_file_name)
if exists(env_file):
    print('Loading environment file {0} through {1}'.format(
        env_file_name,
        os.environ['DJANGO_SETTINGS_MODULE']))
    environ.Env.read_env(str(env_file))
else:
    print('ERROR: File {0} not found.'.format(env_file))
    sys.exit(1)


# DUMP CONFIG IN DEBUG
# ------------------------------------------------------------------------------
def dump_config() -> None:
    """Print the configuration in the console."""
    print('ALLOWED_HOSTS:', ALLOWED_HOSTS)
    print('BASE_DIR:', BASE_DIR())
    print('CELERY_TASK_ALWAYS_EAGER:', CELERY_TASK_ALWAYS_EAGER)
    print('DATABASE_URL:', DATABASES['default'])
    print('DEBUG:', DEBUG)
    print('DOMAIN_NAME:', DOMAIN_NAME)
    print('MEDIA_ROOT:', MEDIA_ROOT)
    print('MEDIA_URL:', MEDIA_URL)
    print('ONTASK_HELP_URL:', ONTASK_HELP_URL)
    print('ONTASK_TESTING:', ONTASK_TESTING)
    print('REDIS_URL:', REDIS_URL)
    print('STATICFILES_DIRS:', ', '.join(STATICFILES_DIRS))
    print('STATIC_ROOT:', STATIC_ROOT)
    print('STATIC_URL:', STATIC_URL)
    print('USE_SSL:', USE_SSL)


def get_from_os_or_env(key: str, env_obj, default_value=''):
    """
    Given a key, search for its value first in the os environment, then in the
    given environment and if not present, return the default
    :param key: key to search
    :param env_obj: env object to use (see django-environ)
    :param default_value: value to return if not found
    :return: value assigned to key or default value
    """
    if key in os.environ:
        return os.environ[key]

    return env_obj(key, default=default_value)


# import ldap
# from django_auth_ldap.config import (
#     LDAPSearch,
#     GroupOfNamesType,
#     LDAPGroupQuery
# )

# CONFIGURATION VARIABLES (Os Environment)
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = get_from_os_or_env('AWS_ACCESS_KEY_ID', env)
AWS_SECRET_ACCESS_KEY = get_from_os_or_env('AWS_SECRET_ACCESS_KEY', env)
AWS_STORAGE_BUCKET_NAME = get_from_os_or_env('AWS_STORAGE_BUCKET_NAME', env)
AWS_LOCATION = get_from_os_or_env('AWS_LOCATION', env, 'static')

BASE_URL = get_from_os_or_env('BASE_URL', env)

DATAOPS_PLUGIN_DIRECTORY = get_from_os_or_env(
    'DATAOPS_PLUGIN_DIRECTORY',
    env,
    '')

DOMAIN_NAME = get_from_os_or_env('DOMAIN_NAME', env, 'localhost')

LOG_FOLDER = get_from_os_or_env('LOG_FOLDER', env)

MEDIA_LOCATION = get_from_os_or_env('MEDIA_LOCATION', env, '/media/')

# Database parameters
RDS_DB_NAME = get_from_os_or_env('RDS_DB_NAME', env)
RDS_USERNAME = get_from_os_or_env('RDS_USERNAME', env)
RDS_PASSWORD = get_from_os_or_env('RDS_PASSWORD', env)
RDS_HOSTNAME = get_from_os_or_env('RDS_HOSTNAME', env)
RDS_PORT = get_from_os_or_env('RDS_PORT', env)

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not defined
SECRET_KEY = get_from_os_or_env('SECRET_KEY', env, '')

# Frequency to run the session clearsession command
SESSION_CLEANUP_CRONTAB = get_from_os_or_env(
    'SESSION_CLEANUP_CRONTAB',
    env,
    '05 5 6 * *')

STATIC_URL_SUFFIX = get_from_os_or_env('STATIC_URL_SUFFIX', env, 'static')

TIME_ZONE = get_from_os_or_env('TIME_ZONE', env, 'UTC')

# CONFIGURATION VARIABLES (Conf File)
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
DATABASE_URL = env.db()
DEBUG = env.bool('DEBUG', default=False)

# JSON execution
EXECUTE_ACTION_JSON_TRANSFER = env.bool(
    'EXECUTE_ACTION_JSON_TRANSFER',
    default=False)

# CACHE
# ------------------------------------------------------------------------------
REDIS_URL = env.cache(
    'REDIS_URL',
    default='redis://localhost:6379/'
            + '?client_class=django_redis.client.DefaultClient'
            + '&timeout=1000'
            + '&key_prefix=ontask'
)

# Login page
SHOW_HOME_FOOTER_IMAGE = env.bool('SHOW_HOME_FOOTER_IMAGE', default=False)

# USE SSL
USE_SSL = env.bool('USE_SSL', default=False)

# Additional variables
# ------------------------------------------------------------------------------
# Path to the src folder
BASE_DIR = environ.Path(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

if not DATAOPS_PLUGIN_DIRECTORY:
    DATAOPS_PLUGIN_DIRECTORY = os.path.join(
        BASE_DIR(),
        'lib',
        'plugins')

# Locale paths
LOCALE_PATHS = [join(BASE_DIR(), 'locale')]

# Variable flagging that this is a test enviromnet
ONTASK_TESTING = sys.argv[1:2] == ['test']

# Log everything to the logs directory at the top
if not LOG_FOLDER:
    LOG_FOLDER = join(BASE_DIR(), 'logs')

MEDIA_ROOT = join(BASE_DIR(), 'media')
if AWS_ACCESS_KEY_ID:
    MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, MEDIA_LOCATION)
else:
    MEDIA_URL = BASE_URL + MEDIA_LOCATION

if AWS_ACCESS_KEY_ID:
    STATICFILES_DIRS = [join(BASE_DIR(), AWS_LOCATION)]
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
else:
    STATICFILES_DIRS = [join(BASE_DIR(), STATIC_URL_SUFFIX)]
    STATIC_URL = BASE_URL + '/' + STATIC_URL_SUFFIX + '/'

STATIC_ROOT = join(BASE_DIR(), 'site', 'static')

# URL pointing to the documentation
ONTASK_HELP_URL = "html/index.html"

TEMPLATES = [
    {
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
                    'ontask.visualizations.templatetags.vis_include',
            }}}]

# Application definition
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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

AUTHENTICATION_BACKENDS = [
    'ontask.django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    # 'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend'
]

CACHES = {"default": REDIS_URL}
# Cache time to live is 15 minutes
CACHE_TTL = 60 * 30

# CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = []
# CORS_ORIGIN_REGEX_WHITELIST = []

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
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '1000/minute'
    }
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
}

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

if 'RDS_DB_NAME' in os.environ:
    # Cater for AWS-style RDS definition in containers
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': RDS_DB_NAME,
            'USER': RDS_USERNAME,
            'PASSWORD': RDS_PASSWORD,
            'HOST': RDS_HOSTNAME,
            'PORT': RDS_PORT,
        },
    }
else:
    DATABASES = {'default': DATABASE_URL, }

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Crispy Form Theme - Bootstrap 4
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# For Bootstrap 3, change error alert to 'danger'
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_LEVEL = message_constants.DEBUG
MESSAGE_TAGS = {messages.ERROR: 'danger'}

LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGIN_URL = reverse_lazy('accounts:login')

THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails

IMPORT_EXPORT_USE_TRANSACTIONS = True

SITE_ID = 1

# Authentication Settings
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'authtools.User'

# Internationalization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
LANGUAGES = (
    ('en-us', _('English')),
    ('es-es', _('Spanish')),
    ('zh-cn', _('Chinese')),
    ('fi', _('Finnish')),
    ('ru', _('Russian')),
)

# LOGGER (modified further in development.py/production.py)
# ------------------------------------------------------------------------------
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

# SUMMERNOTE CONFIGURATION
# ------------------------------------------------------------------------------
SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'iframe': False,
    'summernote': {
        'width': '100%',
        'height': '400px',
        'disableDragAndDrop': True,
    },
    'css': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/'
        + 'theme/base16-dark.min.css',
    ),
    'css_for_inplace': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/'
        + 'theme/base16-dark.min.css',
    ),
    'codemirror': {
        'theme': 'base16-dark',
        'mode': 'htmlmixed',
        'lineNumbers': True,
        'lineWrapping': True,
    },
    # Disable attachment feature so all images are inlined
    'disable_attachment': True,
    'lazy': True,
}

# DATA UPLOAD FILES
# ------------------------------------------------------------------------------
DATAOPS_CONTENT_TYPES = '["text/csv", "application/json", ' \
                        '"application/gzip", "application/x-gzip", ' \
                        '"application/vnd.ms-excel"]'
DATAOPS_MAX_UPLOAD_SIZE = env.int('DATAOPS_MAX_UPLOAD_SIZE', default=209715200)

# Raise because default of 1000 is too short
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Disabled actions
# ------------------------------------------------------------------------------
DISABLED_ACTIONS = [
    # 'models.Action.PERSONALIZED_TEXT',
    # 'models.Action.PERSONALIZED_JSON',
    # 'models.Action.PERSONALIZED_CANVAS_EMAIL',
    # 'models.Action.EMAIL_REPORT',
    # 'models.Action.JSON_REPORT',
    # 'models.Action.SURVEY',
    'models.Action.TODO_LIST',
]

# Log configuration
# ------------------------------------------------------------------------------
LOGS_MAX_LIST_SIZE = 200
SHORT_DATETIME_FORMAT = 'r'

# CELERY parameters
# ------------------------------------------------------------------------------
CELERY_BROKER_URL = REDIS_URL['LOCATION']
CELERY_RESULT_BACKEND = REDIS_URL['LOCATION']
CELERY_ACCEPT_CONTENT = ['application/json', 'pickle']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CLEAN_SESSION_TASK_NAME = '__ONTASK_CLEANUP_SESSION_TASK'
CRONTAB_ITEMS = SESSION_CLEANUP_CRONTAB.split()
CELERY_BEAT_SCHEDULE = {
    'ontask_scheduler': {
        'task': 'ontask.tasks.session_cleanup.session_cleanup',
        'schedule': crontab(
            minute=CRONTAB_ITEMS[0],
            hour=CRONTAB_ITEMS[1],
            day_of_week=CRONTAB_ITEMS[2],
            day_of_month=CRONTAB_ITEMS[3],
            month_of_year=CRONTAB_ITEMS[4]),
        #     'args': (DEBUG,),
        'name': CLEAN_SESSION_TASK_NAME,
    },
}
CELERY_TASK_ALWAYS_EAGER = ONTASK_TESTING

# Email sever configuration
# ------------------------------------------------------------------------------
# Host, port, user and password to open the communication thorugh SMTP
# EMAIL
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env('EMAIL_PORT', default='')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
# The from field when sending notification messages
EMAIL_ACTION_NOTIFICATION_SENDER = env(
    'EMAIL_ACTION_NOTIFICATION_SENDER',
    default='')
# Include HTML only email or HTML and text
EMAIL_HTML_ONLY = env.bool('EMAIL_HTML_ONLY', default=True)
# Use of TLS or SSL (see Django configuration)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
# Number of emails to send out in a burst (before pausing)
EMAIL_BURST = env.int('EMAIL_BURST', default=0)
# Pause between bursts (in seconds)
EMAIL_BURST_PAUSE = env.int('EMAIL_BURST_PAUSE', default=0)

# Additional email related variables
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

EMAIL_ACTION_NOTIFICATION_SUBJECT = _('OnTask: Action executed')
EMAIL_ACTION_PIXEL = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC' \
                     '0lEQVR4nGP6zwAAAgcBApocMXEAAAAASUVORK5CYII='

# LTI Authentication
# ------------------------------------------------------------------------------
#
# In the next variable define a dictionary with name:secret pairs.
#
LTI_OAUTH_CREDENTIALS = env.dict('LTI_OAUTH_CREDENTIALS', default={})
LTI_INSTRUCTOR_GROUP_ROLES = env.list(
    'LTI_INSTRUCTOR_GROUP_ROLES',
    default=['Instructor'])

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
CANVAS_INFO_DICT = json.loads(env.str('CANVAS_INFO_DICT', default='{}'))
# Number of seconds left in the token validity to refresh
CANVAS_TOKEN_EXPIRY_SLACK = env.int('CANVAS_TOKEN_EXPIRY_SLACK', default=600)

# LDAP AUTHENTICATION
# ------------------------------------------------------------------------------
# Variables taken from local.env
# AUTH_LDAP_SERVER_URI = get_from_os_or_env('AUTH_LDAP_SERVER_URI', env)
# AUTH_LDAP_BIND_PASSWORD = get_from_os_or_env('AUTH_LDAP_BIND_PASSWORD', env)

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
