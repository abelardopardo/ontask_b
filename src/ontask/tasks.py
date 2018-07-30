# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ontask.celery import app

@app.task
def add(x, y):
    return x + y

