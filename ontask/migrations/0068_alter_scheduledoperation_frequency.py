# Generated by Django 4.2 on 2023-04-18 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0067_alter_action_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledoperation',
            name='frequency',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]
