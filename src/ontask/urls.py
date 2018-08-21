# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog
from rest_framework.documentation import include_docs_urls

import accounts.urls
import action.urls
import dataops.urls
import logs.urls
import profiles.urls
import scheduler.urls
import table.urls
import workflow.urls
from dataops import pandas_db
from templatetags.settings import ontask_version
from . import views

api_description = _("""The OnTask API offers functionality to manipulate 
workflows, tables and logs. The interface provides CRUD operations over 
these objects.""")

urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home'),

    url(r'^entry$', views.entry, name='entry'),

    url(r'^lti_entry$', views.lti_entry, name='lti_entry'),

    url(r'^not_authorized$', views.HomePage.as_view(), name='not_authorized'),

    url(r'^about/$', views.AboutPage.as_view(), name='about'),

    url(r'^users/', include(profiles.urls, namespace='profiles')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^trck/', views.trck, name='trck'),

    url(r'^keep_alive/', views.keep_alive, name='keep_alive'),

    url(r'^', include(accounts.urls, namespace='accounts')),

    url(r'^workflow/', include(workflow.urls, namespace='workflow')),

    url(r'^dataops/', include(dataops.urls, namespace='dataops')),

    url(r'^action/', include(action.urls, namespace='action')),

    url(r'^table/', include(table.urls, namespace='table')),

    url(r'^scheduler/', include(scheduler.urls, namespace='scheduler')),

    url(r'^logs/', include(logs.urls, namespace='logs')),

    url(r'^summernote/', include('django_summernote.urls')),

    url(r'^tobedone/', views.ToBeDone.as_view(), name='tobedone'),

    # API AUTH and DOC
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^apidoc/',
        include_docs_urls(
            title='OnTask API',
            description=api_description,
            public=False),
        ),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(r'^jsi18n/$',
        cache_page(86400, key_prefix='js18n-%s' % ontask_version())(
            JavaScriptCatalog.as_view()),
        name='javascript-catalog'),
)

# Include django debug toolbar if DEBUG is ons
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler400 = 'ontask.views.ontask_handler400'
handler403 = 'ontask.views.ontask_handler403'
handler404 = 'ontask.views.ontask_handler404'
handler500 = 'ontask.views.ontask_handler500'

# Create the DB engine with SQLAlchemy (once!)
pandas_db.engine = pandas_db.create_db_engine(
    'postgresql',
    '+psycopg2',
    settings.DATABASES['default']['USER'],
    settings.DATABASES['default']['PASSWORD'],
    settings.DATABASES['default']['HOST'],
    settings.DATABASES['default']['NAME'],
)

# Make sure the Site has the right information
try:
    site = Site.objects.get(pk=settings.SITE_ID)
    site.domain = settings.DOMAIN_NAME
    site.name = settings.DOMAIN_NAME
    site.savse()
except Exception:
    # To bypass the migrate command execution that fails because the Site
    # table is not created yet.
    pass