# Generated by Django 4.2.7 on 2023-12-24 23:21

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0075_alter_sqlconnection_db_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthusertoken',
            name='instance_name',
            field=fernet_fields.fields.EncryptedCharField(max_length=2048),
        ),
    ]