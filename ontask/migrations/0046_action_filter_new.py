# Generated by Django 2.2.24 on 2023-03-31 02:06

from django.db import migrations, models
import django.db.models.deletion


def move_filter_reference(apps, schema_editor):
    """Move filter reference from filter to action field.

    :param apps:
    :param schema_editor:
    :return:
    """
    if schema_editor.connection.alias != 'default':
        return

    Filter = apps.get_model('ontask', 'Filter')
    for f_obj in Filter.objects.all():
        if f_obj.action is None:
            continue

        f_obj.action.filter_new = f_obj
        f_obj.action.save()

class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0045_remove_view__formula'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='filter_new',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_new', to='ontask.Filter'),
        ),
	migrations.RunPython(code=move_filter_reference),
    ]
