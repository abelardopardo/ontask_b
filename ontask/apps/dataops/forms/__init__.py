# -*- coding: utf-8 -*-

"""Package with forms to perform uploads, plugig execution."""

from ontask.apps.dataops.forms.dataframeupload import load_df_from_sqlconnection
from ontask.apps.dataops.forms.plugin import PluginInfoForm
from ontask.apps.dataops.forms.row import RowForm
from ontask.apps.dataops.forms.select import SelectColumnUploadForm, SelectKeysForm
from ontask.apps.dataops.forms.upload import (
    FIELD_PREFIX, SQLConnectionForm, SQLRequestPassword, UploadCSVFileForm,
    UploadExcelFileForm, UploadGoogleSheetForm, UploadS3FileForm,
)
