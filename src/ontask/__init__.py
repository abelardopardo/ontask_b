# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import re

__version__ = 'B.2.1.1'


class OntaskException(Exception):
    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return repr(self.value)

