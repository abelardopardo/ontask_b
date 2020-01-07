# -*- coding: utf-8 -*-

"""First entry point to define URLs."""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sites.models import Site
from django.urls import path, re_path
from django.utils.translation import ugettext
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from drf_yasg import openapi
from drf_yasg.renderers import SwaggerUIRenderer
from drf_yasg.views import get_schema_view
from rest_framework import permissions

import ontask
from ontask import models
from ontask.core import views
from ontask.dataops import pandas
from ontask.templatetags.ontask_tags import ontask_version

api_description = ugettext(
    'The OnTask API offers functionality to manipulate workflows, tables '
    + 'and logs. The interface provides CRUD operations over these '
    + 'objects.')

SwaggerUIRenderer.template = 'api_ui.html'

schema_view = get_schema_view(
    openapi.Info(
        title='OnTask API',
        default_version=ontask.__version__,
        description=api_description),
    public=True,
    permission_classes=(permissions.AllowAny,))

urlpatterns = [
    # Home Page!
    path('', views.home, name='home'),
    path('lti_entry', views.lti_entry, name='lti_entry'),
    path('not_authorized', views.home, name='not_authorized'),
    path(
        'under_construction',
        TemplateView.as_view(template_name='under_construction.html'),
        name='under_construction'),
    path('users', include('ontask.profiles.urls', namespace='profiles')),
    path('ota', admin.site.urls),
    path('trck', views.trck, name='trck'),
    path('keep_alive', views.keep_alive, name='keep_alive'),
    path('', include('ontask.accounts.urls', namespace='accounts')),
    path('workflow/', include('ontask.workflow.urls', namespace='workflow')),
    path('column/', include('ontask.column.urls', namespace='column')),
    path('dataops/', include('ontask.dataops.urls', namespace='dataops')),
    path('action/', include('ontask.action.urls', namespace='action')),
    path('table/', include('ontask.table.urls', namespace='table')),
    path(
        'scheduler/',
        include('ontask.scheduler.urls', namespace='scheduler')),
    path('logs/', include('ontask.logs.urls', namespace='logs')),
    path('summernote/', include('django_summernote.urls')),
    path(
        'ontask_oauth/',
        include('ontask.oauth.urls', namespace='ontask_oauth')),
    path('tobedone', views.ToBeDone.as_view(), name='tobedone'),
    # API AUTH
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    # API Doc
    re_path(
        r'apidoc(?P<format>\.json|\.yaml)',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'),
    path(
        r'apidoc/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='ontask-api-doc'),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path(
        'jsi18n',
        cache_page(
            86400,
            key_prefix='js18n-%s' % ontask_version())(
            JavaScriptCatalog.as_view()),
        name='javascript-catalog',
    ),
)

# Include django debug toolbar if DEBUG is ons
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path(r'__debug__/', include(debug_toolbar.urls))]

handler400 = 'ontask.core.services.ontask_handler400'
handler403 = 'ontask.core.services.ontask_handler403'
handler404 = 'ontask.core.services.ontask_handler404'
handler500 = 'ontask.core.services.ontask_handler500'

# Create the DB engine with SQLAlchemy (once!)
pandas.set_engine()

# Make sure the Site has the right information
try:
    Site.objects.filter(id=settings.SITE_ID).update(
        domain=settings.DOMAIN_NAME,
        name=settings.DOMAIN_NAME)
except Exception:
    # To bypass the migrate command execution that fails because the Site
    # table is not created yet.
    site = None

# Remove from AVAILABLE_ACTION_TYPES those in DISABLED_ACTIONS
try:
    eval_obj = [eval(daction) for daction in settings.DISABLED_ACTIONS]
    for atype in eval_obj:
        to_remove = next(
            afull_type for afull_type in models.Action.ACTION_TYPES.keys()
            if atype == afull_type)
        models.Action.AVAILABLE_ACTION_TYPES.pop(to_remove)
except Exception as exc:
    raise Exception(
        'Unable to configure available action types. '
        + 'Review variable DISABLED_ACTIONS')
