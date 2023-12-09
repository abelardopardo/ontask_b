"""Package with forms to perform uploads, plugig execution."""
from ontask.dataops.forms.plugin import PluginInfoForm
from ontask.dataops.forms.row import RowForm
from ontask.dataops.forms.select import (
    MergeForm, SelectColumnUploadForm, SelectKeysForm,
)
from ontask.dataops.forms.upload import (
    UploadCSVFileForm, UploadExcelFileForm, UploadGoogleSheetForm,
    UploadS3FileForm, UploadCanvasCourseStudentForm)
