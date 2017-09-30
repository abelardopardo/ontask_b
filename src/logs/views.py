# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, reverse, render
import django_tables2 as tables
from django_tables2 import RequestConfig, SingleTableView
from django_filters.views import FilterView
from django_filters import FilterSet

from ontask import is_instructor, decorators
from .models import Log


class LogTable(tables.Table):

    # def render_payload(self):
    #     return 'payloaddd'

    class Meta:
        model = Log
        sequence = ('id', 'created', 'user', 'name', 'payload')

        attrs = {
            'class': 'table table-stripped table-bordered table-hover',
            'id': 'log-table'
        }


@login_required
@user_passes_test(is_instructor)
def show(request):

    queryset = Log.objects.filter(user=request.user)

    table = LogTable(queryset,
                     # exclude=['payload'],
                     )

    RequestConfig(request, paginate={'per_page': 15}).configure(table)

    return render(request, 'logs/show.html', {'table': table})


class LogFilter(FilterSet):
    class Meta:
        model = Log
        fields = ['user', 'name', 'created']


class LogFilteredListView(FilterView, SingleTableView):
    table_class = LogTable
    model = Log
    template_name = 'logs/show.html'

    filterset_class = LogFilter
