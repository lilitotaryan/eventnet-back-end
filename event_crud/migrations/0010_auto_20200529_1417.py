# Generated by Django 2.2.5 on 2020-05-29 14:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0009_auto_20200529_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 29, 14, 17, 3, 147033, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 29, 14, 17, 3, 147011, tzinfo=utc)),
        ),
    ]
