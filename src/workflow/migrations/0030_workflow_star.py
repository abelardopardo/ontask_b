# Generated by Django 2.2.2 on 2019-06-09 03:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workflow', '0029_auto_20190524_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='star',
            field=models.ManyToManyField(related_name='workflows_star', to=settings.AUTH_USER_MODEL),
        ),
    ]
