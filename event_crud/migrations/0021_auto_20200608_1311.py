# Generated by Django 2.2.5 on 2020-06-08 13:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0020_auto_20200607_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 8, 13, 11, 2, 220020, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 8, 13, 11, 2, 219995, tzinfo=utc)),
        ),
    ]