# -*- coding: utf-8 -*-

"""Functions implementing the API calls to manipulate the table."""
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from ontask import OnTaskDataFrameNoKey, models
from ontask.core import UserIsInstructor, get_workflow
from ontask.dataops import pandas
from ontask.table import serializers


class TableBasicOps(APIView):
    """Basic class to implement the table API operations.

    Inheritance will implement two versions, one handling data frames in JSON
    format, and the other one using the pickle format in Pandas to preserve
    NaN and NaT and maintain column data types between exchanges.
    """

    # The serializer class needs to be overwritten by the subclasses.
    serializer_class = None

    permission_classes = (UserIsInstructor,)

    @method_decorator(get_workflow(pf_related='columns'))
    def override(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Override the content in the workflow.

        :param request: Received request object
        :param wid: Workflow ID
        :param format: format for the response
        :param workflow: Workflow being manipulated (set by decorator)
        """
        del wid, format
        # Try to retrieve the wflow to check for permissions
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            # Flag the error
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        # Data received is a correct data frame.
        df = serializer.validated_data['data_frame']

        try:
            # Verify the data frame
            pandas.verify_data_frame(df)
            # Store the content in the db and...
            pandas.store_dataframe(df, workflow)
        except OnTaskDataFrameNoKey as exc:
            return Response(
                str(exc),
                status=status.HTTP_400_BAD_REQUEST)

        # Update all the counters in the conditions
        for action in workflow.actions.all():
            action.update_n_rows_selected()

        return Response(None, status=status.HTTP_201_CREATED)

    @method_decorator(get_workflow(pf_related='columns'))
    def get(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Retrieve the existing data frame."""
        del request, wid, format
        serializer = self.serializer_class(
            {
                'data_frame': pandas.load_table(
                    workflow.get_data_frame_table_name())})
        return Response(serializer.data)

    @method_decorator(get_workflow(pf_related='columns'))
    def post(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Create a new data frame."""
        if pandas.load_table(workflow.get_data_frame_table_name()) is not None:
            raise APIException(
                _('Post request requires workflow without a table'))
        return self.override(
            request,
            wid=wid,
            format=format,
            workflow=workflow)

    @method_decorator(get_workflow(pf_related='columns'))
    def put(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ):
        """Process the put method to update the data frame."""
        return self.override(
            request,
            wid=wid,
            format=format,
            workflow=workflow)

    # Delete
    @method_decorator(get_workflow(pf_related='columns'))
    def delete(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Flush the data in the data frame."""
        del request, wid, format
        workflow.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TableJSONOps(TableBasicOps):
    """Class to provide a JSON serialization of the data frame.

    The purpose of the methods are:

    - get: Get all the data in the table corresponding to the workflow (no
    matter how big). If the workflow has no data, an empty dictionary is
    returned.

    - post: Upload a new table to a workflow without. If there is a table
    already, the operation will be rejected (consider deleting the table
    first or use PUT)

    - put: Replace the table currently in the workflow with the one given

    - delete: Flush the data frame from the workflow. The workflow object
    remains, just the data frame is deleted.
    """

    serializer_class = serializers.DataFrameJSONSerializer


class TablePandasOps(TableBasicOps):
    """API to store a table internally as a data frame.

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

    out_file = StringIO()
    pandas.to_pickle(data_frame, out_file)
    result = base64.b64encode(out_file.getvalue())

    2) From base64 encoded string to pandas dataframe

    import StringIO
    import base64
    import pandas

    output = StringIO()
    output.write(base64.b64decode(encoded_dataframe))
    result = pandas.read_pickle(output)

    These are the methods made available by the API

    get: Get all the data in the table corresponding to the workflow (no
    matter how big) as a Base64 encoded string of the binary data frame. If
    the workflow has no data, an empty dictionary is returned.

    post: Upload a new table (Base64 encoded of a binary data frame) to a
    workflow without. If there is a table already, the operation will be
    rejected (consider deleting the table first or use PUT)

    put: Replace the table currently in the workflow with the one given Base64
    encoded string of the binary representation of a pandas data frame.
    """

    serializer_class = serializers.DataFramePandasSerializer


class TableBasicMerge(APIView):
    """Basic table merge methods.

    get:
    Retrieves the data frame attached to the workflow and returns it labeled
    as "data_frame"

    post:
    Request to merge a given data frame with the one attached to the workflow.
    """

    serializer_class = None

    permission_classes = (UserIsInstructor,)

    # Retrieve
    @method_decorator(get_workflow(pf_related='columns'))
    def get(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Process the GET request."""
        del request, wid, format
        # Try to retrieve the wflow to check for permissions
        serializer = self.serializer_class({
            'src_df': pandas.load_table(workflow.get_data_frame_table_name()),
            'how': '',
            'left_on': '',
            'right_on': ''})
        return Response(serializer.data)

    # Update
    @method_decorator(get_workflow(pf_related='columns'))
    def put(
        self,
        request: HttpRequest,
        wid: int,
        format=None,
        workflow: Optional[models.Workflow] = None,
    ) -> HttpResponse:
        """Process the put request."""
        del wid, format
        # Get the dst_df
        dst_df = pandas.load_table(workflow.get_data_frame_table_name())

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        # Check that the parameters are correct
        how = serializer.validated_data['how']
        if how == '' or how not in ['left', 'right', 'outer', 'inner']:
            raise APIException(
                _('how must be one of left, right, outer or inner'))

        left_on = serializer.validated_data['left_on']
        if not pandas.is_unique_column(dst_df[left_on]):
            raise APIException(
                _('column {0} does not contain a unique key.').format(left_on))

        # Operation has been accepted by the serializer
        src_df = serializer.validated_data['src_df']

        right_on = serializer.validated_data['right_on']
        if right_on not in list(src_df.columns):
            raise APIException(_('column {0} not found in data frame').format(
                right_on))

        if not pandas.is_unique_column(src_df[right_on]):
            raise APIException(_(
                'column {0} does not contain a unique key.').format(right_on))

        merge_info = {
            'how_merge': how,
            'dst_selected_key': left_on,
            'src_selected_key': right_on,
            'initial_column_names': list(src_df.columns),
            'rename_column_names': list(src_df.columns),
            'columns_to_upload': [True] * len(list(src_df.columns)),
        }

        # Ready to perform the MERGE
        try:
            pandas.perform_dataframe_upload_merge(
                workflow,
                dst_df,
                src_df,
                merge_info)
        except Exception as exc:
            raise APIException(
                _('Unable to perform merge operation: {0}').format(str(exc)))

        # Merge went through.
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TableJSONMerge(TableBasicMerge):
    """Basic methods to perform JSON merge.

    get:
    Retrieves the data frame attached to the workflow and returns it labeled
    as "data_frame"

    post:
    Request to merge a given data frame with the one attached to the workflow.
    """

    serializer_class = serializers.DataFrameJSONMergeSerializer


class TablePandasMerge(TableBasicMerge):
    """API to merge using a pandas data structure.

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

    out_file = StringIO()
    pandas.to_pickle(data_frame, out_file)
    result = base64.b64encode(out_file.getvalue())
    </pre>

    </li>
    <li>From base64 encoded string to pandas dataframe

    <pre>
    import StringIO
    import base64
    import pandas

    output = StringIO()
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
    serializer_class = serializers.DataFramePandasMergeSerializer
