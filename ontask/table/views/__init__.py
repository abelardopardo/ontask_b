# -*- coding: utf-8 -*-

"""Viewing table and views."""
from ontask.table.views.csvdownload import csvdownload, csvdownload_view
from ontask.table.views.stats import ColumnStatsModalView, ColumnStatsView
from ontask.table.views.table_display import (
    TableDiplayCompleteView, TableDisplayCompleteSSView, TableDisplayViewSSView,
    TableDisplayViewView, TableRowDeleteView)
from ontask.table.views.table_view import (
    ViewAddView, ViewCloneView, ViewDeleteView, ViewEditView)
