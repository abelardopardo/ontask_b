# Generated by Django 2.2.5 on 2019-09-11 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0022_auto_20190911_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rubriccell',
            name='description_text',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='rubriccell',
            name='feedback_text',
            field=models.TextField(blank=True, default='', verbose_name='feedback'),
        ),
    ]
