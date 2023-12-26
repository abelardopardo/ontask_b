"""Initialise the action edit and run factories."""
from ontask.action.services import ActionEditFactory
from ontask.action.services.run_factory import ActionRunFactory

ACTION_EDIT_FACTORY = ActionEditFactory()

ACTION_RUN_FACTORY = ActionRunFactory()


def initialize_action_factory():
    from ontask.models.action import Action, ZIP_OPERATION
    from ontask.action import forms, services

    # Catalogue of action processing blocks. Tuples contain:
    # - Action type: Field in Action Model
    # - Function for the EDIT view
    # - Function for the RUN request view
    # - Class for the batch execution
    action_catalogue = [
        # PERSONALIZED TEXT
        (
            Action.PERSONALIZED_TEXT,
            services.ActionEditProducerEmail.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_out.html'),
            services.ActionRunProducerEmail.as_view(
                form_class=forms.EmailActionRunForm,
                template_name='action/request_email_data.html'),
            services.ActionRunProducerEmail),

        # EMAIL REPORT
        (
            Action.EMAIL_REPORT,
            services.ActionEditProducerEmailReport.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_out.html'),
            services.ActionRunProducerEmailReport.as_view(
                form_class=forms.SendListActionRunForm,
                template_name='action/request_email_report_data.html'),
            services.ActionRunProducerEmailReport),
        (
            Action.RUBRIC_TEXT,
            services.ActionEditProducerRubric.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_rubric.html'),
            services.ActionRunProducerEmail.as_view(
                form_class=forms.EmailActionRunForm,
                template_name='action/request_email_data.html'),
            services.ActionRunProducerEmail),

        # PERSONALIZED JSON
        (
            Action.PERSONALIZED_JSON,
            services.ActionOutEditProducerBase.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_out.html'),
            services.ActionRunProducerJSON.as_view(
                form_class=forms.JSONActionRunForm,
                template_name='action/request_json_data.html'),
            services.ActionRunProducerJSON),

        # JSON REPORT
        (
            Action.JSON_REPORT,
            services.ActionOutEditProducerBase.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_out.html'),
            services.ActionRunProducerJSONReport.as_view(
                form_class=forms.JSONReportActionRunForm,
                template_name='action/request_json_report_data.html'),
            services.ActionRunProducerJSONReport),

        # CANVAS PERSONALIZED EMAIL
        (
            Action.PERSONALIZED_CANVAS_EMAIL,
            services.ActionEditProducerCanvasEmail.as_view(
                form_class=forms.EditActionOutForm,
                template_name='action/edit_out.html'),
            services.ActionRunProducerCanvasEmail.as_view(
                form_class=forms.CanvasEmailActionRunForm,
                template_name='action/request_canvas_email_data.html'),
            services.ActionRunProducerCanvasEmail),

        # ZIP action
        (
            ZIP_OPERATION,
            None,
            services.ActionRunProducerZip.as_view(
                form_class=forms.ZipActionRunForm,
                template_name='action/action_zip_step1.html'),
            services.ActionRunProducerZip),

        # SURVEY
        (
            Action.SURVEY,
            services.ActionEditProducerSurvey.as_view(
                template_name='action/edit_in.html'),
            services.ActionRunProducerSurvey.as_view(
                template_name='action/run_survey.html'),
            None),

        # TODO_LIST action
        (
            Action.TODO_LIST,
            services.ActionEditProducerSurvey.as_view(
                template_name='action/edit_in.html'),
            services.ActionRunProducerTODO.as_view(
                template_name='action/run_survey.html'),
            None),
    ]

    for op_type, edit_view, run_view, run_cls in action_catalogue:
        ACTION_EDIT_FACTORY.register_producer(
            op_type,
            edit_view)

        ACTION_RUN_FACTORY.register_producer(
            op_type,
            (run_view, run_cls))
