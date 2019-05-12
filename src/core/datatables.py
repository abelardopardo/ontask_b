# -*- coding: utf-8 -*-

"""Various functions to support DataTables."""


class DataTablesServerSidePaging(object):
    """Class to handle DataTables Server Side Paging request.

    For large tables DataTables allows to pre-load a subset of a table
    that is requested through AJAX. These requests arrive with a set of
    paging parameters that are stored in these objects.
    """

    draw: int = 0
    start: int = 0
    order_column = None
    order_direction = None
    search_value = None
    is_valid = True

    def __init__(self, request_data):
        """Extract the data from the request."""
        try:
            self.draw = int(request_data.POST.get('draw'))
            self.start = int(request_data.POST.get('start'))
            self.length = int(request_data.POST.get('length'))
            self.order_col = request_data.POST.get('order[0][column]')
            self.order_dir = request_data.POST.get('order[0][dir]', 'asc')
            self.search_value = request_data.POST.get('search[value]')
        except ValueError:
            self.is_valid = False

        if self.order_col:
            self.order_col = int(self.order_col)
