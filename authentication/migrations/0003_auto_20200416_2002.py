# Generated by Django 2.2.5 on 2020-04-16 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_session_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='device_brand',
            field=models.CharField(blank=True, default=None, max_length=200),
        ),
    ]
