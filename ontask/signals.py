"""Intercept signals when manipulating some objects."""

from django.conf import settings
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _

from ontask import LOGGER, models
from ontask.dataops import sql
from ontask.scheduler import services


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_ontaskuser_handler(sender, **kwargs):
    """Create the user extensions whenever a new user is created."""
    del sender
    created = kwargs.get('created', True)
    instance = kwargs.get('instance')
    if not created or not instance:
        return

    # Create the profile and ontask user objects, only if it is newly created
    ontask_user = models.OnTaskUser(user=instance)
    ontask_user.save()
    profile = models.Profile(user=instance)
    profile.save()
    LOGGER.info(_('New ontask user profile for %s created'), str(instance))


@receiver(pre_delete, sender=models.Workflow)
def delete_data_frame_table(sender, **kwargs):
    """Delete the data table when deleting the workflow."""
    del sender
    instance = kwargs.get('instance')
    if not instance:
        return

    if instance.has_data_frame:
        sql.delete_table(instance.get_data_frame_table_name())


@receiver(pre_save, sender=models.Condition)
@receiver(pre_save, sender=models.Filter)
def update_fields(sender, **kwargs):
    """Update various fields after saving conditions and filter."""
    del sender
    instance = kwargs.get('instance')
    if not instance:
        return

    instance.update_fields()


@receiver(post_save, sender=models.ScheduledOperation)
def create_scheduled_task(sender, **kwargs):
    """Create the task in django_celery_beat for every scheduled operation."""
    del sender
    instance = kwargs.get('instance')
    if not instance or not instance.status == models.scheduler.STATUS_PENDING:
        return
    services.schedule_task(instance)


@receiver(pre_delete, sender=models.ScheduledOperation)
def delete_scheduled_task(sender, **kwargs):
    """Delete the task attached to a Scheduled Operation."""
    del sender
    instance = kwargs.get('instance')
    if not instance:
        return

    instance.delete_task()
