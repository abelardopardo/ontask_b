# Generated by Django 2.2.5 on 2019-10-02 01:11

from django.db import migrations, models
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0037_auto_20191002_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athenaconnection',
            name='aws_secret_access_key',
            field=fernet_fields.fields.EncryptedCharField(blank=True, default='', max_length=512, null=True, verbose_name='AWS secret access key'),
        ),
        migrations.AlterField(
            model_name='sqlconnection',
            name='db_name',
            field=models.CharField(default='', max_length=2048, verbose_name='Database name'),
        ),
        migrations.AlterField(
            model_name='sqlconnection',
            name='db_password',
            field=fernet_fields.fields.EncryptedCharField(blank=True, default=False, max_length=2048, null=True, verbose_name='Password (leave empty to enter at execution)'),
        ),
        migrations.AlterField(
            model_name='sqlconnection',
            name='db_table',
            field=models.CharField(blank=True, default='', max_length=2048, null=True, verbose_name='Database table'),
        ),
    ]
