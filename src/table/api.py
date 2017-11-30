# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from dataops import pandas_db, ops
from table.serializers import (
    DataFramePandasMergeSerializer,
    DataFramePandasSerializer,
    DataFrameJSONSerializer,
    DataFrameJSONMergeSerializer)
from ontask.permissions import UserIsInstructor
from workflow.models import Workflow
from workflow.ops import is_locked, detach_dataframe


class TableBasicOps(APIView):
    """
    Basic class to implement the table API operations so that we can provide
    two versions, one handling data frames in JSON format, and the other one
    using the pickle format in Pandas to preserve NaN and NaT and maintain
    column data types between exchanges.
    """

    # The serializer class needs to be overwritten by the subclasses.
    serializer_class = None
    permission_classes = (UserIsInstructor,)

    def get_object(self, pk, **kwargs):
        user = kwargs['user']
        try:
            if user.is_superuser:
                workflow = Workflow.objects.get(pk=pk)
            else:
                workflow = Workflow.objects.filter(
                    Q(user=self.request.user) |
                    Q(shared__id=self.request.user.id)
                ).distinct().get(id=pk)
        except Workflow.DoesNotExist:
            raise APIException('Incorrect object')

        if is_locked(workflow):
            raise APIException('Workflow is locked by another user')

        return workflow

    def override(self, request, pk, format=None):
        # Try to retrieve the wflow to check for permissions
        self.get_object(pk, user=self.request.user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            df = serializer.validated_data['data_frame']

            ops.store_dataframe_in_db(df, pk)

            return Response(None,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    # Retrieve
    def get(self, request, pk, format=None):
        # Try to retrieve the wflow to check for permissions
        self.get_object(pk, user=self.request.user)
        serializer = self.serializer_class(
            {'data_frame': pandas_db.load_from_db(pk)}
        )
        return Response(serializer.data)

    # Create
    def post(self, request, pk, format=None):
        # If there is a table in the workflow, ignore the request
        if pandas_db.load_from_db(pk) is not None:
            raise APIException('Post request requires workflow without '
                               'a table')
        return self.override(request, pk, format)

    # Update
    def put(self, request, pk, format=None):
        return self.override(request, pk, format)

    # Delete
    def delete(self, request, pk, format=None):
        wflow = self.get_object(pk, user=self.request.user)
        detach_dataframe(wflow)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TableJSONOps(TableBasicOps):
    """
    get:
    Get all the data in the table corresponding to the workflow (no matter
    how big). If the workflow has no data, an empty {} is returned.

    post:
    Upload a new table to a workflow without. If there is a table already, the
    operation will be rejected (consider deleting the table first or use PUT)

    put:
    Replace the table currently in the workflow with the one given

    delete:
    Flush the data frame from the workflow. The workflow object remains, just
    the data frame is deleted.
    """

    serializer_class = DataFrameJSONSerializer


class TablePandasOps(TableBasicOps):
    """
    This API is provided because OnTask stores the table internally as a
    Pandas data frame. When using conventional API transactions using JSON
    strings, it is possible to loose information because JSON cannot handle
    NaN or NaT (specific values for Pandas data frames).

    For example, if a column has boolean values and a NaN and it is
    transformed to JSON and transmitted, the NaN will be encoded as an empty
    string, and the column will no longer contain booleans but strings.
    Similar situations ocurr with integers, dates, etc.

    Use this API when you require to have a consisten handling of NaN and NaT.

    The code to handle the Base64 encoded data in Python is:

    1) From Pandas dataframe to base64 encoded string:

    import StringIO
    import base64
    import pandas

    out_file = StringIO.StringIO()
    pandas.to_pickle(data_frame, out_file)
    result = base64.b64encode(out_file.getvalue())

    2) From base64 encoded string to pandas dataframe

    import StringIO
    import base64
    import pandas

    output = StringIO.StringIO()
    output.write(base64.b64decode(encoded_dataframe))
    result = pandas.read_pickle(output)

    These are the methods made available by the API

    get:
    Get all the data in the table corresponding to the workflow (no matter
    how big) as a Base64 encoded string of the binary data frame. If the
    workflow has no data, an empty {} is returned.

    post:
    Upload a new table (Base64 encoded of a binary data frame) to a workflow
    without. If there is a table already, the operation will be rejected
    (consider deleting the table first or use PUT)

    put:
    Replace the table currently in the workflow with the one given Base64
    encoded string of the binary representation of a pandas data frame.
    """

    serializer_class = DataFramePandasSerializer


class TableBasicMerge(APIView):
    """
    These are basic merge methods to be invoked by the subclasses
    get:
    Retrieves the data frame attached to the workflow and returns it labeled
    as "data_frame"

    post:
    Request to merge a given data frame with the one attached to the workflow.
    """

    serializer_class = None
    permission_classes = (UserIsInstructor,)

    def get_object(self, pk, **kwargs):
        user = kwargs['user']
        try:
            if user.is_superuser:
                workflow = Workflow.objects.get(pk=pk)
            else:
                workflow = Workflow.objects.filter(
                    Q(user=self.request.user) |
                    Q(shared__id=self.request.user.id)
                ).distinct().get(id=pk)
        except Workflow.DoesNotExist:
            raise APIException('Incorrect object')

        if is_locked(workflow):
            raise APIException('Workflow is locked by another user')

        return workflow

    # Retrieve
    def get(self, request, pk, format=None):
        # Try to retrieve the wflow to check for permissions
        self.get_object(pk, user=self.request.user)
        serializer = self.serializer_class(
            {'src_df': pandas_db.load_from_db(pk),
             'how': '',
             'left_on': '',
             'right_on': '',
             'dup_column': ''}
        )
        return Response(serializer.data)

    # Update
    def put(self, request, pk, format=None):
        # Try to retrieve the wflow to check for permissions
        self.get_object(pk, user=self.request.user)
        # Get the dst_df
        dst_df = pandas_db.load_from_db(pk)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        # Check that the parameters are correct
        how = serializer.validated_data['how']
        if how == '' or how not in ['left', 'right', 'outer', 'inner']:
            raise APIException('how must be one of left, right, outer '
                               'or inner')

        left_on = serializer.validated_data['left_on']
        if not ops.is_unique_column(dst_df[left_on]):
            raise APIException('column' + left_on +
                               'does not contain a unique key.')

        # Operation has been accepted by the serializer
        src_df = serializer.validated_data['src_df']

        right_on = serializer.validated_data['right_on']
        if right_on not in list(src_df.columns):
            raise APIException('column ' + right_on +
                               ' not found in data frame')

        if not ops.is_unique_column(src_df[right_on]):
            raise APIException('column' + right_on +
                               'does not contain a unique key.')

        dup_column = serializer.validated_data['dup_column']
        if dup_column == '' or dup_column not in ['override', 'rename']:
            raise APIException('dup_column must be override or rename')

        override_columns_names = []
        autorename_column_names = None
        if dup_column == 'override':
            # List of columns to drop (the ones in both data sets
            override_columns_names = list(
                (set(dst_df.columns) & set(src_df.columns)) -
                {left_on}
            )
        else:
            autorename_column_names = []
            for colname in list(src_df.columns):
                # If the column is the key, insert as is
                if colname == right_on:
                    autorename_column_names.append(colname)
                    continue

                # If the column does not collide, insert as is
                if colname not in dst_df.columns:
                    autorename_column_names.append(colname)
                    continue

                # Column name collides with existing column
                i = 0  # Suffix to rename
                while True:
                    i += 1
                    new_name = colname + '_{0}'.format(i)
                    if new_name not in dst_df.columns:
                        break
                autorename_column_names.append(new_name)

        merge_info = {
            'how_merge': how,
            'dst_selected_key': left_on,
            'src_selected_key': right_on,
            'initial_column_names': list(src_df.columns),
            'autorename_column_names': autorename_column_names,
            'rename_column_names': list(src_df.columns),
            'columns_to_upload': [True] * len(list(src_df.columns)),
            'override_columns_names': override_columns_names
        }

        # Ready to perform the MERGE
        try:
            merge_result = ops.perform_dataframe_upload_merge(pk,
                                                              dst_df,
                                                              src_df,
                                                              merge_info)
        except Exception:
            raise APIException('Unable to perform merge operation')

        if merge_result:
            # Something went wrong, raise the exception
            raise APIException(merge_result)

        # Merge went through.
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class TableJSONMerge(TableBasicMerge):
    """
    get:
    Retrieves the data frame attached to the workflow and returns it labeled
    as "data_frame"

    post:
    Request to merge a given data frame with the one attached to the workflow.
    """

    serializer_class = DataFrameJSONMergeSerializer


class TablePandasMerge(TableBasicMerge):
    """
    This API is provided because OnTask stores the table internally as a
    Pandas data frame. When using conventional API transactions using JSON
    strings, it is possible to loose information because JSON cannot handle
    NaN or NaT (specific values for Pandas data frames).

    For example, if a column has boolean values and a NaN and it is
    transformed to JSON and transmitted, the NaN will be encoded as an empty
    string, and the column will no longer contain booleans but strings.
    Similar situations ocurr with integers, dates, etc.

    Use this API when you require to have a consisten handling of NaN and NaT.

    The code to handle the Base64 encoded data in Python is:

    <ol>
    <li>From Pandas dataframe to base64 encoded string:

    <pre>
    import StringIO
    import base64
    import pandas

    out_file = StringIO.StringIO()
    pandas.to_pickle(data_frame, out_file)
    result = base64.b64encode(out_file.getvalue())
    </pre>

    </li>
    <li>From base64 encoded string to pandas dataframe

    <pre>
    import StringIO
    import base64
    import pandas

    output = StringIO.StringIO()
    output.write(base64.b64decode(encoded_dataframe))
    result = pandas.read_pickle(output)
    </pre>
    </li>
    </ol>

    These are the methods made available by the API

    get:
    Retrieves the data frame attached to the workflow and returns it labeled
    as "src_df" as a Base64 encoded pandas pickled dataa frame.

    post:
    Request to merge a pandas data frame given as a Base64 encoded pickled
    string with the one attached to the workflow.
    """

    # To be overwritten by the subclass
    serializer_class = DataFramePandasMergeSerializer
