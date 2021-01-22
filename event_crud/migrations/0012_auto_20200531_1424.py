# Generated by Django 2.2.5 on 2020-05-31 14:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0011_auto_20200530_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 31, 14, 24, 23, 989513, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 31, 14, 24, 23, 989474, tzinfo=utc)),
        ),
    ]