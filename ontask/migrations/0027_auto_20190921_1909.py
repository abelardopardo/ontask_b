# Generated by Django 2.2.5 on 2019-09-21 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0026_auto_20190921_1853'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rubriccell',
            options={'ordering': ['column__position', 'loa_position']},
        ),
    ]