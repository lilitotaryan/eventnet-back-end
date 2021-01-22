# Generated by Django 2.2.5 on 2020-06-06 19:11

import datetime
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('event_crud', '0017_auto_20200606_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 6, 19, 11, 29, 714746, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 6, 19, 11, 29, 714723, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='event',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='cohosts', to=settings.AUTH_USER_MODEL),
        ),
    ]
