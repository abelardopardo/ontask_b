# Generated by Django 2.1.7 on 2019-02-28 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0050_auto_20190228_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actioncolumnconditiontuple',
            name='action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns_condition_pair', to='action.Action'),
        ),
    ]