# Generated by Django 2.2.8 on 2019-12-07 10:37

from django.db import migrations


def set_workflow_field(apps, schema_editor):
    """Set the workflow field for every scheduled operation if needed."""
    ScheduledOperation = apps.get_model('ontask', 'ScheduledOperation')
    for sitem in ScheduledOperation.objects.all():
        if sitem.workflow:
            continue

        if not sitem.action:
            raise Exception('Unable to set workflow in ScheduledOperation')

        sitem.workflow = sitem.action.workflow
        sitem.save()


def reverse_migration(apps, schema_editor):
    del apps, schema_editor


class Migration(migrations.Migration):

    dependencies = [('ontask', '0006_auto_20191207_1330')]

    operations = [
        migrations.RunPython(
            code=set_workflow_field,
            reverse_code=reverse_migration)]
