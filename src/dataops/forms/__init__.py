# -*- coding: utf-8 -*-

"""Package with forms to perform uploads, plugig execution."""

from dataops.forms.plugin import PluginInfoForm
from dataops.forms.row import RowForm
from dataops.forms.select import SelectColumnUploadForm, SelectKeysForm
from dataops.forms.upload import (
    FIELD_PREFIX, SQLConnectionForm, SQLRequestPassword, UploadCSVFileForm,
    UploadExcelFileForm, UploadGoogleSheetForm, UploadS3FileForm,
)
from dataops.forms.dataframeupload import load_df_from_sqlconnection
