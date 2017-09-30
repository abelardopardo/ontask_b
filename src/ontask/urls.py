# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import profiles.urls
import accounts.urls
import workflow.urls
import dataops.urls
import action.urls
import email_action.urls
import logs.urls

# import matrix.urls

from . import views

urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home'),
    url(r'^about/$', views.AboutPage.as_view(), name='about'),
    url(r'^users/', include(profiles.urls, namespace='profiles')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(accounts.urls, namespace='accounts')),
    url(r'^workflow/', include(workflow.urls, namespace='workflow')),
    url(r'^dataops/', include(dataops.urls, namespace='dataops')),
    url(r'^action/', include(action.urls, namespace='action')),
    # url(r'^matrix/', include(matrix.urls, namespace='matrix')),
    url(r'^email_action/', include(email_action.urls,
                                   namespace='email_action')),
    url(r'^logs/', include(logs.urls, namespace='logs')),

    url(r'^tobedone/', views.ToBeDone.as_view(), name='tobedone'),

    url(r'^tinymce/', include('tinymce.urls')),

]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
