# Generated by Django 2.2.24 on 2023-03-31 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0044_auto_20230331_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='view',
            name='_formula',
        ),
    ]
