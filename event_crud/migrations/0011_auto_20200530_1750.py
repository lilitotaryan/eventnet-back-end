# Generated by Django 2.2.5 on 2020-05-30 17:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0010_auto_20200529_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='available_places',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 30, 17, 50, 42, 838983, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 30, 17, 50, 42, 838957, tzinfo=utc)),
        ),
    ]
