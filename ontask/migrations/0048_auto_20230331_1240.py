# Generated by Django 2.2.24 on 2023-03-31 02:10

from django.db import migrations, models
import django.db.models.deletion


def move_filter_reference(apps, schema_editor):
    """Move filter reference from filter_new to filter."""

    Action = apps.get_model('ontask', 'Action')
    for aitem in Action.objects.all():
        if aitem.filter_new:
            aitem.filter = aitem.filter_new
            aitem.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0047_remove_filter_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='filter',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action', to='ontask.Filter'),
        ),
        migrations.RunPython(code=move_filter_reference),
        migrations.RemoveField(
            model_name='action',
            name='filter_new',
        ),
    ]
