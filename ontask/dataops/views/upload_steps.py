"""Views for steps 2 - 4 of the upload process."""
from builtins import range, zip
from typing import Optional

from django import http
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models, OnTaskException
from ontask.core import (
    UserIsInstructor, WorkflowView, session_ops)
from ontask.dataops import forms, services, pandas


class UploadShowSourcesView(
    UserIsInstructor,
    WorkflowView,
    generic.TemplateView
):
    """Show the table of options for upload/merge operation."""

    template_name = 'dataops/uploadmerge.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'sql_enabled': models.SQLConnection.objects.filter(
                enabled=True).exists(),
            'athena_enabled': models.AthenaConnection.objects.filter(
                enabled=True).exists(),
            'canvas_enabled': settings.CANVAS_INFO_DICT})
        return context

    def get(self, request, *args, **kwargs):
        # Remove the upload_data payload from the session
        session_ops.flush_payload(request)
        return super().get(request, *args, **kwargs)


class UploadStepOneView(UserIsInstructor, WorkflowView, generic.FormView):
    """Start the upload of a data frame from a CSV file.

    The four-step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set)

    STEP 1:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step
    """
    data_type = None
    data_type_select = None
    prev_step_url = 'dataops:uploadmerge'

    # To be overwritten by the subclasses
    step_1_url = None
    log_upload = None

    # Store data frame and its information after uploading it
    data_frame = None
    frame_info = None

    def validate_data_frame(self) -> dict:
        """Check that the dataframe can be properly stored.

        :return: Dictionary with frame information for further processing
        """

        # Verify the data frame
        pandas.verify_data_frame(self.data_frame)

        # Store the data frame in the DB and return
        # frame info with three lists: names, types and is_key
        return pandas.store_temporary_dataframe(
            self.data_frame,
            self.workflow)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'data_type': self.data_type,
            'data_type_select': self.data_type_select,
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'prev_step': reverse(self.prev_step_url)})
        return context

    def get(self, request, *args, **kwargs):
        """Remove payload  from session dictionary and get the page."""
        session_ops.flush_payload(request)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Check that the data frame is ready for further processing.
        try:
            frame_info = self.validate_data_frame()
        except Exception as exc:
            messages.error(
                self.request,
                _('Unable to obtain data: {0}').format(str(exc)))
            return redirect('dataops:uploadmerge')

        # Dictionary to populate gradually throughout the sequence of steps.
        # It is stored in the session.
        session_ops.set_payload(
            self.request,
            {
                'initial_column_names': frame_info[0],
                'column_types': frame_info[1],
                'src_is_key_column': frame_info[2],
                'step_1': reverse(self.step_1_url),
                'log_upload': self.log_upload})

        return redirect('dataops:upload_s2')


class UploadStepBasicView(UserIsInstructor, WorkflowView):
    """Base class for the Upload Step Views."""

    upload_data = None

    def request_is_valid(self) -> Optional[http.HttpResponse]:
        """Verify some requirements for the incoming request.

        If the expected data is not there, return an HTTP response. If
        everything is correct, return None.
        """
        # Get the dictionary to store information about the upload
        # is stored in the session.
        self.upload_data = session_ops.get_payload(self.request)
        if not self.upload_data:
            # If there is no object, or it is an empty dict, it denotes a
            # direct jump to this step, get back to the home page
            return redirect('home')

        # Everything is in order, no redirect required
        return None

    def dispatch(self, request, *args, **kwargs):
        if error_response := self.request_is_valid():
            return error_response

        return super().dispatch(request, *args, **kwargs)


class UploadStepTwoView(UploadStepBasicView, generic.FormView):
    """Second step of the upload process.

    The four-step process will populate the following dictionary with name
    upload_data (divided by steps in which they are set)

    ASSUMES:

    initial_columns: List of columns in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    CREATES:

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    keep_key_column: Boolean list with those key columns that need to be kept.
    """

    form_class = forms.SelectColumnUploadForm
    template_name = 'dataops/upload_s2.html'

    initial_columns = None
    src_is_key_column = None
    column_types = None

    def request_is_valid(self) -> Optional[http.HttpResponse]:
        """Verify some requirements for the incoming request.

        If the expected data is not there, return an HTTP response. If
        everything is correct, return None.
        """
        if error_response := super().request_is_valid():
            return error_response

        # Get the column names, types, and those that are unique from the data
        # frame
        try:
            self.initial_columns = self.upload_data.get('initial_column_names')
            self.column_types = self.upload_data.get('column_types')
            self.src_is_key_column = self.upload_data.get('src_is_key_column')
        except KeyError:
            # The page has been invoked out of order
            return redirect(self.upload_data.get(
                'step_1',
                reverse('dataops:uploadmerge')))

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        # Get a hold of the fields to create a list to be processed in the page
        load_fields = [
            ffield for ffield in form if ffield.name.startswith('upload_')]
        newname_fields = [
            ffield for ffield in form if ffield.name.startswith('new_name_')]
        src_key_fields = [
            form['make_key_%s' % idx] if self.src_is_key_column[idx] else None
            for idx in range(len(self.src_is_key_column))
        ]

        # Create one of the context elements for the form. Pack the lists so
        # that they can be iterated in the template
        df_info = [list(info_item) for info_item in zip(
            load_fields,
            self.initial_columns,
            newname_fields,
            self.column_types,
            src_key_fields)]
        context.update({
            'prev_step': self.upload_data['step_1'],
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'df_info': df_info,
            'next_name':
                _('Finish') if not self.workflow.has_data_frame else None})

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create the list with the renamed column names
        rename_column_names = self.upload_data.get('rename_column_names')
        if rename_column_names is None:
            rename_column_names = self.initial_columns[:]
            self.upload_data['rename_column_names'] = rename_column_names
        kwargs['column_names'] = rename_column_names

        # Get or create list of booleans identifying columns to be uploaded
        columns_to_upload = self.upload_data.get('columns_to_upload')
        if columns_to_upload is None:
            columns_to_upload = [True] * len(self.initial_columns)
            self.upload_data['columns_to_upload'] = columns_to_upload
        kwargs['columns_to_upload'] = columns_to_upload

        # Get or create list of booleans identifying key columns to be kept
        keep_key_column = self.upload_data.get('keep_key_column')
        if keep_key_column is None:
            keep_key_column = self.upload_data['src_is_key_column'][:]
            self.upload_data['keep_key_column'] = keep_key_column
        kwargs['keep_key'] = keep_key_column
        kwargs['is_key'] = self.src_is_key_column

        return kwargs

    def form_valid(self, form):
        try:
            return services.upload_step_two(
                self.request,
                self.workflow,
                form.cleaned_data,
                self.upload_data)
        except Exception as exc:
            # Something went wrong. Flag it and reload
            messages.error(
                self.request,
                _('Unable to upload the data: {0}').format(str(exc)),
            )
            return redirect('dataops:uploadmerge')


class UploadStepThreeView(UploadStepBasicView, generic.FormView):
    """Step 3: This is already a merge operation (not an upload).

    The columns to merge have been selected and renamed. The data frame to
    merge is called src.

    In this step the user selects the unique keys to perform the merge,
    the join method, and what to do with the columns that overlap (rename or
    override)

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    CREATES:

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Key column name selected in DST

    src_selected_key: Key column name selected in SRC

    how_merge: How to merge. One of {left, right, outer, inner}
    """

    form_class = forms.SelectKeysForm
    template_name = 'dataops/upload_s3.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'prev_step': reverse('dataops:upload_s2'),
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3))})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get column names in dst_df
        dst_column_names = self.upload_data.get('dst_column_names')
        if not dst_column_names:
            dst_column_names = self.workflow.get_column_names()
            self.upload_data['dst_column_names'] = dst_column_names

        # Array of booleans saying which columns are unique in the dst DF.
        dst_is_unique_column = self.upload_data.get('dst_is_unique_column')
        if dst_is_unique_column is None:
            dst_is_unique_column = self.workflow.get_column_unique()
            self.upload_data['dst_is_unique_column'] = dst_is_unique_column

        # Array of unique col names in DST
        dst_unique_col_names = self.upload_data.get('dst_unique_col_names')
        if dst_unique_col_names is None:
            dst_unique_col_names = [
                cname for idx, cname in enumerate(dst_column_names)
                if dst_is_unique_column[idx]]
            self.upload_data['dst_unique_col_names'] = dst_unique_col_names
        kwargs['dst_keys'] = dst_unique_col_names

        # Get the names of the unique columns to upload in the source DF
        columns_to_upload = self.upload_data['columns_to_upload']
        src_column_names = self.upload_data['rename_column_names']
        src_is_key_column = self.upload_data['src_is_key_column']
        src_unique_col_names = [
            cname for idx, cname in enumerate(src_column_names)
            if src_is_key_column[idx] and columns_to_upload[idx]]
        kwargs['src_keys'] = src_unique_col_names

        kwargs['src_selected_key'] = self.upload_data.get('src_selected_key')
        kwargs['dst_selected_key'] = self.upload_data.get('dst_selected_key')
        kwargs['how_merge'] = self.upload_data.get('how_merge')

        return kwargs

    def form_valid(self, form):
        # Get the keys and merge method and store them in the session dict
        self.upload_data['dst_selected_key'] = form.cleaned_data['dst_key']
        self.upload_data['src_selected_key'] = form.cleaned_data['src_key']
        self.upload_data['how_merge'] = form.cleaned_data['how_merge']

        return redirect('dataops:upload_s4')


class UploadStepFourView(UploadStepBasicView, generic.TemplateView):
    """Step 4: Show the user the expected effect of the merge and perform it.

    ASSUMES:

    initial_column_names: List of column names in the initial file.

    column_types: List of column types as detected by pandas

    src_is_key_column: Boolean list with src columns that are unique

    step_1: URL name of the first step

    rename_column_names: Modified column names to remove ambiguity when
                          merging.

    columns_to_upload: Boolean list denoting the columns in SRC that are
                       marked for upload.

    dst_column_names: List of column names in destination frame

    dst_is_unique_column: Boolean list with dst columns that are unique

    dst_unique_col_names: List with the column names that are unique

    dst_selected_key: Key column name selected in DST

    src_selected_key: Key column name selected in SRC

    how_merge: How to merge. One of {left, right, outer, inner}
    """

    template_name = 'dataops/upload_s4.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'prev_step': reverse('dataops:upload_s3'),
            'value_range': (
                range(5) if self.workflow.has_data_frame else range(3)),
            'next_name': _('Finish'),
            'info': services.upload_prepare_step_four(self.upload_data)})
        return context

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        return services.upload_step_four(
            request,
            self.workflow,
            self.upload_data)
