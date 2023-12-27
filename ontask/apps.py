"""File defining the class with configuration operation"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OnTaskConfig(AppConfig):
    """Define app configuration."""
    name = 'ontask'
    verbose_name = _('OnTask')

    def ready(self) -> None:
        """Register the signals."""
        # Needed so that the signal registration is done
        # noinspection PyUnresolvedReferences
        from ontask import signals  # noqa: F401

        # Initialize the required factories
        from ontask.tasks import initialize_task_factory
        initialize_task_factory()

        from ontask.action import initialize_action_factory
        initialize_action_factory()

        from ontask.scheduler import initialize_schedule_factory
        initialize_schedule_factory()
