# Generated by Django 2.2.8 on 2019-12-08 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0007_set_workflow_in_scheduled_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledoperation',
            name='frequency',
            field=models.CharField(blank=True, default='', max_length=1024, null=True),
        ),
    ]