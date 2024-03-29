# Generated by Django 2.2.8 on 2019-12-21 23:01

from django.db import migrations


from ontask.core import fix_non_unique_object_names


def fix_non_unique_scheduleop_names(apps, schema_editor):
    """Disambiguate schedule ops with identical names within a workflow."""

    Workflow = apps.get_model('ontask', 'Action')
    for workflow in Workflow.objects.all():
        # Loop over the workflows to make the schedule ops unique

        # Get the schedule ops names and those with duplicate names
        sch_op_names = set()
        dupes = [
            sch_op for sch_op in workflow.scheduled_operations.all()
            if sch_op.name in sch_op_names or sch_op_names.add(sch_op.name)]

        if not dupes:
            # No duplicates, nothing to do here
            continue

        fix_non_unique_object_names(sch_op_names, dupes)


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0021_auto_20191221_1852'),
    ]

    operations = [
        migrations.RunPython(code=fix_non_unique_scheduleop_names),
        migrations.AlterUniqueTogether(
            name='scheduledoperation',
            unique_together={('name', 'workflow')},
        ),
    ]
