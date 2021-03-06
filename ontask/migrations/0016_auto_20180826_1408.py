# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-26 04:38
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0023_auto_20180722_1013'),
        ('ontask', '0015_scheduledemailaction_exclude_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledemailaction',
            name='item_column',
            field=models.ForeignKey(blank=True, db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_actions', to='ontask.Column', verbose_name='Column to select the elements for the action'),
        ),
        migrations.AlterField(
            model_name='scheduledemailaction',
            name='email_column',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_email_actions', to='ontask.Column', verbose_name='Column to select the elements for the action'),
        ),
    ]
