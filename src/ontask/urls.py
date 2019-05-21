# -*- coding: utf-8 -*-

"""First entry point to define URLs."""

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sites.models import Site
from django.urls import path
from django.utils.translation import ugettext
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog
from rest_framework.documentation import include_docs_urls

import accounts.urls
import action.urls
import dataops.urls
import logs.urls
import ontask_oauth.urls
import profiles.urls
import scheduler.urls
import table.urls
import workflow.urls
from dataops.pandas import set_engine
from ontask import views
from ontask.templatetags.ontask_tags import ontask_version

api_description = ugettext(
    'The OnTask API offers functionality to manipulate workflows, tables '
    + 'and logs. The interface provides CRUD operations over these '
    + 'objects.')

urlpatterns = [
    # Home Page!
    path('', views.home, name='home'),

    path('lti_entry', views.lti_entry, name='lti_entry'),

    path('not_authorized', views.home, name='not_authorized'),

    path('about', views.AboutPage.as_view(), name='about'),

    path(
        'under_construction',
        views.under_construction,
        name='under_construction'),

    path('users', include(profiles.urls, namespace='profiles')),

    path('admin', admin.site.urls),

    path('trck', views.trck, name='trck'),

    path('keep_alive', views.keep_alive, name='keep_alive'),

    path('', include(accounts.urls, namespace='accounts')),

    path('workflow/', include(workflow.urls, namespace='workflow')),

    path('dataops/', include(dataops.urls, namespace='dataops')),

    path('action/', include(action.urls, namespace='action')),

    path('table/', include(table.urls, namespace='table')),

    path('scheduler/', include(scheduler.urls, namespace='scheduler')),

    path('logs/', include(logs.urls, namespace='logs')),

    path('summernote/', include('django_summernote.urls')),

    path(
        'ontask_oauth/',
        include(ontask_oauth.urls,
                namespace='ontask_oauth')),

    path('tobedone', views.ToBeDone.as_view(), name='tobedone'),

    # API AUTH and DOC
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    path(
        'apidoc/',
        include_docs_urls(
            title='OnTask API',
            description=api_description,
            public=False),
    ),
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

    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]

handler400 = 'ontask.views.ontask_handler400'
handler403 = 'ontask.views.ontask_handler403'
handler404 = 'ontask.views.ontask_handler404'
handler500 = 'ontask.views.ontask_handler500'

# Create the DB engine with SQLAlchemy (once!)
set_engine()

# Make sure the Site has the right information
try:
    site = Site.objects.get(id=settings.SITE_ID)
    site.domain = settings.DOMAIN_NAME
    site.name = settings.DOMAIN_NAME
    site.save()
except Exception:
    # To bypass the migrate command execution that fails because the Site
    # table is not created yet.
    site = None
